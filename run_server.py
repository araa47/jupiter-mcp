#!/usr/bin/env python3
"""
Jupiter Ultra MCP Server Entry Point

This script provides a clean entry point for running the Jupiter Ultra MCP server.
"""

import sys
from pathlib import Path


def main() -> None:
    """Main entry point for the Jupiter Ultra MCP server."""
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    # Import and run the MCP server
    from src.server import main as server_main  # noqa: E402

    server_main()


if __name__ == "__main__":
    main()
