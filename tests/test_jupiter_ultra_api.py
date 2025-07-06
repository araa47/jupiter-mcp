#!/usr/bin/env python3
"""
Unit Tests for Jupiter Ultra API Client

Tests the API methods directly without MCP server overhead.
"""

import os
import sys
from typing import Any, Generator
from unittest.mock import patch

import pytest

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jupiter_ultra_api import JupiterUltraAPI


class TestJupiterUltraAPI:
    """Test suite for Jupiter Ultra API client."""

    @pytest.fixture
    def api(self) -> JupiterUltraAPI:
        """Create a test API client."""
        return JupiterUltraAPI()

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
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_balances with a valid wallet address."""
        # Test with a known devnet address (doesn't require our private key)
        test_address = "11111111111111111111111111111112"

        result = await api.get_balances(wallet_address=test_address)

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_sol(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test search_token functionality with SOL."""
        result = await api.search_token(query="SOL")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_by_mint(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test search_token functionality with a known mint address."""
        # SOL mint address
        sol_mint = "So11111111111111111111111111111111111111112"

        result = await api.search_token(query=sol_mint)

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_shield_sol_usdc(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_shield functionality with SOL and USDC."""
        # SOL and USDC mint addresses
        mints = "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

        result = await api.get_shield(mints=mints)

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_order_real_quote(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_order with real API call (no cost - just getting a quote)."""
        result = await api.get_order(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount="100000",  # 0.0001 SOL (very small for safety)
        )

        assert result is not None
        assert isinstance(result, dict)
        # Should contain either success or error
        assert "success" in result or "error" in result

    @pytest.mark.asyncio
    async def test_execute_order_mock_response(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test execute_order with mocked HTTP response."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "sign_transaction") as mock_sign,
        ):
            mock_request.return_value = {
                "status": "Success",
                "signature": "mock-signature",
                "slot": "12345",
            }
            mock_sign.return_value = "mock-signed-transaction-base64"

            result = await api.execute_order(
                transaction="mock-unsigned-transaction-base64",
                request_id="mock-request-id",
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_error_handling_invalid_params(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test error handling with invalid parameters."""
        # Test with invalid mint address (empty string)
        result = await api.search_token(query="")

        # Should handle gracefully and return error
        assert result is not None
        assert isinstance(result, dict)

    def test_get_wallet_info_no_private_key(self, api: JupiterUltraAPI) -> None:
        """Test get_wallet_info when no private key is set."""
        with patch.dict(os.environ, {}, clear=True):
            api.reset_cached_clients()  # Reset cached keypair
            api.private_key = None

            result = api.get_wallet_info()

            assert result is not None
            assert isinstance(result, dict)
            assert "error" in result

    def test_get_wallet_info_valid_config(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_wallet_info with valid configuration."""
        with patch.object(api, "get_keypair") as mock_keypair:
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = api.get_wallet_info()

            assert result is not None
            assert isinstance(result, dict)
            assert "wallet_address" in result
            assert "network" in result
            assert "rpc_url" in result


# PAID TESTS - These require actual SOL for transactions
# Only run with --run-paid-tests flag


class TestJupiterUltraAPIPaid:
    """Paid test suite that requires actual SOL for transactions."""

    @pytest.fixture
    def api(self) -> JupiterUltraAPI:
        """Create a test API client."""
        return JupiterUltraAPI()

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
        self, api: JupiterUltraAPI, real_env_vars: Any
    ) -> None:
        """Test get_balances with real wallet."""
        result = await api.get_balances()

        assert result is not None
        assert isinstance(result, dict)
        # Should return actual balance data
        assert "success" in result or "error" in result

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_order_creation(
        self, api: JupiterUltraAPI, real_env_vars: Any
    ) -> None:
        """Test creating a real order (no execution)."""
        print("\n🔄 Testing real order creation...")
        result = await api.get_order(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount="500000",  # 0.0005 SOL (reduced for mainnet safety)
        )

        assert result is not None
        assert isinstance(result, dict)
        print(f"Order result: {result}")

        # Should contain either success or error
        assert "success" in result or "error" in result

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_shield_check(
        self, api: JupiterUltraAPI, real_env_vars: Any
    ) -> None:
        """Test shield check with real tokens."""
        # Check SOL and USDC
        result = await api.get_shield(
            mints="So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result or "error" in result
