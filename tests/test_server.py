"""
Tests for the main MCP server.
"""

import pytest
from mcp_server.server import app, list_tools, call_tool


@pytest.mark.asyncio
async def test_list_tools():
    """Test that all expected tools are registered."""
    tools = await list_tools()

    assert len(tools) == 6, "Expected 6 tools to be registered"

    tool_names = [tool.name for tool in tools]
    assert "search_files" in tool_names
    assert "read_file" in tool_names
    assert "get_pr_diff" in tool_names
    assert "search_github_files" in tool_names
    assert "read_github_file" in tool_names
    assert "grep_github_repo" in tool_names


@pytest.mark.asyncio
async def test_list_tools_schemas():
    """Test that all tools have proper input schemas."""
    tools = await list_tools()

    for tool in tools:
        assert tool.name, "Tool must have a name"
        assert tool.description, "Tool must have a description"
        assert tool.inputSchema, "Tool must have an input schema"
        assert tool.inputSchema.get("type") == "object"
        assert "properties" in tool.inputSchema
        assert "required" in tool.inputSchema


@pytest.mark.asyncio
async def test_search_files_tool_schema():
    """Test search_files tool has correct schema."""
    tools = await list_tools()
    search_tool = next(t for t in tools if t.name == "search_files")

    props = search_tool.inputSchema["properties"]
    assert "query" in props
    assert "search_type" in props
    assert "path" in props

    required = search_tool.inputSchema["required"]
    assert "query" in required
    assert "search_type" in required


@pytest.mark.asyncio
async def test_read_file_tool_schema():
    """Test read_file tool has correct schema."""
    tools = await list_tools()
    read_tool = next(t for t in tools if t.name == "read_file")

    props = read_tool.inputSchema["properties"]
    assert "file_path" in props

    required = read_tool.inputSchema["required"]
    assert "file_path" in required


@pytest.mark.asyncio
async def test_get_pr_diff_tool_schema():
    """Test get_pr_diff tool has correct schema."""
    tools = await list_tools()
    pr_tool = next(t for t in tools if t.name == "get_pr_diff")

    props = pr_tool.inputSchema["properties"]
    assert "repo" in props
    assert "pr_number" in props

    required = pr_tool.inputSchema["required"]
    assert "repo" in required
    assert "pr_number" in required


@pytest.mark.asyncio
async def test_call_unknown_tool():
    """Test that calling an unknown tool raises an error."""
    with pytest.raises(ValueError, match="Unknown tool"):
        await call_tool("nonexistent_tool", {})
