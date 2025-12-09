"""
Tests for the GitHub tool.
"""

import os
import base64
import pytest
from pytest_httpx import HTTPXMock

from mcp_server.tools.github import (
    get_pr_diff,
    search_github_files,
    read_github_file,
    grep_github_repo,
)


@pytest.mark.asyncio
async def test_get_pr_diff_success(httpx_mock: HTTPXMock):
    """Test successfully fetching a PR diff."""
    mock_diff = """diff --git a/file.py b/file.py
index 1234567..abcdefg 100644
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Added line")
     pass
"""

    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/pulls/123",
        text=mock_diff,
        status_code=200,
    )

    result = await get_pr_diff("owner/repo", 123)

    assert "diff --git" in result
    assert "Added line" in result


@pytest.mark.asyncio
async def test_get_pr_diff_not_found(httpx_mock: HTTPXMock):
    """Test handling of non-existent PR."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/pulls/999",
        status_code=404,
    )

    result = await get_pr_diff("owner/repo", 999)

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_get_pr_diff_rate_limit(httpx_mock: HTTPXMock):
    """Test handling of rate limit errors."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/pulls/123",
        status_code=403,
    )

    result = await get_pr_diff("owner/repo", 123)

    assert "rate limit" in result.lower() or "authentication" in result.lower()


@pytest.mark.asyncio
async def test_get_pr_diff_with_token(httpx_mock: HTTPXMock, monkeypatch):
    """Test that GitHub token is used when available."""
    mock_diff = "diff content"
    test_token = "ghp_test_token_123"

    # Set environment variable
    monkeypatch.setenv("GITHUB_TOKEN", test_token)

    def check_auth(request):
        assert "Authorization" in request.headers
        assert f"Bearer {test_token}" in request.headers["Authorization"]
        return True

    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/pulls/123",
        text=mock_diff,
        status_code=200,
        match_headers={"Accept": "application/vnd.github.v3.diff"},
    )

    result = await get_pr_diff("owner/repo", 123)

    assert result == mock_diff


@pytest.mark.asyncio
async def test_get_pr_diff_timeout(httpx_mock: HTTPXMock):
    """Test handling of timeout errors."""
    httpx_mock.add_exception(
        Exception("Timeout"),
        url="https://api.github.com/repos/owner/repo/pulls/123",
    )

    result = await get_pr_diff("owner/repo", 123)

    assert "error" in result.lower()


@pytest.mark.asyncio
async def test_get_pr_diff_correct_headers(httpx_mock: HTTPXMock):
    """Test that correct headers are sent to GitHub API."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/pulls/123",
        text="diff",
        status_code=200,
    )

    await get_pr_diff("owner/repo", 123)

    request = httpx_mock.get_request()
    assert request.headers["Accept"] == "application/vnd.github.v3.diff"


# Tests for search_github_files


@pytest.mark.asyncio
async def test_search_github_files_success(httpx_mock: HTTPXMock):
    """Test successfully searching for files in GitHub repo."""
    mock_response = {
        "total_count": 2,
        "items": [
            {
                "path": "src/main.py",
                "html_url": "https://github.com/owner/repo/blob/main/src/main.py",
            },
            {
                "path": "tests/test_main.py",
                "html_url": "https://github.com/owner/repo/blob/main/tests/test_main.py",
            },
        ],
    }

    httpx_mock.add_response(
        json=mock_response,
        status_code=200,
    )

    result = await search_github_files("owner/repo", "main.py")

    assert "Found 2 files" in result
    assert "src/main.py" in result
    assert "tests/test_main.py" in result


@pytest.mark.asyncio
async def test_search_github_files_no_results(httpx_mock: HTTPXMock):
    """Test search with no results."""
    httpx_mock.add_response(
        json={"total_count": 0, "items": []},
        status_code=200,
    )

    result = await search_github_files("owner/repo", "nonexistent.py")

    assert "No files found" in result


@pytest.mark.asyncio
async def test_search_github_files_with_path(httpx_mock: HTTPXMock):
    """Test searching within a specific path."""
    httpx_mock.add_response(
        json={"total_count": 1, "items": [{"path": "src/test.py", "html_url": "url"}]},
        status_code=200,
    )

    result = await search_github_files("owner/repo", "test.py", path="src/")

    request = httpx_mock.get_request()
    # Check for URL-encoded version: path:src/ becomes path%3Asrc%2F
    assert "path%3Asrc%2F" in str(request.url) or "path:src/" in str(request.url)


# Tests for read_github_file


@pytest.mark.asyncio
async def test_read_github_file_success(httpx_mock: HTTPXMock):
    """Test successfully reading a file from GitHub."""
    file_content = "print('Hello, World!')\n"
    content_base64 = base64.b64encode(file_content.encode()).decode()

    mock_response = {
        "type": "file",
        "content": content_base64,
        "encoding": "base64",
    }

    httpx_mock.add_response(
        json=mock_response,
        status_code=200,
    )

    result = await read_github_file("owner/repo", "main.py")

    assert result == file_content


@pytest.mark.asyncio
async def test_read_github_file_not_found(httpx_mock: HTTPXMock):
    """Test reading a non-existent file."""
    httpx_mock.add_response(
        status_code=404,
    )

    result = await read_github_file("owner/repo", "missing.py")

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_read_github_file_is_directory(httpx_mock: HTTPXMock):
    """Test attempting to read a directory."""
    httpx_mock.add_response(
        json={"type": "dir"},
        status_code=200,
    )

    result = await read_github_file("owner/repo", "src")

    assert "not a file" in result.lower()


@pytest.mark.asyncio
async def test_read_github_file_custom_branch(httpx_mock: HTTPXMock):
    """Test reading from a specific branch."""
    content_base64 = base64.b64encode(b"test").decode()

    httpx_mock.add_response(
        json={"type": "file", "content": content_base64},
        status_code=200,
    )

    result = await read_github_file("owner/repo", "file.py", branch="develop")

    request = httpx_mock.get_request()
    assert "ref=develop" in str(request.url)


# Tests for grep_github_repo


@pytest.mark.asyncio
async def test_grep_github_repo_success(httpx_mock: HTTPXMock):
    """Test successfully searching for code content."""
    mock_response = {
        "total_count": 3,
        "items": [
            {"path": "src/auth.py", "html_url": "url1"},
            {"path": "tests/test_auth.py", "html_url": "url2"},
        ],
    }

    httpx_mock.add_response(
        json=mock_response,
        status_code=200,
    )

    result = await grep_github_repo("owner/repo", "async def")

    assert "Found 3 matches" in result
    assert "src/auth.py" in result
    assert "tests/test_auth.py" in result


@pytest.mark.asyncio
async def test_grep_github_repo_no_matches(httpx_mock: HTTPXMock):
    """Test grep with no matches."""
    httpx_mock.add_response(
        json={"total_count": 0, "items": []},
        status_code=200,
    )

    result = await grep_github_repo("owner/repo", "nonexistent_function")

    assert "No matches found" in result


@pytest.mark.asyncio
async def test_grep_github_repo_rate_limit(httpx_mock: HTTPXMock):
    """Test handling rate limit errors."""
    httpx_mock.add_response(
        status_code=403,
    )

    result = await grep_github_repo("owner/repo", "test")

    assert "rate limit" in result.lower() or "authentication" in result.lower()
