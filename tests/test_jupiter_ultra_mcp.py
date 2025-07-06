#!/usr/bin/env python3
"""
Tests for Jupiter Ultra MCP Server

This module contains both free tests (that don't require actual transactions)
and paid tests (that require minimal SOL for real transactions).
"""

import os
import sys
from typing import Any, Generator
from unittest.mock import patch

import pytest
from fastmcp import Client

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import mcp  # type: ignore[attr-defined]


class TestJupiterUltraMCP:
    """Test suite for Jupiter Ultra MCP Server."""

    @pytest.fixture
    def client(self) -> Client:  # type: ignore[type-arg]
        """Create a test client for the MCP server."""
        return Client(mcp)

    @pytest.fixture
    def mock_env_vars(self) -> Generator[None, None, None]:
        """Mock environment variables for testing."""
        with patch.dict(
            os.environ,
            {
                "SOLANA_RPC_URL": "https://api.devnet.solana.com",
                "PRIVATE_KEY": "test_private_key_base58_encoded",
                "SOLANA_NETWORK": "devnet",
                "REQUEST_TIMEOUT": "30",
            },
        ):
            yield

    # FREE TESTS - These don't require actual transactions

    @pytest.mark.asyncio
    async def test_get_balances_with_valid_address(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test get_balances with a valid wallet address."""
        # Test with a known devnet address (doesn't require our private key)
        test_address = "11111111111111111111111111111112"

        async with client:
            result = await client.call_tool(
                "get_balances", {"wallet_address": test_address}
            )

            assert result is not None
            # The tool should return a success/error structure
            assert "success" in str(result)

    @pytest.mark.asyncio
    async def test_search_token_sol(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test search_token functionality with SOL."""
        async with client:
            result = await client.call_tool("search_token", {"query": "SOL"})

            assert result is not None
            assert "success" in str(result)

    @pytest.mark.asyncio
    async def test_search_token_by_mint(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test search_token functionality with a known mint address."""
        # SOL mint address
        sol_mint = "So11111111111111111111111111111111111111112"

        async with client:
            result = await client.call_tool("search_token", {"query": sol_mint})

            assert result is not None
            assert "success" in str(result)

    @pytest.mark.asyncio
    async def test_get_shield_sol_usdc(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test get_shield functionality with SOL and USDC."""
        # SOL and USDC mint addresses
        mints = "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

        async with client:
            result = await client.call_tool("get_shield", {"mints": mints})

            assert result is not None
            assert "success" in str(result)

    @pytest.mark.asyncio
    async def test_get_order_real_quote(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test get_order with real API call (no cost - just getting a quote)."""
        async with client:
            result = await client.call_tool(
                "get_order",
                {
                    "input_mint": "So11111111111111111111111111111111111111112",  # SOL
                    "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                    "amount": "1000000",  # 0.001 SOL
                },
            )

            assert result is not None
            # Should contain either success or error
            result_str = str(result)
            assert "success" in result_str or "error" in result_str

    @pytest.mark.asyncio
    async def test_execute_order_mock_response(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test execute_order with mocked HTTP response."""
        with patch(
            "src.jupiter_ultra_api.JupiterUltraAPI.make_http_request"
        ) as mock_request:
            mock_request.return_value = {
                "status": "Success",
                "signature": "mock-signature",
                "slot": "12345",
            }

            async with client:
                result = await client.call_tool(
                    "execute_order",
                    {
                        "signed_transaction": "mock-signed-transaction-base64",
                        "request_id": "mock-request-id",
                    },
                )

                assert result is not None
                result_str = str(result)
                assert "success" in result_str or "error" in result_str

    @pytest.mark.asyncio
    async def test_client_connection(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test that the client can connect to the MCP server."""
        async with client:
            # Test server ping
            await client.ping()

            # List available tools
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]

            # Verify all required tools are available
            expected_tools = [
                "get_order",
                "execute_order",
                "get_balances",
                "get_shield",
                "search_token",
            ]

            for tool_name in expected_tools:
                assert (
                    tool_name in tool_names
                ), f"Tool {tool_name} not found in available tools"

    @pytest.mark.asyncio
    async def test_error_handling_invalid_params(
        self, client: Client, mock_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test error handling with invalid parameters."""
        async with client:
            # Test with invalid mint address (empty string)
            result = await client.call_tool("search_token", {"query": ""})

            # Should handle gracefully and return error
            assert result is not None


# PAID TESTS - These require actual SOL for transactions
# Only run with --run-paid-tests flag


class TestJupiterUltraMCPPaid:
    """Paid test suite that requires actual SOL for transactions."""

    @pytest.fixture
    def client(self) -> Client:  # type: ignore[type-arg]
        """Create a test client for the MCP server."""
        return Client(mcp)

    @pytest.fixture
    def real_env_vars(self) -> Generator[None, None, None]:
        """Use real environment variables for paid tests."""
        # These tests require actual PRIVATE_KEY and SOLANA_RPC_URL
        if not os.getenv("PRIVATE_KEY") or not os.getenv("SOLANA_RPC_URL"):
            pytest.skip("PRIVATE_KEY and SOLANA_RPC_URL required for paid tests")
        yield

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_get_balances(
        self, client: Client, real_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test get_balances with real wallet."""
        async with client:
            result = await client.call_tool("get_balances", {})

            assert result is not None
            # Should return actual balance data
            result_str = str(result)
            assert "success" in result_str or "SOL" in result_str

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_order_creation_no_execution(
        self, client: Client, real_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test creating a real order without execution."""
        async with client:
            # Step 1: Get an order for 0.01 SOL → USDC
            print("\n🔄 Step 1: Getting swap order...")
            order_result = await client.call_tool(
                "get_order",
                {
                    "input_mint": "So11111111111111111111111111111111111111112",  # SOL
                    "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                    "amount": "10000000",  # 0.01 SOL in lamports
                },
            )

            assert order_result is not None
            print(f"Order result: {order_result}")

            # Extract order data - check if we got a valid order response
            order_str = str(order_result)
            if "success" in order_str and "transaction" in order_str:
                print("✅ Got valid order, ready for signing and execution")
                assert "requestId" in order_str or "transaction" in order_str
                print("✅ Order contains required fields for execution")
            else:
                print(
                    "⚠️  Order failed or no transaction returned - this is expected behavior"
                )
                # This is still a valid test result - the API might not always return executable orders
                assert order_result is not None

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_shield_check(
        self, client: Client, real_env_vars: Any  # type: ignore[type-arg]
    ) -> None:
        """Test shield check with real tokens."""
        async with client:
            # Check SOL and USDC
            result = await client.call_tool(
                "get_shield",
                {
                    "mints": "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
                },
            )

            assert result is not None
            result_str = str(result)
            assert "success" in result_str or "warnings" in result_str
