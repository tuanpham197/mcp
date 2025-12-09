"""
Safe file reading with path validation.
"""

import os
from pathlib import Path


async def read_file(file_path: str, root_dir: str = ".") -> str:
    """
    Read file contents with path traversal protection.

    Args:
        file_path: Path to the file to read
        root_dir: Root directory to constrain reads within

    Returns:
        File contents as string
    """
    try:
        # Resolve absolute paths and validate
        abs_root = os.path.abspath(root_dir)
        abs_file = os.path.abspath(file_path)

        # Ensure the file is within the allowed root directory
        if not abs_file.startswith(abs_root):
            return f"Error: Access denied - file is outside allowed directory"

        # Check if file exists
        if not os.path.isfile(abs_file):
            return f"Error: File not found: {file_path}"

        # Check if file is sensitive
        if _is_sensitive_file(Path(abs_file)):
            return f"Error: Cannot read sensitive file: {file_path}"

        # Read file contents
        with open(abs_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    except UnicodeDecodeError:
        return f"Error: File is not a text file or has unsupported encoding: {file_path}"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def _is_sensitive_file(path: Path) -> bool:
    """Check if a file contains sensitive information."""
    sensitive_patterns = {
        ".env",
        ".env.local",
        ".env.production",
        "credentials",
        "secrets",
        "private_key",
        ".pem",
        ".key",
        "id_rsa",
        "id_dsa",
    }

    name_lower = path.name.lower()
    return any(pattern in name_lower for pattern in sensitive_patterns)
