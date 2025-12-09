"""
Tests for the read tool.
"""

import os
import tempfile
from pathlib import Path
import pytest

from mcp_server.tools.read import read_file, _is_sensitive_file


@pytest.mark.asyncio
async def test_read_file_success():
    """Test successfully reading a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir, "test.txt")
        test_content = "Hello, World!\nThis is a test file."
        test_file.write_text(test_content)

        result = await read_file(str(test_file), tmpdir)

        assert result == test_content


@pytest.mark.asyncio
async def test_read_file_not_found():
    """Test reading a non-existent file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await read_file(
            os.path.join(tmpdir, "nonexistent.txt"),
            tmpdir
        )

        assert "File not found" in result


@pytest.mark.asyncio
async def test_read_file_path_traversal_protection():
    """Test that path traversal attempts are blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Try to read a file outside the allowed directory
        result = await read_file("/etc/passwd", tmpdir)

        assert "Access denied" in result or "outside allowed directory" in result


@pytest.mark.asyncio
async def test_read_file_relative_path_traversal():
    """Test that relative path traversal is blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Try to use .. to escape the directory
        result = await read_file("../../etc/passwd", tmpdir)

        assert "Access denied" in result or "outside allowed directory" in result


@pytest.mark.asyncio
async def test_read_sensitive_file_blocked():
    """Test that sensitive files cannot be read."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir, ".env")
        env_file.write_text("SECRET_KEY=abc123")

        result = await read_file(str(env_file), tmpdir)

        assert "Cannot read sensitive file" in result or "sensitive" in result.lower()


@pytest.mark.asyncio
async def test_read_file_binary_error():
    """Test handling of binary/non-text files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        binary_file = Path(tmpdir, "test.bin")
        binary_file.write_bytes(b'\x00\x01\x02\x03\xff\xfe')

        result = await read_file(str(binary_file), tmpdir)

        # Should handle encoding error gracefully
        assert "Error" in result or result == ""


def test_is_sensitive_file_env():
    """Test detection of environment files."""
    assert _is_sensitive_file(Path(".env"))
    assert _is_sensitive_file(Path(".env.local"))
    assert _is_sensitive_file(Path("config/.env.production"))


def test_is_sensitive_file_keys():
    """Test detection of key files."""
    assert _is_sensitive_file(Path("private_key.pem"))
    assert _is_sensitive_file(Path("id_rsa"))
    assert _is_sensitive_file(Path("cert.key"))


def test_is_sensitive_file_credentials():
    """Test detection of credential files."""
    assert _is_sensitive_file(Path("credentials.json"))
    assert _is_sensitive_file(Path("secrets.yaml"))


def test_is_sensitive_file_normal_files():
    """Test that normal files are not flagged."""
    assert not _is_sensitive_file(Path("README.md"))
    assert not _is_sensitive_file(Path("config.py"))
    assert not _is_sensitive_file(Path("test.txt"))
