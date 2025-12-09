"""
Tests for the GitHub tool.
"""

import os
import pytest
from pytest_httpx import HTTPXMock

from mcp_server.tools.github import get_pr_diff


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
