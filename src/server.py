#!/usr/bin/env python3
"""
Jupiter Ultra MCP Server

A Python MCP server that provides tools to access the Jupiter Ultra API
for Solana blockchain interactions.
"""

from fastmcp import FastMCP

from .jupiter_ultra_api import JupiterUltraAPI

# Create the Jupiter Ultra API client
api = JupiterUltraAPI()

# Create the main MCP server
mcp = FastMCP(name="Jupiter Ultra MCP Server")  # type: ignore


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


# Register all API methods as tools
mcp.tool()(api.get_order)
mcp.tool()(api.execute_order)
mcp.tool()(api.get_balances)
mcp.tool()(api.get_shield)
mcp.tool()(api.search_token)


def main():
    """Main entry point for the Jupiter Ultra MCP server."""
    print("=" * 60)
    print("🚀 Jupiter Ultra MCP Server")
    print("=" * 60)

    # Get wallet info for startup display
    wallet_info = api.get_wallet_info()
    if "error" in wallet_info:
        print(f"❌ Error: {wallet_info['error']}")
        print("Please check your PRIVATE_KEY environment variable")
        return

    print(f"📡 Solana Network: {wallet_info['network']}")
    print(f"🔗 RPC URL: {wallet_info['rpc_url']}")
    print(f"💼 Wallet Address: {wallet_info['wallet_address']}")
    print("")
    print("🔧 Available Tools:")
    print("  • get_order - Get swap quotes from Jupiter Ultra")
    print("  • execute_order - Execute signed swap transactions")
    print("  • get_balances - Get token balances for a wallet")
    print("  • get_shield - Get token security information")
    print("  • search_token - Search for tokens")
    print("")
    print("📋 Available Resources:")
    print("  • wallet://info - Get wallet configuration details")
    print("")
    print("🎯 Server starting...")
    print("=" * 60)

    # Start the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
