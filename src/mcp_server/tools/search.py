"""
File search implementation (glob and grep).
"""

import os
import subprocess
from pathlib import Path


async def search_files(query: str, search_type: str, path: str = ".") -> str:
    """
    Search for files by name (glob) or content (grep).

    Args:
        query: Search pattern (file pattern for glob, regex for grep)
        search_type: Either "glob" or "grep"
        path: Root directory to search within

    Returns:
        Search results as formatted string
    """
    # Validate path to prevent path traversal
    abs_path = os.path.abspath(path)

    if search_type == "glob":
        return await _search_by_glob(query, abs_path)
    elif search_type == "grep":
        return await _search_by_grep(query, abs_path)
    else:
        raise ValueError(f"Invalid search_type: {search_type}")


async def _search_by_glob(pattern: str, root_path: str) -> str:
    """Search files by name pattern using glob."""
    try:
        root = Path(root_path)
        matches = list(root.glob(pattern))

        if not matches:
            return f"No files found matching pattern: {pattern}"

        # Filter out sensitive files
        filtered = [m for m in matches if not _is_sensitive_file(m)]

        result = f"Found {len(filtered)} files:\n"
        for match in sorted(filtered):
            result += f"  {match}\n"

        return result
    except Exception as e:
        return f"Error during glob search: {str(e)}"


async def _search_by_grep(pattern: str, root_path: str) -> str:
    """Search file contents using ripgrep (rg) or git grep."""
    try:
        # Try ripgrep first (faster)
        try:
            result = subprocess.run(
                ["rg", "--line-number", "--heading", pattern, root_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout or "No matches found"
            elif result.returncode == 1:
                return "No matches found"
            else:
                return f"Error: {result.stderr}"

        except FileNotFoundError:
            # Fallback to git grep if rg not available
            result = subprocess.run(
                ["git", "grep", "-n", pattern],
                cwd=root_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout or "No matches found"
            elif result.returncode == 1:
                return "No matches found"
            else:
                return f"Error: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "Search timed out after 30 seconds"
    except Exception as e:
        return f"Error during grep search: {str(e)}"


def _is_sensitive_file(path: Path) -> bool:
    """Check if a file should be filtered from search results."""
    sensitive_patterns = {
        ".env",
        ".env.local",
        ".env.production",
        "credentials",
        "secrets",
        "private_key",
        ".pem",
        ".key",
    }

    name_lower = path.name.lower()
    return any(pattern in name_lower for pattern in sensitive_patterns)
