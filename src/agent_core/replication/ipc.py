"""IPC (Inter-Process Communication) bridge for parent-child agent communication.

Uses Unix Domain Sockets with a JSON-line protocol for bidirectional messaging
between parent and child agent processes.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine

import structlog

logger = structlog.get_logger()


@dataclass
class IPCMessage:
    """A message exchanged between parent and child agents."""
    msg_type: str  # "heartbeat" | "status" | "command" | "response" | "shutdown"
    payload: dict[str, Any] = field(default_factory=dict)
    sender_id: str = ""
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: float = field(default_factory=time.time)

    def serialize(self) -> bytes:
        """Serialize message to JSON line bytes."""
        data = {
            "type": self.msg_type,
            "payload": self.payload,
            "sender_id": self.sender_id,
            "msg_id": self.msg_id,
            "timestamp": self.timestamp,
        }
        return (json.dumps(data, default=str) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes) -> IPCMessage:
        """Deserialize a JSON line into an IPCMessage."""
        d = json.loads(data.decode("utf-8").strip())
        return cls(
            msg_type=d.get("type", "unknown"),
            payload=d.get("payload", {}),
            sender_id=d.get("sender_id", ""),
            msg_id=d.get("msg_id", ""),
            timestamp=d.get("timestamp", 0.0),
        )


MessageHandler = Callable[[IPCMessage], Coroutine[Any, Any, IPCMessage | None]]


class IPCBridge:
    """Unix Domain Socket based IPC for agent communication.

    Can operate in two modes:
    - Server mode (parent): Listens on a socket, accepts connections from children.
    - Client mode (child): Connects to parent's socket.
    """

    def __init__(
        self,
        agent_id: str,
        socket_dir: Path | str = "/tmp/sim_ipc",
    ):
        self.agent_id = agent_id
        self.socket_dir = Path(socket_dir)
        self.socket_dir.mkdir(parents=True, exist_ok=True)
        self.socket_path = self.socket_dir / f"agent_{agent_id}.sock"

        self._server: asyncio.AbstractServer | None = None
        self._handlers: dict[str, MessageHandler] = {}
        self._connections: dict[str, asyncio.StreamWriter] = {}
        self._running = False
        self._pending_responses: dict[str, asyncio.Future] = {}

    def on_message(self, msg_type: str, handler: MessageHandler) -> None:
        """Register a handler for a specific message type."""
        self._handlers[msg_type] = handler

    async def start_server(self) -> None:
        """Start listening as a server (parent mode)."""
        # Remove stale socket file
        if self.socket_path.exists():
            self.socket_path.unlink()

        self._server = await asyncio.start_unix_server(
            self._handle_client_connection,
            path=str(self.socket_path),
        )
        self._running = True
        logger.info("ipc.server_started", path=str(self.socket_path))

    async def _handle_client_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle an incoming client connection."""
        peer_id = "unknown"
        try:
            while self._running:
                line = await asyncio.wait_for(reader.readline(), timeout=120)
                if not line:
                    break

                msg = IPCMessage.deserialize(line)
                peer_id = msg.sender_id

                # Track the connection by sender ID
                self._connections[peer_id] = writer

                # Check if this is a response to a pending request
                if msg.msg_type == "response" and msg.msg_id in self._pending_responses:
                    self._pending_responses[msg.msg_id].set_result(msg)
                    continue

                # Dispatch to registered handler
                handler = self._handlers.get(msg.msg_type)
                if handler:
                    response = await handler(msg)
                    if response:
                        response.sender_id = self.agent_id
                        writer.write(response.serialize())
                        await writer.drain()
                else:
                    logger.debug("ipc.unhandled_message", type=msg.msg_type)
        except asyncio.TimeoutError:
            logger.debug("ipc.client_timeout", peer=peer_id)
        except ConnectionResetError:
            logger.debug("ipc.client_disconnected", peer=peer_id)
        except Exception as e:
            logger.error("ipc.client_error", error=str(e), peer=peer_id)
        finally:
            self._connections.pop(peer_id, None)
            writer.close()

    async def connect_to_parent(self, parent_id: str) -> bool:
        """Connect to a parent agent's socket (child mode)."""
        parent_socket = self.socket_dir / f"agent_{parent_id}.sock"
        if not parent_socket.exists():
            logger.warning("ipc.parent_socket_not_found", parent=parent_id)
            return False

        try:
            reader, writer = await asyncio.open_unix_connection(str(parent_socket))
            self._connections[parent_id] = writer
            self._running = True

            # Start background reader
            asyncio.create_task(self._read_from_parent(reader, parent_id))

            logger.info("ipc.connected_to_parent", parent=parent_id)
            return True
        except Exception as e:
            logger.error("ipc.connect_failed", parent=parent_id, error=str(e))
            return False

    async def _read_from_parent(
        self,
        reader: asyncio.StreamReader,
        parent_id: str,
    ) -> None:
        """Read messages from parent in background."""
        try:
            while self._running:
                line = await asyncio.wait_for(reader.readline(), timeout=120)
                if not line:
                    break

                msg = IPCMessage.deserialize(line)

                if msg.msg_type == "response" and msg.msg_id in self._pending_responses:
                    self._pending_responses[msg.msg_id].set_result(msg)
                    continue

                handler = self._handlers.get(msg.msg_type)
                if handler:
                    response = await handler(msg)
                    if response and parent_id in self._connections:
                        response.sender_id = self.agent_id
                        self._connections[parent_id].write(response.serialize())
                        await self._connections[parent_id].drain()
        except asyncio.TimeoutError:
            logger.debug("ipc.parent_timeout")
        except Exception as e:
            logger.error("ipc.parent_read_error", error=str(e))

    async def send(self, target_id: str, message: IPCMessage) -> bool:
        """Send a message to a specific agent."""
        writer = self._connections.get(target_id)
        if not writer:
            logger.warning("ipc.target_not_connected", target=target_id)
            return False

        try:
            message.sender_id = self.agent_id
            writer.write(message.serialize())
            await writer.drain()
            return True
        except Exception as e:
            logger.error("ipc.send_failed", target=target_id, error=str(e))
            self._connections.pop(target_id, None)
            return False

    async def request(
        self, target_id: str, message: IPCMessage, timeout: float = 30.0
    ) -> IPCMessage | None:
        """Send a message and wait for a response."""
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_responses[message.msg_id] = future

        sent = await self.send(target_id, message)
        if not sent:
            self._pending_responses.pop(message.msg_id, None)
            return None

        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.warning("ipc.request_timeout", target=target_id, msg_id=message.msg_id)
            return None
        finally:
            self._pending_responses.pop(message.msg_id, None)

    async def broadcast(self, message: IPCMessage) -> int:
        """Broadcast a message to all connected agents."""
        sent_count = 0
        disconnected = []

        for target_id, writer in self._connections.items():
            try:
                message.sender_id = self.agent_id
                writer.write(message.serialize())
                await writer.drain()
                sent_count += 1
            except Exception:
                disconnected.append(target_id)

        for tid in disconnected:
            self._connections.pop(tid, None)

        return sent_count

    def get_connected_peers(self) -> list[str]:
        """Get list of connected peer agent IDs."""
        return list(self._connections.keys())

    async def stop(self) -> None:
        """Shutdown the IPC bridge."""
        self._running = False

        # Close all connections
        for writer in self._connections.values():
            try:
                writer.close()
            except Exception:
                pass
        self._connections.clear()

        # Stop server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        # Clean up socket file
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass

        # Cancel pending responses
        for future in self._pending_responses.values():
            if not future.done():
                future.cancel()
        self._pending_responses.clear()

        logger.info("ipc.stopped", agent=self.agent_id)
