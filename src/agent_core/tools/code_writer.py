"""Code writing and editing tools with syntax validation."""

from __future__ import annotations

import ast
from pathlib import Path

import structlog

from .registry import ToolResult, tool

logger = structlog.get_logger()


@tool(
    name="write_code",
    description="Create or overwrite a file with the given content. For Python files, validates syntax before writing.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to create/overwrite",
            },
            "content": {
                "type": "string",
                "description": "The file content to write",
            },
        },
        "required": ["file_path", "content"],
    },
)
async def write_code(file_path: str, content: str) -> ToolResult:
    """Write content to a file, with Python syntax validation."""
    path = Path(file_path)

    # Syntax check for Python files
    if path.suffix == ".py":
        try:
            ast.parse(content)
        except SyntaxError as e:
            return ToolResult(
                success=False,
                error=f"Python syntax error at line {e.lineno}: {e.msg}",
            )

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info("code.written", path=str(path), size=len(content))
        return ToolResult(
            success=True,
            output=f"File written: {path} ({len(content)} bytes)",
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="edit_code",
    description="Edit a file by replacing content between specified line numbers.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to edit",
            },
            "start_line": {
                "type": "integer",
                "description": "Starting line number (1-based)",
            },
            "end_line": {
                "type": "integer",
                "description": "Ending line number (1-based, inclusive)",
            },
            "new_content": {
                "type": "string",
                "description": "New content to replace the specified line range",
            },
        },
        "required": ["file_path", "start_line", "end_line", "new_content"],
    },
)
async def edit_code(file_path: str, start_line: int, end_line: int, new_content: str) -> ToolResult:
    """Edit a file by replacing lines in the specified range."""
    path = Path(file_path)
    if not path.exists():
        return ToolResult(success=False, error=f"File not found: {path}")

    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        total_lines = len(lines)

        if start_line < 1 or end_line > total_lines or start_line > end_line:
            return ToolResult(
                success=False,
                error=f"Invalid line range {start_line}-{end_line} (file has {total_lines} lines)",
            )

        new_lines = new_content.splitlines(keepends=True)
        if new_content and not new_content.endswith("\n"):
            new_lines[-1] += "\n"

        result_lines = lines[:start_line - 1] + new_lines + lines[end_line:]
        new_file_content = "".join(result_lines)

        # Syntax check for Python files
        if path.suffix == ".py":
            try:
                ast.parse(new_file_content)
            except SyntaxError as e:
                return ToolResult(
                    success=False,
                    error=f"Edit would cause syntax error at line {e.lineno}: {e.msg}",
                )

        path.write_text(new_file_content, encoding="utf-8")
        return ToolResult(
            success=True,
            output=f"Edited {path}: replaced lines {start_line}-{end_line}",
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
