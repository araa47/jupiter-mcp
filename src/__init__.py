"""
Jupiter MCP Server - Model Context Protocol server for Jupiter APIs.

This package provides MCP server tools for interacting with Jupiter's Ultra and Trigger APIs.
"""

from .jupiter_api import JupiterAPI
from .server import setup_server  # type: ignore

# For backward compatibility, create default instances
mcp, api = setup_server(client_side_mode=False)

__all__ = ["JupiterAPI", "mcp", "api", "setup_server"]
