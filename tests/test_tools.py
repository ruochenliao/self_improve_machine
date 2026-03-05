"""Tests for the tool registry and built-in tools."""

from __future__ import annotations

import asyncio

import pytest

from agent_core.tools.registry import ToolRegistry, ToolEntry, ToolResult, tool


class TestToolRegistry:
    """Test tool registration, discovery, and execution."""

    def test_register_and_list(self, tool_registry):
        entry = ToolEntry(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
            handler=lambda: ToolResult(success=True, output="ok"),
        )
        tool_registry.register(entry)
        assert "test_tool" in tool_registry.list_tools()

    def test_get_tool(self, tool_registry):
        entry = ToolEntry(
            name="my_tool",
            description="desc",
            parameters={"type": "object", "properties": {}},
            handler=lambda: None,
        )
        tool_registry.register(entry)
        retrieved = tool_registry.get("my_tool")
        assert retrieved is not None
        assert retrieved.name == "my_tool"

    def test_get_missing_tool(self, tool_registry):
        assert tool_registry.get("nonexistent") is None

    def test_get_tool_schemas(self, tool_registry):
        entry = ToolEntry(
            name="schema_tool",
            description="A tool with schema",
            parameters={"type": "object", "properties": {"arg1": {"type": "string"}}},
            handler=lambda arg1: None,
        )
        tool_registry.register(entry)
        schemas = tool_registry.get_tool_schemas()
        assert len(schemas) >= 1
        schema = next(s for s in schemas if s["name"] == "schema_tool")
        assert schema["description"] == "A tool with schema"
        assert "arg1" in schema["parameters"]["properties"]

    @pytest.mark.asyncio
    async def test_execute_async_tool(self, tool_registry):
        async def my_async_tool(msg: str) -> ToolResult:
            return ToolResult(success=True, output=f"hello {msg}")

        tool_registry.register(ToolEntry(
            name="async_tool",
            description="async",
            parameters={"type": "object", "properties": {"msg": {"type": "string"}}},
            handler=my_async_tool,
        ))

        result = await tool_registry.execute("async_tool", {"msg": "world"})
        assert result.success
        assert result.output == "hello world"

    @pytest.mark.asyncio
    async def test_execute_sync_tool(self, tool_registry):
        def my_sync_tool(x: str) -> ToolResult:
            return ToolResult(success=True, output=x.upper())

        tool_registry.register(ToolEntry(
            name="sync_tool",
            description="sync",
            parameters={"type": "object", "properties": {"x": {"type": "string"}}},
            handler=my_sync_tool,
        ))

        result = await tool_registry.execute("sync_tool", {"x": "test"})
        assert result.success
        assert result.output == "TEST"

    @pytest.mark.asyncio
    async def test_execute_missing_tool(self, tool_registry):
        result = await tool_registry.execute("no_such_tool", {})
        assert not result.success
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_execute_timeout(self, tool_registry):
        async def slow_tool() -> ToolResult:
            await asyncio.sleep(10)
            return ToolResult(success=True, output="done")

        tool_registry.register(ToolEntry(
            name="slow_tool",
            description="slow",
            parameters={"type": "object", "properties": {}},
            handler=slow_tool,
            timeout_sec=1,
        ))

        result = await tool_registry.execute("slow_tool", {})
        assert not result.success
        assert "timed out" in result.error

    @pytest.mark.asyncio
    async def test_execute_error_handling(self, tool_registry):
        async def failing_tool() -> ToolResult:
            raise ValueError("something went wrong")

        tool_registry.register(ToolEntry(
            name="fail_tool",
            description="fails",
            parameters={"type": "object", "properties": {}},
            handler=failing_tool,
        ))

        result = await tool_registry.execute("fail_tool", {})
        assert not result.success
        assert "something went wrong" in result.error


class TestToolDecorator:
    """Test the @tool decorator."""

    def test_decorator_registers_tool(self):
        ToolRegistry.reset()

        @tool(name="decorated_tool", description="auto-registered")
        async def my_tool():
            return ToolResult(success=True, output="decorated")

        registry = ToolRegistry()
        assert "decorated_tool" in registry.list_tools()
        ToolRegistry.reset()
