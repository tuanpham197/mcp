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
  - `server.py`: Main MCP server entrypoint and tool registration (6 tools)
  - `tools/`: MCP tool implementations
    - `search.py`: File search (glob/grep) for local codebases
    - `read.py`: Safe file reading with path validation for local files
    - `github.py`: GitHub API integration (PR diffs, file search, file reading, code grep)
- `tests/`: Unit tests for all tools (40 tests)

**Tool Capabilities:**

*Local Operations:*
1. **search_files**: Find files by name (glob) or content (grep) in local codebase
2. **read_file**: Read local file contents with security validation

*GitHub Operations:*
3. **get_pr_diff**: Fetch and analyze Pull Request diffs
4. **search_github_files**: Search for files by name in GitHub repositories
5. **read_github_file**: Read file contents directly from GitHub repositories
6. **grep_github_repo**: Search code content in GitHub repositories (grep-like)

## Critical Security Requirements

**Path Traversal Prevention:**
All file read operations MUST validate paths to ensure they remain within the allow-listed root directory. Never allow reading files outside the authorized workspace.

**Secret Filtering:**
Search results must exclude sensitive files (`.env`, credentials, tokens, etc.) from results to prevent accidental exposure.

## Performance Considerations

- **Search Operations**: Use native tools (`rg`, `git grep`) instead of Python iteration for better performance
- **Strict Typing**: Enforce strictly typed schemas for tool arguments to prevent invalid file handling
- **Stateless Design**: Do not persist state between tool calls
