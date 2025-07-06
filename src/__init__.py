"""
Jupiter Ultra MCP Server Package

A Python MCP server that provides tools to access the Jupiter Ultra API.
"""

from .jupiter_ultra_api import JupiterUltraAPI
from .server import api, mcp  # type: ignore

__all__ = ["JupiterUltraAPI", "mcp", "api"]
