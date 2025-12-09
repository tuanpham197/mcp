"""
GitHub API integration for PR analysis, file search, and file reading.
"""

import os
import base64
from typing import Optional
import httpx


async def get_pr_diff(repo: str, pr_number: int) -> str:
    """
    Fetch Pull Request diff from GitHub.

    Args:
        repo: Repository in format 'owner/repo'
        pr_number: Pull request number

    Returns:
        PR diff as string
    """
    try:
        # GitHub API endpoint
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

        # Get GitHub token from environment if available
        headers = {
            "Accept": "application/vnd.github.v3.diff",
        }

        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        # Fetch PR diff
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)

            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                return f"Error: PR #{pr_number} not found in {repo}"
            elif response.status_code == 403:
                return "Error: Rate limit exceeded or authentication required. Set GITHUB_TOKEN environment variable."
            else:
                return f"Error: GitHub API returned status {response.status_code}"

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error fetching PR diff: {str(e)}"


async def search_github_files(
    repo: str,
    query: str,
    path: Optional[str] = None,
) -> str:
    """
    Search for files in a GitHub repository by name or path.

    Args:
        repo: Repository in format 'owner/repo'
        query: Search query (filename or path pattern)
        path: Optional path prefix to search within (e.g., "src/")

    Returns:
        List of matching files with their paths
    """
    try:
        # Build search query
        search_query = f"repo:{repo} filename:{query}"
        if path:
            search_query += f" path:{path}"

        url = "https://api.github.com/search/code"
        params = {"q": search_query, "per_page": 100}

        headers = _get_github_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)

            if response.status_code == 200:
                data = response.json()
                total_count = data.get("total_count", 0)

                if total_count == 0:
                    return f"No files found matching: {query}"

                items = data.get("items", [])
                result = f"Found {total_count} files (showing first {len(items)}):\n\n"

                for item in items:
                    file_path = item.get("path", "")
                    html_url = item.get("html_url", "")
                    result += f"  📄 {file_path}\n     {html_url}\n\n"

                return result

            elif response.status_code == 403:
                return "Error: Rate limit exceeded or authentication required. Set GITHUB_TOKEN environment variable."
            elif response.status_code == 422:
                return f"Error: Invalid search query. Check your search parameters."
            else:
                return f"Error: GitHub API returned status {response.status_code}"

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error searching GitHub files: {str(e)}"


async def read_github_file(
    repo: str,
    file_path: str,
    branch: str = "main",
) -> str:
    """
    Read the contents of a file from a GitHub repository.

    Args:
        repo: Repository in format 'owner/repo'
        file_path: Path to the file in the repository
        branch: Branch name (defaults to "main")

    Returns:
        File contents as string
    """
    try:
        # GitHub API endpoint for file contents
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        params = {"ref": branch}

        headers = _get_github_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)

            if response.status_code == 200:
                data = response.json()

                # Check if it's a file (not a directory)
                if data.get("type") != "file":
                    return f"Error: {file_path} is not a file (it might be a directory)"

                # Decode base64 content
                content_base64 = data.get("content", "")
                if not content_base64:
                    return "Error: File content is empty or unavailable"

                try:
                    content = base64.b64decode(content_base64).decode("utf-8")
                    return content
                except UnicodeDecodeError:
                    return f"Error: File is not a text file or has unsupported encoding"

            elif response.status_code == 404:
                return f"Error: File not found: {file_path} (branch: {branch})"
            elif response.status_code == 403:
                return "Error: Rate limit exceeded or authentication required. Set GITHUB_TOKEN environment variable."
            else:
                return f"Error: GitHub API returned status {response.status_code}"

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error reading GitHub file: {str(e)}"


async def grep_github_repo(
    repo: str,
    query: str,
    path: Optional[str] = None,
) -> str:
    """
    Search for code content in a GitHub repository (grep-like functionality).

    Args:
        repo: Repository in format 'owner/repo'
        query: Code search query (text to find in files)
        path: Optional path prefix to search within

    Returns:
        Search results with file paths and matching lines
    """
    try:
        # Build search query
        search_query = f"repo:{repo} {query}"
        if path:
            search_query += f" path:{path}"

        url = "https://api.github.com/search/code"
        params = {"q": search_query, "per_page": 30}

        headers = _get_github_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)

            if response.status_code == 200:
                data = response.json()
                total_count = data.get("total_count", 0)

                if total_count == 0:
                    return f"No matches found for: {query}"

                items = data.get("items", [])
                result = f"Found {total_count} matches (showing first {len(items)}):\n\n"

                for item in items:
                    file_path = item.get("path", "")
                    html_url = item.get("html_url", "")
                    result += f"  📄 {file_path}\n     {html_url}\n\n"

                result += "\nNote: Use read_github_file to view full file contents."
                return result

            elif response.status_code == 403:
                return "Error: Rate limit exceeded or authentication required. Set GITHUB_TOKEN environment variable."
            elif response.status_code == 422:
                return f"Error: Invalid search query. Try a more specific search."
            else:
                return f"Error: GitHub API returned status {response.status_code}"

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error searching GitHub code: {str(e)}"


def _get_github_headers() -> dict:
    """Get standard headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    return headers
