#!/usr/bin/env python3
"""
Jupiter MCP Server

This module provides an MCP server for interacting with the Jupiter APIs.
"""

import os
from typing import Any

import click
from fastmcp import FastMCP

from .jupiter_api import JupiterAPI


def setup_server(client_side_mode: bool = False) -> tuple[Any, JupiterAPI]:
    """Setup the MCP server and Jupiter API client."""
    # Check if client-side mode is enabled via environment variable (fallback)
    if not client_side_mode:
        client_side_mode = os.getenv("CLIENT_SIDE_MODE", "false").lower() in (
            "true",
            "1",
            "yes",
        )

    # Create the FastMCP server instance
    mcp = FastMCP("Jupiter MCP Server")  # type: ignore

    # Initialize the Jupiter API client
    api = JupiterAPI(client_side_mode=client_side_mode)

    # Register all API methods as MCP tools using the clean pattern
    # Phase 1: Ultra API tools (immediate swaps)
    mcp.tool()(api.get_swap_quote)
    mcp.tool()(api.execute_swap_transaction)
    mcp.tool()(api.get_balances)
    mcp.tool()(api.get_shield)
    mcp.tool()(api.search_token)

    # Phase 1a: Client-side transaction handling
    mcp.tool()(api.build_raw_swap_tx)
    mcp.tool()(api.submit_signed_transaction)

    # Phase 2: Trigger API tools (limit orders)
    mcp.tool()(api.create_limit_order)
    mcp.tool()(api.execute_limit_order)
    mcp.tool()(api.cancel_limit_order)
    mcp.tool()(api.cancel_limit_orders)
    mcp.tool()(api.get_limit_orders)

    @mcp.resource("wallet://info")  # type: ignore
    def get_wallet_info() -> str:  # type: ignore
        """Get information about the configured wallet."""
        info = api.get_wallet_info()
        if "error" in info:
            return f"Error: {info['error']}"

        if info.get("client_side_mode") == "true":
            return f"""
Wallet Configuration:
- Mode: Client-side (wallet address managed externally)
- Network: {info['network']}
- RPC URL: {info['rpc_url']}
- Message: {info['message']}
"""
        else:
            return f"""
Wallet Configuration:
- Address: {info['wallet_address']}
- Network: {info['network']}
- RPC URL: {info['rpc_url']}
"""

    return mcp, api  # type: ignore


@click.command()
@click.option(
    "--client-side",
    is_flag=True,
    default=False,
    help="Enable client-side mode (disable server-side transaction signing)",
)
@click.option(
    "--host",
    default="localhost",
    help="Host to bind the server to (default: localhost)",
)
@click.option(
    "--port",
    default=None,
    type=int,
    help="Port to bind the server to (default: auto-select)",
)
def main(client_side: bool, host: str, port: int | None):
    """
    Jupiter MCP Server - Model Context Protocol server for Jupiter Ultra and Trigger APIs.

    This server provides tools to interact with Jupiter's swap and limit order APIs.

    \b
    Modes:
    • Server-side mode (default): Private key managed by server, all operations available
    • Client-side mode (--client-side): External wallet management, enhanced security

    \b
    Client-side mode benefits:
    • Private keys never leave your client
    • Enhanced security for sensitive operations
    • Compatible with hardware wallets and external signers

    \b
    Examples:
      # Start in server-side mode (traditional)
      jupiter-mcp

      # Start in client-side mode (secure)
      jupiter-mcp --client-side

      # Start with custom host/port
      jupiter-mcp --host 0.0.0.0 --port 8080
    """
    # Setup the server with the specified mode
    mcp, api = setup_server(client_side_mode=client_side)

    print("🚀 Jupiter MCP Server")
    print("=" * 50)
    print("")
    print("🔗 Connection Details:")
    print(f"  Network: {api.network}")
    print(f"  RPC URL: {api.rpc_url}")
    print(f"  Client-side mode: {'✅ Enabled' if client_side else '❌ Disabled'}")
    if host != "localhost" or port is not None:
        print(f"  Host: {host}")
        if port:
            print(f"  Port: {port}")
    print("")

    # Get wallet info
    wallet_info = api.get_wallet_info()
    if wallet_info.get("client_side_mode") == "true":
        print("💳 Wallet: Client-side mode (external wallet management)")
    elif wallet_info.get("wallet_address"):
        print(f"💳 Wallet: {wallet_info['wallet_address']}")
    else:
        print("⚠️  No wallet configured")

    print("")
    print("🛠️  Available Tools:")
    print("")
    print("  💱 Jupiter Ultra API (Immediate Swaps):")
    print("    • get_swap_quote - Get swap quotes and unsigned transactions (FREE)")
    if client_side:
        print(
            "    • build_raw_swap_tx - Build unsigned transactions for client-side signing (FREE)"
        )
        print("    • submit_signed_transaction - Submit pre-signed transactions (PAID)")
        print("    ⚠️  execute_swap_transaction - DISABLED in client-side mode")
    else:
        print(
            "    • execute_swap_transaction - Sign and execute swap transactions (PAID)"
        )
    print("    • get_balances - Get wallet token balances (FREE)")
    print("    • get_shield - Get token security information (FREE)")
    print("    • search_token - Search for tokens (FREE)")
    print("")
    print("  📊 Jupiter Trigger API (Limit Orders):")
    print("    • create_limit_order - Create limit order transactions (FREE)")
    if client_side:
        print("    ⚠️  execute_limit_order - DISABLED in client-side mode")
        print(
            "    💡 Use submit_signed_transaction for limit orders in client-side mode"
        )
    else:
        print("    • execute_limit_order - Sign and execute limit orders (PAID)")
    print("    • cancel_limit_order - Cancel a single limit order (FREE)")
    print("    • cancel_limit_orders - Cancel multiple limit orders (FREE)")
    print("    • get_limit_orders - Get active/historical limit orders (FREE)")
    print("")
    print("📋 Available Resources:")
    print("  • wallet://info - Get wallet configuration details")
    print("")
    if client_side:
        print("🔐 Client-side mode: Private keys are managed externally for security")
        print(
            "💡 Use build_raw_* methods + client-side signing + submit_signed_transaction"
        )
        print("")
        print("🔄 Typical client-side workflow:")
        print("  1. build_raw_swap_tx → get unsigned transaction")
        print("  2. Sign transaction with your external wallet/hardware device")
        print("  3. submit_signed_transaction → execute on blockchain")
    print("")
    print("🔥 Server is ready! Connect with your MCP client.")
    print("")

    # Run the server with custom host/port if specified
    if host != "localhost" or port is not None:
        # For FastMCP, we'll run with default settings since it handles its own server setup
        # The host/port options are shown for future extensibility
        print("💡 Note: Custom host/port settings displayed for reference.")
        print("   FastMCP handles its own server configuration.")
        print("")

    # Run the server
    mcp.run()


# For backward compatibility when importing directly from server
# Create default instances that can be imported
mcp, api = setup_server(client_side_mode=False)

if __name__ == "__main__":
    main()
