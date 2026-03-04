"""Shell execution tool with safety checks."""

from __future__ import annotations

import asyncio

import structlog

from .registry import ToolResult, tool

logger = structlog.get_logger()

_DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",
    "chmod -R 777 /",
    "shutdown",
    "reboot",
    "init 0",
    "init 6",
    "> /dev/sda",
    "wget | sh",
    "curl | sh",
]


@tool(
    name="shell_execute",
    description="Execute a shell command and return stdout/stderr. Use for running scripts, installing packages, checking system state, etc.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            },
            "working_dir": {
                "type": "string",
                "description": "Working directory for the command (optional)",
            },
        },
        "required": ["command"],
    },
    timeout_sec=60,
)
async def shell_execute(command: str, working_dir: str = "") -> ToolResult:
    """Execute a shell command with safety checks."""
    # Safety check
    cmd_lower = command.lower().strip()
    for pattern in _DANGEROUS_PATTERNS:
        if pattern in cmd_lower:
            return ToolResult(
                success=False,
                error=f"Dangerous command blocked: contains '{pattern}'",
            )

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir or None,
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        stdout_str = stdout.decode("utf-8", errors="replace")[:10240]  # 10KB limit
        stderr_str = stderr.decode("utf-8", errors="replace")[:10240]

        output = stdout_str
        if stderr_str:
            output += f"\n[stderr]\n{stderr_str}"

        return ToolResult(
            success=proc.returncode == 0,
            output=output,
            error=stderr_str if proc.returncode != 0 else "",
            data={"exit_code": proc.returncode},
        )
    except asyncio.TimeoutError:
        return ToolResult(success=False, error="Command timed out after 60s")
    except Exception as e:
        return ToolResult(success=False, error=str(e))
