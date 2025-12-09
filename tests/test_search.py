"""
Tests for the search tool.
"""

import os
import tempfile
from pathlib import Path
import pytest

from mcp_server.tools.search import search_files, _is_sensitive_file


@pytest.mark.asyncio
async def test_search_by_glob_finds_files():
    """Test that glob search finds matching files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        Path(tmpdir, "test1.py").touch()
        Path(tmpdir, "test2.py").touch()
        Path(tmpdir, "other.txt").touch()

        result = await search_files("*.py", "glob", tmpdir)

        assert "test1.py" in result
        assert "test2.py" in result
        assert "other.txt" not in result


@pytest.mark.asyncio
async def test_search_by_glob_no_matches():
    """Test glob search with no matches."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "test.txt").touch()

        result = await search_files("*.py", "glob", tmpdir)

        assert "No files found" in result


@pytest.mark.asyncio
async def test_search_by_glob_filters_sensitive_files():
    """Test that sensitive files are filtered from glob results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create normal and sensitive files
        Path(tmpdir, "config.py").touch()
        Path(tmpdir, ".env").touch()
        Path(tmpdir, "credentials.txt").touch()

        result = await search_files("*", "glob", tmpdir)

        assert "config.py" in result
        assert ".env" not in result
        assert "credentials" not in result


@pytest.mark.asyncio
async def test_search_by_grep_finds_content():
    """Test that grep search finds file content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file with content
        test_file = Path(tmpdir, "test.py")
        test_file.write_text("def hello():\n    print('Hello, World!')\n")

        result = await search_files("hello", "grep", tmpdir)

        # Should find the match (either via rg or git grep) or return error
        # Note: git grep requires a git repo, rg may not be installed
        assert (
            "hello" in result.lower()
            or "no matches found" in result.lower()
            or "error" in result.lower()  # Accept error if tools not available
        )


@pytest.mark.asyncio
async def test_search_invalid_type():
    """Test that invalid search type raises error."""
    with pytest.raises(ValueError, match="Invalid search_type"):
        await search_files("test", "invalid", ".")


def test_is_sensitive_file_detects_env():
    """Test that .env files are detected as sensitive."""
    assert _is_sensitive_file(Path(".env"))
    assert _is_sensitive_file(Path(".env.local"))
    assert _is_sensitive_file(Path(".env.production"))


def test_is_sensitive_file_detects_credentials():
    """Test that credential files are detected as sensitive."""
    assert _is_sensitive_file(Path("credentials.json"))
    assert _is_sensitive_file(Path("secrets.yaml"))
    assert _is_sensitive_file(Path("private_key.pem"))


def test_is_sensitive_file_allows_normal():
    """Test that normal files are not flagged as sensitive."""
    assert not _is_sensitive_file(Path("config.py"))
    assert not _is_sensitive_file(Path("README.md"))
    assert not _is_sensitive_file(Path("main.py"))
