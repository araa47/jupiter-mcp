#!/usr/bin/env python3
"""
Jupiter MCP Server

This module provides an MCP server for interacting with the Jupiter APIs.
"""

from fastmcp import FastMCP

from .jupiter_api import JupiterAPI

# Create the FastMCP server instance
mcp = FastMCP("Jupiter MCP Server")  # type: ignore

# Initialize the Jupiter API client
api = JupiterAPI()

# Register all API methods as MCP tools using the clean pattern
# Phase 1: Ultra API tools (immediate swaps)
mcp.tool()(api.get_swap_quote)
mcp.tool()(api.execute_swap_transaction)
mcp.tool()(api.get_balances)
mcp.tool()(api.get_shield)
mcp.tool()(api.search_token)

# Phase 2: Trigger API tools (limit orders)
mcp.tool()(api.create_limit_order)
mcp.tool()(api.execute_limit_order)
mcp.tool()(api.cancel_limit_order)
mcp.tool()(api.cancel_limit_orders)
mcp.tool()(api.get_limit_orders)


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
    """Main entry point for the Jupiter MCP server."""
    print("🚀 Jupiter MCP Server")
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
    print("")
    print("  💱 Jupiter Ultra API (Immediate Swaps):")
    print("    • get_swap_quote - Get swap quotes and unsigned transactions (FREE)")
    print("    • execute_swap_transaction - Sign and execute swap transactions (PAID)")
    print("    • get_balances - Get wallet token balances (FREE)")
    print("    • get_shield - Get token security information (FREE)")
    print("    • search_token - Search for tokens (FREE)")
    print("")
    print("  📊 Jupiter Trigger API (Limit Orders):")
    print("    • create_limit_order - Create limit order transactions (FREE)")
    print("    • execute_limit_order - Sign and execute limit orders (PAID)")
    print("    • cancel_limit_order - Cancel a single limit order (FREE)")
    print("    • cancel_limit_orders - Cancel multiple limit orders (FREE)")
    print("    • get_limit_orders - Get active/historical limit orders (FREE)")
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
