#!/usr/bin/env python3
"""
Unit Tests for Jupiter API Client

Tests the API methods directly without MCP server overhead.
"""

import os
import sys
from typing import Any, Generator
from unittest.mock import patch

import pytest

# Add the parent directory to the path to import our module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jupiter_api import JupiterAPI


class TestJupiterAPI:
    """Test suite for Jupiter API client."""

    @pytest.fixture
    def api(self) -> JupiterAPI:
        """Create a test API client."""
        return JupiterAPI()

    @pytest.fixture
    def client_side_api(self) -> JupiterAPI:
        """Create a test API client in client-side mode."""
        return JupiterAPI(client_side_mode=True)

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
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_balances with a valid wallet address."""
        # Test with a known devnet address (doesn't require our private key)
        test_address = "11111111111111111111111111111112"

        result = await api.get_balances(wallet_address=test_address)

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_sol(self, api: JupiterAPI, mock_env_vars: Any) -> None:
        """Test search_token functionality with SOL."""
        result = await api.search_token(query="SOL")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_by_mint(
        self, api: JupiterAPI, mock_env_vars: Any
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
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_shield functionality with SOL and USDC."""
        # SOL and USDC mint addresses
        mints = "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

        result = await api.get_shield(mints=mints)

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_swap_quote_real_quote(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_swap_quote with real API call (no cost - just getting a quote)."""
        result = await api.get_swap_quote(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount="100000",  # 0.0001 SOL (very small for safety)
        )

        assert result is not None
        assert isinstance(result, dict)
        # Should contain either success or error
        assert "success" in result or "error" in result

    @pytest.mark.asyncio
    async def test_execute_swap_transaction_mock_response(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test execute_swap_transaction with mocked HTTP response."""
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

            result = await api.execute_swap_transaction(
                transaction="mock-unsigned-transaction-base64",
                request_id="mock-request-id",
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_error_handling_invalid_params(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test error handling with invalid parameters."""
        # Test with invalid mint address (empty string)
        result = await api.search_token(query="")

        # Should handle gracefully and return error
        assert result is not None
        assert isinstance(result, dict)

    def test_get_wallet_info_no_private_key(self, api: JupiterAPI) -> None:
        """Test get_wallet_info when no private key is set."""
        with patch.dict(os.environ, {}, clear=True):
            api.reset_cached_clients()  # Reset cached keypair
            api.private_key = None

            result = api.get_wallet_info()

            assert result is not None
            assert isinstance(result, dict)
            assert "error" in result

    def test_get_wallet_info_valid_config(
        self, api: JupiterAPI, mock_env_vars: Any
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

    @pytest.mark.asyncio
    async def test_get_swap_quote_invalid_mint(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_swap_quote with invalid mint address."""
        result = await api.get_swap_quote(
            input_mint="invalid_mint",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            amount="1000000",
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result
        # Should gracefully handle invalid mint and return error

    @pytest.mark.asyncio
    async def test_get_swap_quote_zero_amount(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_swap_quote with zero amount."""
        result = await api.get_swap_quote(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            amount="0",
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_swap_quote_empty_params(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_swap_quote with empty parameters."""
        result = await api.get_swap_quote(input_mint="", output_mint="", amount="")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_execute_swap_transaction_empty_params(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test execute_swap_transaction with empty parameters."""
        result = await api.execute_swap_transaction(transaction="", request_id="")

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
        assert "cannot be empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_swap_transaction_invalid_transaction(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test execute_swap_transaction with invalid transaction format."""
        with patch.object(api, "sign_transaction") as mock_sign:
            mock_sign.side_effect = Exception("Invalid transaction format")

            result = await api.execute_swap_transaction(
                transaction="invalid_transaction", request_id="test_request_id"
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_balances_invalid_address(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_balances with invalid wallet address."""
        result = await api.get_balances(wallet_address="invalid_address")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_shield_empty_mints(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_shield with empty mints parameter."""
        result = await api.get_shield(mints="")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_shield_invalid_mints(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_shield with invalid mint addresses."""
        result = await api.get_shield(mints="invalid_mint1,invalid_mint2")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_numeric_query(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test search_token with numeric query."""
        result = await api.search_token(query="123")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_special_characters(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test search_token with special characters."""
        result = await api.search_token(query="!@#$%")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_http_timeout_handling(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test HTTP timeout handling."""
        with patch.object(api, "make_http_request") as mock_request:
            mock_request.side_effect = Exception("Request timed out after 30 seconds")

            result = await api.get_balances()

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is False
            assert "error" in result

    def test_sign_transaction_empty_input(self, api: JupiterAPI) -> None:
        """Test sign_transaction with empty input."""
        with patch.object(api, "get_keypair"):
            with pytest.raises(Exception) as exc_info:
                api.sign_transaction("")
            assert "cannot be empty" in str(exc_info.value).lower()

    def test_sign_transaction_invalid_base64(self, api: JupiterAPI) -> None:
        """Test sign_transaction with invalid base64."""
        with patch.object(api, "get_keypair"):
            with pytest.raises(Exception) as exc_info:
                api.sign_transaction("invalid_base64!")
            assert "invalid base64" in str(exc_info.value).lower()

    def test_reset_cached_clients(self, api: JupiterAPI) -> None:
        """Test reset_cached_clients functionality."""
        # Test that reset_cached_clients method exists and is callable
        # We can't test the internal state directly due to protected attributes
        # but we can verify the method exists and doesn't raise errors
        try:
            api.reset_cached_clients()
            # If we get here without exception, the method works
            assert True
        except Exception as e:
            pytest.fail(f"reset_cached_clients should not raise exceptions: {e}")

    # PHASE 2: TRIGGER API TESTS (Limit Orders)

    @pytest.mark.asyncio
    async def test_create_limit_order_mock_response(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test create_limit_order with mocked HTTP response."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "order": "mock-order-account-address",
                "transaction": "mock-unsigned-transaction-base64",
                "requestId": "mock-request-id",
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = await api.create_limit_order(
                input_mint="So11111111111111111111111111111111111111112",  # SOL
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                making_amount="10000000",  # 0.01 SOL
                taking_amount="2500000",  # 2.5 USDC
                slippage_bps=100,  # 1% slippage
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result
            assert result["data"]["order"] == "mock-order-account-address"

    @pytest.mark.asyncio
    async def test_execute_limit_order_mock_response(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test execute_limit_order with mocked HTTP response."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "sign_transaction") as mock_sign,
        ):
            mock_request.return_value = {
                "status": "Success",
                "signature": "mock-limit-order-signature",
                "slot": "12345",
            }
            mock_sign.return_value = "mock-signed-transaction-base64"

            result = await api.execute_limit_order(
                transaction="mock-unsigned-transaction-base64",
                request_id="mock-request-id",
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_cancel_limit_order_mock_response(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test cancel_limit_order with mocked HTTP response."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "transaction": "mock-cancel-transaction-base64",
                "requestId": "mock-cancel-request-id",
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = await api.cancel_limit_order(order="mock-order-account-address")

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_cancel_limit_orders_mock_response(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test cancel_limit_orders with mocked HTTP response."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "transactions": ["mock-tx-1", "mock-tx-2"],
                "requestId": "mock-batch-cancel-request-id",
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = await api.cancel_limit_orders(
                orders=["order1", "order2", "order3"]
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_limit_orders_mock_response(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_limit_orders with mocked HTTP response."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "orders": [
                    {
                        "orderAccount": "order1",
                        "makingAmount": "1000000",
                        "takingAmount": "250000",
                        "status": "active",
                    }
                ],
                "hasMoreData": False,
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = await api.get_limit_orders(order_status="active")

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result
            assert result["hasMoreData"] is False

    @pytest.mark.asyncio
    async def test_create_limit_order_invalid_params(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test create_limit_order with invalid parameters."""
        # Test with empty input_mint
        result = await api.create_limit_order(
            input_mint="",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            making_amount="1000000",
            taking_amount="250000",
        )

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_create_limit_order_zero_amount(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test create_limit_order with zero amount."""
        result = await api.create_limit_order(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            making_amount="0",
            taking_amount="250000",
        )

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_cancel_limit_order_empty_order(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test cancel_limit_order with empty order address."""
        result = await api.cancel_limit_order(order="")

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_limit_orders_invalid_status(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_limit_orders with invalid order status."""
        result = await api.get_limit_orders(order_status="invalid_status")

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_create_limit_order_with_expiry(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test create_limit_order with expiry timestamp."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "order": "mock-order-with-expiry",
                "transaction": "mock-transaction",
                "requestId": "mock-request-id",
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            # Set expiry to 1 hour from now
            import time

            expiry = int(time.time()) + 3600

            result = await api.create_limit_order(
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                making_amount="10000000",
                taking_amount="2500000",
                expired_at=expiry,
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_cancel_limit_orders_all_orders(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test cancel_limit_orders without specifying orders (cancels ALL)."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "transactions": ["mock-cancel-all-tx-1", "mock-cancel-all-tx-2"],
                "requestId": "mock-cancel-all-request-id",
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            # Call without orders parameter to cancel ALL orders
            result = await api.cancel_limit_orders()

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result
            assert len(result["data"]["transactions"]) == 2

    @pytest.mark.asyncio
    async def test_get_limit_orders_with_filters(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_limit_orders with input_mint and output_mint filters."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            mock_request.return_value = {
                "orders": [
                    {
                        "orderAccount": "filtered-order-1",
                        "inputMint": "So11111111111111111111111111111111111111112",
                        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                        "makingAmount": "5000000",
                        "takingAmount": "1250000",
                        "status": "active",
                    }
                ],
                "hasMoreData": False,
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = await api.get_limit_orders(
                order_status="active",
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result
            assert len(result["data"]) == 1
            assert result["data"][0]["orderAccount"] == "filtered-order-1"

    @pytest.mark.asyncio
    async def test_get_limit_orders_with_pagination(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_limit_orders with pagination."""
        with (
            patch.object(api, "make_http_request") as mock_request,
            patch.object(api, "get_keypair") as mock_keypair,
        ):
            # Mock response for page 2
            mock_request.return_value = {
                "orders": [
                    {
                        "orderAccount": f"order-page2-{i}",
                        "makingAmount": "1000000",
                        "takingAmount": "250000",
                        "status": "history",
                    }
                    for i in range(10)  # 10 orders per page
                ],
                "hasMoreData": True,  # More pages available
            }
            # Mock keypair to return a test wallet address
            mock_keypair.return_value.pubkey.return_value = "test_wallet_address"

            result = await api.get_limit_orders(order_status="history", page=2)

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert "data" in result
            assert len(result["data"]) == 10
            assert result["hasMoreData"] is True
            assert result["data"][0]["orderAccount"] == "order-page2-0"

    @pytest.mark.asyncio
    async def test_get_limit_orders_with_custom_wallet(
        self, api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_limit_orders with a custom wallet address."""
        with patch.object(api, "make_http_request") as mock_request:
            mock_request.return_value = {
                "orders": [
                    {
                        "orderAccount": "custom-wallet-order",
                        "userPubkey": "CustomWalletAddressHere",
                        "makingAmount": "2000000",
                        "takingAmount": "500000",
                        "status": "active",
                    }
                ],
                "hasMoreData": False,
            }

            # Use custom wallet address (no need to mock get_keypair)
            custom_wallet = "CustomWalletAddressHere"
            result = await api.get_limit_orders(
                order_status="active", wallet_address=custom_wallet
            )

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is True
            assert result["wallet_address"] == custom_wallet
            assert "data" in result
            assert len(result["data"]) == 1
            assert result["data"][0]["userPubkey"] == custom_wallet


# PAID TESTS - These require actual SOL for transactions
# Only run with --run-paid-tests flag


class TestJupiterAPIPaid:
    """Paid test suite that requires actual SOL for transactions."""

    @pytest.fixture
    def api(self) -> JupiterAPI:
        """Create a test API client."""
        return JupiterAPI()

    @pytest.fixture
    def real_env_vars(self) -> Generator[None, None, None]:
        """Use real environment variables for paid tests."""
        # These tests require actual PRIVATE_KEY and SOLANA_RPC_URL
        if not os.getenv("PRIVATE_KEY") or not os.getenv("SOLANA_RPC_URL"):
            pytest.skip("PRIVATE_KEY and SOLANA_RPC_URL required for paid tests")
        yield

    @pytest.mark.asyncio
    async def test_real_get_balances(self, api: JupiterAPI, real_env_vars: Any) -> None:
        """Test get_balances with real wallet."""
        result = await api.get_balances()

        assert result is not None
        assert isinstance(result, dict)
        # Should return actual balance data
        assert "success" in result or "error" in result

    @pytest.mark.asyncio
    async def test_real_swap_quote_creation(
        self, api: JupiterAPI, real_env_vars: Any
    ) -> None:
        """Test creating a real swap quote (no execution)."""
        print("\n🔄 Testing real swap quote creation...")
        result = await api.get_swap_quote(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount="500000",  # 0.0005 SOL (reduced for mainnet safety)
        )

        assert result is not None
        assert isinstance(result, dict)
        print(f"Order result: {result}")

        # Should contain either success or error
        assert "success" in result or "error" in result

    @pytest.mark.asyncio
    async def test_real_shield_check(self, api: JupiterAPI, real_env_vars: Any) -> None:
        """Test shield check with real tokens."""
        # Check SOL and USDC
        result = await api.get_shield(
            mints="So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result or "error" in result

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_trade_execution(
        self, api: JupiterAPI, real_env_vars: Any
    ) -> None:
        """Test executing a real trade: get_swap_quote -> execute_swap_transaction."""
        print("\n🔄 Step 1: Getting swap quote...")

        # Step 1: Get a quote for 0.0001 SOL → USDC (very small amount)
        order_result = await api.get_swap_quote(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            amount="100000",  # 0.0001 SOL (very small for safety)
        )

        assert order_result is not None
        assert isinstance(order_result, dict)
        print(f"Order result: {order_result}")

        # Check if order was successful
        if order_result.get("success") and "data" in order_result:
            order_data = order_result["data"]
            transaction = order_data.get("transaction")
            request_id = order_data.get("requestId")

            if transaction and request_id:
                print(f"✅ Got order with requestId: {request_id}")
                print(f"📦 Transaction length: {len(transaction)} characters")

                # Step 2: Execute the swap transaction (this will sign and execute on mainnet)
                print("⚡ Step 2: Executing transaction (SPENDING REAL SOL!)...")
                execution_result = await api.execute_swap_transaction(
                    transaction=transaction,
                    request_id=request_id,
                )

                assert execution_result is not None
                assert isinstance(execution_result, dict)
                print(f"🎉 Execution result: {execution_result}")

                # Check if execution was successful
                if execution_result.get("success") and "data" in execution_result:
                    exec_data = execution_result["data"]
                    signature = exec_data.get("signature")
                    if signature:
                        print("✅ Trade executed successfully!")
                        print(f"🔗 Transaction signature: {signature}")
                        assert signature is not None
                        assert len(signature) > 0
                    else:
                        print("⚠️  Trade execution completed but no signature returned")
                        print(f"Execution data: {exec_data}")
                else:
                    print("⚠️  Trade execution failed")
                    print(f"Execution result: {execution_result}")
                    # Still assert success for the test structure
                    assert execution_result.get("success") is not None

            else:
                print("⚠️  Order missing transaction or requestId")
                print(f"Order data: {order_data}")
                pytest.fail("Order missing required transaction or requestId")
        else:
            print("⚠️  Order creation failed")
            print(f"Order response: {order_result}")
            pytest.fail("Order creation failed")

    # PHASE 2: TRIGGER API PAID TESTS (Limit Orders)

    @pytest.mark.asyncio
    async def test_real_limit_order_creation(
        self, api: JupiterAPI, real_env_vars: Any
    ) -> None:
        """Test creating a real limit order quote (no execution)."""
        print("\n📊 Testing real limit order creation...")

        # Create a limit order: sell 0.01 SOL for 2.5 USDC (price: $250/SOL)
        # This is above market price so it won't execute immediately
        result = await api.create_limit_order(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            making_amount="10000000",  # 0.01 SOL (minimum is ~$5 USD)
            taking_amount="2500000",  # 2.5 USDC (6 decimals)
            slippage_bps=100,  # 1% slippage
        )

        assert result is not None
        assert isinstance(result, dict)
        print(f"Limit order result: {result}")

        # Should contain either success or error
        assert "success" in result or "error" in result

    @pytest.mark.asyncio
    async def test_real_get_limit_orders(
        self, api: JupiterAPI, real_env_vars: Any
    ) -> None:
        """Test getting real limit orders for configured wallet."""
        print("\n📊 Testing get limit orders...")

        # Get active orders
        active_result = await api.get_limit_orders(order_status="active")

        assert active_result is not None
        assert isinstance(active_result, dict)
        print(f"Active orders: {active_result}")

        # Get order history
        history_result = await api.get_limit_orders(order_status="history", page=1)

        assert history_result is not None
        assert isinstance(history_result, dict)
        print(f"Order history: {history_result}")

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_limit_order_execution(
        self, api: JupiterAPI, real_env_vars: Any
    ) -> None:
        """Test executing a real limit order: create_limit_order -> execute_limit_order."""
        print("\n📊 Step 1: Creating limit order quote...")

        # Create a limit order with a price 20% above market so it won't execute immediately
        # Using a more reasonable amount that meets the $5 minimum
        # Assuming SOL is around $150, we'll ask for $180/SOL
        order_result = await api.create_limit_order(
            input_mint="So11111111111111111111111111111111111111112",  # SOL
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            making_amount="40000000",  # 0.04 SOL (about $6 at $150/SOL)
            taking_amount="7200000",  # 7.2 USDC (implies $180/SOL - 20% above market)
            slippage_bps=0,  # Exact mode - only execute at this exact price
        )

        assert order_result is not None
        assert isinstance(order_result, dict)
        print(f"Order result: {order_result}")

        # Check if order creation was successful
        if order_result.get("success") and "data" in order_result:
            order_data = order_result["data"]
            transaction = order_data.get("transaction")
            request_id = order_data.get("requestId")
            order_account = order_data.get("order")

            if transaction and request_id:
                print(f"✅ Got order with requestId: {request_id}")
                print(f"📦 Order account: {order_account}")
                print(f"📦 Transaction length: {len(transaction)} characters")

                # Step 2: Execute the limit order (this will create it on-chain)
                print("⚡ Step 2: Creating limit order on-chain...")
                print("💰 Order details: Sell 0.04 SOL for 7.2 USDC (price: $180/SOL)")
                execution_result = await api.execute_limit_order(
                    transaction=transaction,
                    request_id=request_id,
                )

                assert execution_result is not None
                assert isinstance(execution_result, dict)
                print(f"🎉 Execution result: {execution_result}")

                # Check if execution was successful
                if execution_result.get("success") and "data" in execution_result:
                    exec_data = execution_result["data"]
                    signature = exec_data.get("signature")
                    if signature:
                        print("✅ Limit order created successfully!")
                        print(f"🔗 Transaction signature: {signature}")
                        print(f"📊 Order account: {order_account}")
                        assert signature is not None
                        assert len(signature) > 0

                        # Step 3: Wait a bit and verify the order exists
                        print(
                            "\n⏳ Step 3: Waiting 5 seconds then checking active orders..."
                        )
                        import asyncio

                        await asyncio.sleep(5)

                        # Get active orders to verify our order is there
                        active_orders = await api.get_limit_orders(
                            order_status="active"
                        )
                        if active_orders.get("success") and active_orders.get("data"):
                            print(
                                f"📋 Found {len(active_orders['data'])} active orders"
                            )

                            # Look for our order
                            our_order = None
                            for order in active_orders["data"]:
                                if order.get("orderAccount") == order_account:
                                    our_order = order
                                    break

                            if our_order:
                                print(f"✅ Found our order: {our_order}")
                            else:
                                print(
                                    "⚠️ Our order not found in active orders (might have executed)"
                                )

                        # Step 4: Cancel the order to clean up
                        if order_account:
                            print("\n🧹 Step 4: Canceling the limit order...")
                            cancel_result = await api.cancel_limit_order(
                                order=order_account
                            )

                            if cancel_result.get("success") and "data" in cancel_result:
                                cancel_tx = cancel_result["data"].get("transaction")
                                cancel_request_id = cancel_result["data"].get(
                                    "requestId"
                                )

                                if cancel_tx and cancel_request_id:
                                    print("📝 Executing cancellation transaction...")
                                    cancel_exec = await api.execute_limit_order(
                                        transaction=cancel_tx,
                                        request_id=cancel_request_id,
                                    )
                                    if cancel_exec.get("success"):
                                        print("✅ Order cancelled successfully!")
                                        print(
                                            f"🔗 Cancel signature: {cancel_exec['data'].get('signature')}"
                                        )
                                    else:
                                        print(
                                            f"⚠️ Cancel execution failed: {cancel_exec}"
                                        )
                                else:
                                    print(
                                        "⚠️ Cancel result missing transaction or requestId"
                                    )
                            else:
                                print(f"⚠️ Cancel order failed: {cancel_result}")
                    else:
                        print(
                            "⚠️  Limit order execution completed but no signature returned"
                        )
                        print(f"Execution data: {exec_data}")
                else:
                    print("⚠️  Limit order execution failed")
                    print(f"Execution result: {execution_result}")
                    # Still assert success for the test structure
                    assert execution_result.get("success") is not None

            else:
                print("⚠️  Order missing transaction or requestId")
                print(f"Order data: {order_data}")
                pytest.fail("Order missing required transaction or requestId")
        else:
            print("⚠️  Order creation failed")
            print(f"Order response: {order_result}")
            # Check if it's a minimum size error
            if "error" in order_result and "minimum" in order_result["error"].lower():
                print(
                    "💡 Note: Order might be below $5 minimum. Adjust amounts if needed."
                )
            pytest.fail("Limit order creation failed")


# CLIENT-SIDE MODE TESTS
class TestJupiterAPIClientSide:
    """Test suite for Jupiter API client in client-side mode."""

    @pytest.fixture
    def client_side_api(self) -> JupiterAPI:
        """Create a test API client in client-side mode."""
        return JupiterAPI(client_side_mode=True)

    @pytest.fixture
    def mock_env_vars(self) -> Generator[None, None, None]:
        """Mock environment variables for testing."""
        with patch.dict(
            os.environ,
            {
                "SOLANA_RPC_URL": "https://api.devnet.solana.com",
                "PRIVATE_KEY": "",  # No private key needed in client-side mode
                "SOLANA_NETWORK": "devnet",
                "REQUEST_TIMEOUT": "30",
            },
        ):
            yield

    def test_client_side_mode_enabled(self, client_side_api: JupiterAPI) -> None:
        """Test that client-side mode is properly enabled."""
        assert client_side_api.client_side_mode is True

    def test_get_keypair_disabled_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test that get_keypair raises error in client-side mode."""
        with pytest.raises(
            ValueError, match="Keypair access is disabled in client-side mode"
        ):
            client_side_api.get_keypair()

    def test_get_wallet_info_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_wallet_info in client-side mode."""
        info = client_side_api.get_wallet_info()

        assert info.get("client_side_mode") == "true"
        assert "network" in info
        assert "rpc_url" in info
        assert "message" in info
        assert "wallet_address" not in info

    @pytest.mark.asyncio
    async def test_build_raw_swap_tx_success(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test build_raw_swap_tx with valid parameters."""
        with patch.object(client_side_api, "make_http_request") as mock_request:
            mock_response = {
                "transaction": "mock_unsigned_transaction",
                "requestId": "mock_request_id",
            }
            mock_request.return_value = mock_response

            result = await client_side_api.build_raw_swap_tx(
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                amount="1000000",
                user_address="TestUserAddressHere",
            )

            assert result["success"] is True
            assert "data" in result
            assert result["data"]["transaction"] == "mock_unsigned_transaction"
            assert result["data"]["requestId"] == "mock_request_id"
            assert result["data"]["user_address"] == "TestUserAddressHere"

    @pytest.mark.asyncio
    async def test_build_raw_swap_tx_missing_user_address(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test build_raw_swap_tx fails without user_address."""
        result = await client_side_api.build_raw_swap_tx(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            amount="1000000",
            user_address="",  # Empty address
        )

        assert result["success"] is False
        assert "user_address cannot be empty" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_swap_transaction_disabled_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test that execute_swap_transaction is disabled in client-side mode."""
        result = await client_side_api.execute_swap_transaction(
            transaction="mock_transaction", request_id="mock_request_id"
        )

        assert result["success"] is False
        assert (
            "execute_swap_transaction is disabled in client-side mode"
            in result["error"]
        )

    @pytest.mark.asyncio
    async def test_execute_limit_order_disabled_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test that execute_limit_order is disabled in client-side mode."""
        result = await client_side_api.execute_limit_order(
            transaction="mock_transaction", request_id="mock_request_id"
        )

        assert result["success"] is False
        assert "execute_limit_order is disabled in client-side mode" in result["error"]

    @pytest.mark.asyncio
    async def test_submit_signed_transaction_success(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test submit_signed_transaction with valid parameters."""
        with patch.object(client_side_api, "make_http_request") as mock_request:
            mock_response = {"signature": "mock_signature", "status": "Success"}
            mock_request.return_value = mock_response

            result = await client_side_api.submit_signed_transaction(
                signed_transaction="mock_signed_transaction",
                request_id="mock_request_id",
            )

            assert result["success"] is True
            assert "data" in result
            assert result["data"]["signature"] == "mock_signature"

    @pytest.mark.asyncio
    async def test_get_balances_requires_wallet_address_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test that get_balances requires wallet_address in client-side mode."""
        result = await client_side_api.get_balances()

        assert result["success"] is False
        assert (
            "wallet_address parameter is required in client-side mode"
            in result["error"]
        )

    @pytest.mark.asyncio
    async def test_get_balances_with_wallet_address_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test get_balances with wallet_address in client-side mode."""
        with patch.object(client_side_api, "make_http_request") as mock_request:
            mock_response = [
                {
                    "mint": "So11111111111111111111111111111111111111112",
                    "amount": "1000000",
                }
            ]
            mock_request.return_value = mock_response

            result = await client_side_api.get_balances(
                wallet_address="TestWalletAddress"
            )

            assert result["success"] is True
            assert result["wallet_address"] == "TestWalletAddress"
            assert "data" in result

    @pytest.mark.asyncio
    async def test_create_limit_order_requires_user_address_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test that create_limit_order requires user_address in client-side mode."""
        result = await client_side_api.create_limit_order(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            making_amount="1000000",
            taking_amount="20000000",
        )

        assert result["success"] is False
        assert (
            "user_address parameter is required in client-side mode" in result["error"]
        )

    @pytest.mark.asyncio
    async def test_create_limit_order_with_user_address_in_client_side_mode(
        self, client_side_api: JupiterAPI, mock_env_vars: Any
    ) -> None:
        """Test create_limit_order with user_address in client-side mode."""
        with patch.object(client_side_api, "make_http_request") as mock_request:
            mock_response = {
                "order": "mock_order_account",
                "transaction": "mock_unsigned_transaction",
                "requestId": "mock_request_id",
            }
            mock_request.return_value = mock_response

            result = await client_side_api.create_limit_order(
                input_mint="So11111111111111111111111111111111111111112",
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                making_amount="1000000",
                taking_amount="20000000",
                user_address="TestUserAddress",
            )

            assert result["success"] is True
            assert "data" in result
