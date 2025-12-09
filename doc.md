# MCP Server: Code Search, Read & PR Analysis

## Project Overview
This is a Python-based Model Context Protocol (MCP) server designed to enable LLMs to interact with codebases.
**Core Capabilities:**
1. **Search**: Find files by name or grep source code content (local & GitHub).
2. **Read**: Retrieve full file contents for context.
3. **Diffs**: Fetch and analyze Pull Request changes.

## Build & Run
- **Dependency Manager**: [uv / poetry / pip]
- **Install**: `pip install -e .`
- **Run Server**: `python -m server_name`
- **Run Tests**: `pytest`
- **Lint/Format**: `ruff check .`

## Codebase Map
- `src/`: Core logic.
  - `tools/`: MCP tool definitions.
    - `search.py`: Implementation of file search (glob/grep).
    - `read.py`: Safe file reading logic.
    - `github.py`: GitHub API integration for PRs.
  - `server.py`: Main MCP server entrypoint and tool registration.
- `tests/`: Unit tests for tool inputs/outputs.

## Development Guidelines
1. **Security (Critical)**:
   - **Path Traversal**: All "Read" tools must validate paths to ensure they stay within the allow-listed root directory.
   - **Secrets**: Filter out `.env` or secret files from "Search" results.
2. **Performance**:
   - For "Search", prefer native tools (like `rg` or `git grep`) over Python iteration where possible for speed.
   - For "Read", enforce a strictly typed schema for arguments to prevent invalid file handling.
3. **Statelessness**: Do not persist state between tool calls.