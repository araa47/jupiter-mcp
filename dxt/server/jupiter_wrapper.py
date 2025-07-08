#!/usr/bin/env python3
"""
Jupiter MCP DXT Wrapper

This script acts as a wrapper for the Jupiter MCP server when running as a DXT extension.
It handles finding uvx with the full path and manages environment variables from .env file.
"""

import os
import shutil
import sys
from typing import Optional


def debug_print(message: str) -> None:
    """Print debug messages to stderr so they appear in Claude Desktop logs."""
    print(f"[Jupiter Wrapper Debug] {message}", file=sys.stderr, flush=True)


def find_uvx_path() -> Optional[str]:
    """
    Find the full path to uvx executable.

    Returns:
        Path to uvx executable or None if not found
    """
    # Try to find uvx using shutil.which (cross-platform)
    uvx_path = shutil.which("uvx")
    if uvx_path:
        debug_print(f"Found uvx using which: {uvx_path}")
        return uvx_path

    # Common paths where uvx might be installed
    common_paths = [
        "/usr/local/bin/uvx",
        "/opt/homebrew/bin/uvx",
        "/usr/bin/uvx",
        os.path.expanduser("~/.local/bin/uvx"),
        os.path.expanduser("~/.cargo/bin/uvx"),
        "/usr/local/cargo/bin/uvx",
    ]

    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            debug_print(f"Found uvx at: {path}")
            return path

    debug_print("uvx not found in any common locations")
    return None


def load_env_file(env_file_path: str) -> dict[str, str]:
    """
    Load environment variables from .env file.

    Args:
        env_file_path: Path to the .env file

    Returns:
        Dictionary of environment variables
    """
    env_vars: dict[str, str] = {}

    if not os.path.exists(env_file_path):
        debug_print(f"Warning: .env file not found at {env_file_path}")
        return env_vars

    try:
        with open(env_file_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip().strip('"').strip("'")
                    else:
                        debug_print(
                            f"Warning: Invalid line {line_num} in .env file: {line}"
                        )

        debug_print(
            f"Loaded {len(env_vars)} environment variables from {env_file_path}"
        )
        # Don't log the actual values for security
        debug_print(f"Environment variable keys: {list(env_vars.keys())}")

    except Exception as e:
        debug_print(f"Error reading .env file: {e}")

    return env_vars


def main() -> None:
    """Main wrapper function."""
    debug_print("Starting Jupiter MCP wrapper")
    debug_print(f"Python executable: {sys.executable}")
    debug_print(f"Python version: {sys.version}")
    debug_print(f"Current working directory: {os.getcwd()}")
    debug_print(f"Command line args: {sys.argv}")

    # Get environment file path from environment variable
    env_file_path = os.environ.get("ENV_FILE_PATH")

    if not env_file_path:
        debug_print("Error: ENV_FILE_PATH not provided")
        sys.exit(1)

    debug_print(f"ENV_FILE_PATH: {env_file_path}")

    # Load environment variables from .env file
    env_vars = load_env_file(env_file_path)

    # Update current environment with loaded variables
    os.environ.update(env_vars)

    # Find uvx
    uvx_path = find_uvx_path()
    if not uvx_path:
        debug_print(
            "Error: uvx not found. Please install uv from https://docs.astral.sh/uv/getting-started/installation/"
        )
        sys.exit(1)

    debug_print(f"Using uvx at: {uvx_path}")

    # Execute the Jupiter MCP server using uvx with git installation
    try:
        debug_print("Executing Jupiter MCP server with uvx from git repository...")
        os.execv(
            uvx_path,
            [
                uvx_path,
                "--from",
                "git+https://github.com/araa47/jupiter-mcp",
                "jupiter-mcp",
            ],
        )
    except Exception as e:
        debug_print(f"Error executing Jupiter MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
