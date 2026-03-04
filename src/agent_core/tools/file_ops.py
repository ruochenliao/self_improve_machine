"""File system operation tools with path safety restrictions."""

from __future__ import annotations

import re
from pathlib import Path

import structlog

from .registry import ToolResult, tool

logger = structlog.get_logger()

# Project root is determined at module level
_PROJECT_ROOT: Path | None = None


def set_project_root(root: Path) -> None:
    global _PROJECT_ROOT
    _PROJECT_ROOT = root


def _resolve_safe_path(path_str: str) -> Path | None:
    """Resolve path and ensure it's within the project root."""
    path = Path(path_str).resolve()
    if _PROJECT_ROOT and not str(path).startswith(str(_PROJECT_ROOT.resolve())):
        return None
    return path


@tool(
    name="read_file",
    description="Read the contents of a file.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read",
            },
        },
        "required": ["file_path"],
    },
)
async def read_file(file_path: str) -> ToolResult:
    path = _resolve_safe_path(file_path)
    if path is None:
        return ToolResult(success=False, error="Path outside project directory")
    if not path.exists():
        return ToolResult(success=False, error=f"File not found: {path}")
    if not path.is_file():
        return ToolResult(success=False, error=f"Not a file: {path}")

    try:
        content = path.read_text(encoding="utf-8")
        return ToolResult(success=True, output=content)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="write_file",
    description="Write content to a file, creating parent directories if needed.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to write to"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["file_path", "content"],
    },
)
async def write_file(file_path: str, content: str) -> ToolResult:
    path = _resolve_safe_path(file_path)
    if path is None:
        return ToolResult(success=False, error="Path outside project directory")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return ToolResult(success=True, output=f"Written {len(content)} bytes to {path}")
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="list_directory",
    description="List contents of a directory.",
    parameters={
        "type": "object",
        "properties": {
            "dir_path": {"type": "string", "description": "Directory path to list"},
            "recursive": {"type": "boolean", "description": "List recursively (default: false)"},
        },
        "required": ["dir_path"],
    },
)
async def list_directory(dir_path: str, recursive: bool = False) -> ToolResult:
    path = _resolve_safe_path(dir_path)
    if path is None:
        return ToolResult(success=False, error="Path outside project directory")
    if not path.is_dir():
        return ToolResult(success=False, error=f"Not a directory: {path}")

    try:
        if recursive:
            entries = sorted(str(p.relative_to(path)) for p in path.rglob("*") if not any(part.startswith(".") for part in p.parts))
        else:
            entries = sorted(p.name + ("/" if p.is_dir() else "") for p in path.iterdir() if not p.name.startswith("."))

        return ToolResult(success=True, output="\n".join(entries))
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="search_in_files",
    description="Search for a pattern across files in a directory.",
    parameters={
        "type": "object",
        "properties": {
            "dir_path": {"type": "string", "description": "Directory to search in"},
            "pattern": {"type": "string", "description": "Regex pattern to search for"},
            "file_glob": {"type": "string", "description": "File glob pattern (e.g., '*.py')"},
        },
        "required": ["dir_path", "pattern"],
    },
)
async def search_in_files(dir_path: str, pattern: str, file_glob: str = "*") -> ToolResult:
    path = _resolve_safe_path(dir_path)
    if path is None:
        return ToolResult(success=False, error="Path outside project directory")
    if not path.is_dir():
        return ToolResult(success=False, error=f"Not a directory: {path}")

    try:
        regex = re.compile(pattern)
        matches: list[str] = []

        for file_path in path.rglob(file_glob):
            if not file_path.is_file():
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    if regex.search(line):
                        rel = file_path.relative_to(path)
                        matches.append(f"{rel}:{i}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                continue

            if len(matches) >= 100:
                matches.append("... (truncated at 100 matches)")
                break

        return ToolResult(
            success=True,
            output="\n".join(matches) if matches else "No matches found",
            data={"match_count": len(matches)},
        )
    except re.error as e:
        return ToolResult(success=False, error=f"Invalid regex: {e}")
    except Exception as e:
        return ToolResult(success=False, error=str(e))
