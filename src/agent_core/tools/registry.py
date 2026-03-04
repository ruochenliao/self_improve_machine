"""Tool registry with decorator-based registration and dynamic loading."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import structlog

logger = structlog.get_logger()


@dataclass
class ToolResult:
    success: bool
    output: str = ""
    error: str = ""
    data: Any = None


@dataclass
class ToolEntry:
    name: str
    description: str
    parameters: dict  # JSON Schema
    handler: Callable
    timeout_sec: int = 60


class ToolRegistry:
    """Singleton tool registry with @tool decorator support."""

    _instance: ToolRegistry | None = None
    _tools: dict[str, ToolEntry] = {}

    def __new__(cls) -> ToolRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(self, entry: ToolEntry) -> None:
        self._tools[entry.name] = entry
        logger.debug("tool.registered", name=entry.name)

    def get(self, name: str) -> ToolEntry | None:
        return self._tools.get(name)

    def get_tool_schemas(self) -> list[dict]:
        """Return OpenAI function calling compatible schemas for all tools."""
        schemas = []
        for entry in self._tools.values():
            schemas.append({
                "name": entry.name,
                "description": entry.description,
                "parameters": entry.parameters,
            })
        return schemas

    async def execute(self, name: str, args: dict) -> ToolResult:
        """Execute a tool by name with given arguments."""
        entry = self._tools.get(name)
        if entry is None:
            return ToolResult(success=False, error=f"Tool '{name}' not found")

        try:
            if asyncio.iscoroutinefunction(entry.handler):
                result = await asyncio.wait_for(
                    entry.handler(**args),
                    timeout=entry.timeout_sec,
                )
            else:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: entry.handler(**args)),
                    timeout=entry.timeout_sec,
                )

            if isinstance(result, ToolResult):
                return result
            return ToolResult(success=True, output=str(result))

        except asyncio.TimeoutError:
            logger.warning("tool.timeout", name=name, timeout=entry.timeout_sec)
            return ToolResult(success=False, error=f"Tool '{name}' timed out after {entry.timeout_sec}s")
        except Exception as e:
            logger.error("tool.error", name=name, error=str(e))
            return ToolResult(success=False, error=str(e))

    def load_from_directory(self, directory: str | Path) -> int:
        """Dynamically load tool modules from a directory. Returns count loaded."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            return 0

        count = 0
        for py_file in dir_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(
                    f"dynamic_tool_{py_file.stem}", py_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    count += 1
                    logger.info("tool.dynamic_loaded", file=py_file.name)
            except Exception as e:
                logger.error("tool.dynamic_load_failed", file=py_file.name, error=str(e))

        return count

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None
        cls._tools = {}


def tool(
    name: str,
    description: str,
    parameters: dict | None = None,
    timeout_sec: int = 60,
) -> Callable:
    """Decorator to register an async function as a tool.

    Usage:
        @tool(name="my_tool", description="Does something", parameters={...})
        async def my_tool(arg1: str) -> ToolResult:
            ...
    """
    def decorator(func: Callable) -> Callable:
        params = parameters or {
            "type": "object",
            "properties": {},
            "required": [],
        }
        entry = ToolEntry(
            name=name,
            description=description,
            parameters=params,
            handler=func,
            timeout_sec=timeout_sec,
        )
        ToolRegistry().register(entry)
        return func
    return decorator
