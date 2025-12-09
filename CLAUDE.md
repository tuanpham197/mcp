# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Type

Python-based MCP (Model Context Protocol) server enabling LLMs to interact with codebases through search, read, and PR analysis capabilities.

## Development Commands

**Setup (using uv):**
```bash
uv sync                   # Install dependencies from lock file
uv pip install -e .       # Install package in editable mode
```

**Run Server:**
```bash
uv run python -m mcp_server
```

**Testing:**
```bash
uv run pytest                    # Run all tests
uv run pytest tests/test_*.py    # Run specific test file
```

**Linting:**
```bash
uv run ruff check .
```

## Architecture

**Core Components:**
- `src/mcp_server/`: Main package directory
  - `server.py`: Main MCP server entrypoint and tool registration
  - `tools/`: MCP tool implementations
    - `search.py`: File search (glob/grep) for local and GitHub repos
    - `read.py`: Safe file reading with path validation
    - `github.py`: GitHub API integration for fetching PR diffs
- `tests/`: Unit tests for tool inputs/outputs

**Tool Capabilities:**
1. **Search**: Find files by name or grep content across codebase
2. **Read**: Retrieve full file contents for analysis
3. **Diffs**: Fetch and analyze Pull Request changes from GitHub

## Critical Security Requirements

**Path Traversal Prevention:**
All file read operations MUST validate paths to ensure they remain within the allow-listed root directory. Never allow reading files outside the authorized workspace.

**Secret Filtering:**
Search results must exclude sensitive files (`.env`, credentials, tokens, etc.) from results to prevent accidental exposure.

## Performance Considerations

- **Search Operations**: Use native tools (`rg`, `git grep`) instead of Python iteration for better performance
- **Strict Typing**: Enforce strictly typed schemas for tool arguments to prevent invalid file handling
- **Stateless Design**: Do not persist state between tool calls
