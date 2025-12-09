"""
MCP Server for code search, read, and PR analysis.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server
app = Server("mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_files",
            description="Search for files by name pattern (glob) or content (grep) in local codebase",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (file pattern for glob, regex for grep)",
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["glob", "grep"],
                        "description": "Type of search to perform",
                    },
                    "path": {
                        "type": "string",
                        "description": "Root path to search within (defaults to current directory)",
                    },
                },
                "required": ["query", "search_type"],
            },
        ),
        Tool(
            name="read_file",
            description="Read the full contents of a file from the local filesystem",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file to read",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="get_pr_diff",
            description="Fetch and analyze Pull Request changes from GitHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'",
                    },
                    "pr_number": {
                        "type": "integer",
                        "description": "Pull request number",
                    },
                },
                "required": ["repo", "pr_number"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""

    if name == "search_files":
        from .tools.search import search_files
        result = await search_files(
            query=arguments["query"],
            search_type=arguments["search_type"],
            path=arguments.get("path", "."),
        )
        return [TextContent(type="text", text=result)]

    elif name == "read_file":
        from .tools.read import read_file
        result = await read_file(file_path=arguments["file_path"])
        return [TextContent(type="text", text=result)]

    elif name == "get_pr_diff":
        from .tools.github import get_pr_diff
        result = await get_pr_diff(
            repo=arguments["repo"],
            pr_number=arguments["pr_number"],
        )
        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
