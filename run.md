# Running the MCP Server

This guide explains how to run the MCP server and integrate it with VS Code.

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- VS Code with Claude Code extension or another MCP-compatible client

## Installation

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Install the package in development mode:**
   ```bash
   uv pip install -e .
   ```

## Running the Server

### Option 1: Run as Python Module
```bash
uv run python -m mcp_server
```

### Option 2: Run via stdio (for MCP clients)
The server runs via stdio by default, which is the standard way MCP servers communicate with clients.

```bash
uv run python -m mcp_server
```

### Option 3: Test the Server Manually
You can test individual tools programmatically:

```python
import asyncio
from mcp_server.tools.search import search_files
from mcp_server.tools.read import read_file

# Test search
result = asyncio.run(search_files("*.py", "glob", "."))
print(result)

# Test read
result = asyncio.run(read_file("README.md", "."))
print(result)
```

## Configuration for VS Code

### Step 1: Install Claude Code Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Claude Code"
4. Install the extension

### Step 2: Configure MCP Server

Create or edit the MCP configuration file:

**Location:**
- **macOS/Linux**: `~/.config/claude-code/mcp_config.json`
- **Windows**: `%APPDATA%\claude-code\mcp_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "code-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/tuanpham/mcp",
        "python",
        "-m",
        "mcp_server"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

**Important:** Replace `/home/tuanpham/mcp` with the absolute path to your project directory.

### Step 3: Set GitHub Token (Optional)

For GitHub PR analysis functionality, set your GitHub personal access token:

1. Create a token at: https://github.com/settings/tokens
2. Add it to the `env` section in the config above, OR
3. Set it as an environment variable:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

### Step 4: Restart VS Code

1. Close VS Code completely
2. Reopen VS Code
3. Open the Claude Code extension
4. Your MCP server should now be available

## Verifying the Installation

### Check MCP Server Status

In Claude Code, you should see the "code-search" server available. You can test it by asking Claude to:

- "Search for Python files in this project"
- "Read the contents of README.md"
- "Get the diff for PR #123 in owner/repo"

### Check Server Logs

If the server isn't working, check the logs:

**macOS/Linux:**
```bash
tail -f ~/.config/claude-code/logs/mcp-*.log
```

**Windows:**
```powershell
Get-Content $env:APPDATA\claude-code\logs\mcp-*.log -Tail 50 -Wait
```

## Alternative: Using with Claude Desktop App

If you're using the Claude Desktop app instead of VS Code:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "code-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/tuanpham/mcp",
        "python",
        "-m",
        "mcp_server"
      ]
    }
  }
}
```

## Troubleshooting

### Server Won't Start

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.12+
   ```

2. **Verify installation:**
   ```bash
   uv run python -c "import mcp_server; print('OK')"
   ```

3. **Check for errors:**
   ```bash
   uv run python -m mcp_server 2>&1 | tee server.log
   ```

### Tools Not Working

1. **For grep search**: Install ripgrep for better performance:
   ```bash
   # macOS
   brew install ripgrep

   # Ubuntu/Debian
   sudo apt install ripgrep

   # Windows
   winget install BurntSushi.ripgrep.MSVC
   ```

2. **For GitHub API**: Ensure GITHUB_TOKEN is set and valid

### Permission Errors

Make sure the server has read access to the directories you want to search:
```bash
chmod -R +r /path/to/search
```

## Available Tools

Once configured, the following MCP tools are available:

1. **search_files**
   - Search by filename pattern (glob)
   - Search by content (grep)
   - Automatically filters sensitive files

2. **read_file**
   - Read file contents safely
   - Path traversal protection
   - Blocks sensitive files (.env, keys, etc.)

3. **get_pr_diff**
   - Fetch GitHub PR diffs
   - Analyze code changes
   - Requires GitHub token for private repos

## Example Usage in Claude

Once installed, you can ask Claude:

```
"Search for all Python files containing 'async def'"
"Read the contents of src/mcp_server/server.py"
"Get the diff for PR #42 in anthropics/anthropic-sdk-python"
```

## Security Notes

- The server automatically blocks access to sensitive files (.env, credentials, keys)
- All file reads are validated to prevent path traversal attacks
- GitHub tokens should be stored securely (never commit them)
- The server only has access to files in the directories you configure

## Development Mode

For development, you can run the tests to verify everything works:

```bash
uv run pytest -v
```

To run the linter:

```bash
uv run ruff check .
```
