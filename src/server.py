#!/usr/bin/env python3
"""
Jupiter Ultra MCP Server

This module provides an MCP server for interacting with the Jupiter Ultra API.
"""

from fastmcp import FastMCP

from .jupiter_ultra_api import JupiterUltraAPI

# Create the FastMCP server instance
mcp = FastMCP("Jupiter Ultra MCP Server")  # type: ignore

# Initialize the Jupiter Ultra API client
api = JupiterUltraAPI()

# Register all API methods as MCP tools using the clean pattern
mcp.tool()(api.get_order)
mcp.tool()(api.execute_order)
mcp.tool()(api.get_balances)
mcp.tool()(api.get_shield)
mcp.tool()(api.search_token)


@mcp.resource("wallet://info")
def get_wallet_info() -> str:
    """Get information about the configured wallet."""
    info = api.get_wallet_info()
    if "error" in info:
        return f"Error: {info['error']}"

    return f"""
Wallet Configuration:
- Address: {info['wallet_address']}
- Network: {info['network']}
- RPC URL: {info['rpc_url']}
"""


def main():
    """Main entry point for the Jupiter Ultra MCP server."""
    print("🚀 Jupiter Ultra MCP Server")
    print("=" * 50)
    print("")
    print("🔗 Connection Details:")
    print(f"  Network: {api.network}")
    print(f"  RPC URL: {api.rpc_url}")
    print("")

    # Get wallet info
    wallet_info = api.get_wallet_info()
    if wallet_info.get("wallet_address"):
        print(f"💳 Wallet: {wallet_info['wallet_address']}")
    else:
        print("⚠️  No wallet configured")

    print("")
    print("🛠️  Available Tools:")
    print("  • get_order - Get swap quotes and orders")
    print("  • execute_order - Sign and execute transactions")
    print("  • get_balances - Get wallet token balances")
    print("  • get_shield - Get token security information")
    print("  • search_token - Search for tokens")
    print("")
    print("📋 Available Resources:")
    print("  • wallet://info - Get wallet configuration details")
    print("")
    print("🔥 Server is ready! Connect with your MCP client.")
    print("")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
