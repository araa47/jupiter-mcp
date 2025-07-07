"""
Jupiter MCP Server - Model Context Protocol server for Jupiter APIs.

This package provides MCP server tools for interacting with Jupiter's Ultra and Trigger APIs.
"""

from .jupiter_api import JupiterAPI
from .server import api, mcp  # type: ignore

__all__ = ["JupiterAPI", "mcp", "api"]
