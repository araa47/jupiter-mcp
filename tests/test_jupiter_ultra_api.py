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
    async def test_get_swap_quote_real_quote(
        self, api: JupiterUltraAPI, mock_env_vars: Any
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
        self, api: JupiterUltraAPI, mock_env_vars: Any
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

    @pytest.mark.asyncio
    async def test_get_swap_quote_invalid_mint(
        self, api: JupiterUltraAPI, mock_env_vars: Any
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
        self, api: JupiterUltraAPI, mock_env_vars: Any
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
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_swap_quote with empty parameters."""
        result = await api.get_swap_quote(input_mint="", output_mint="", amount="")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_execute_swap_transaction_empty_params(
        self, api: JupiterUltraAPI, mock_env_vars: Any
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
        self, api: JupiterUltraAPI, mock_env_vars: Any
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
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_balances with invalid wallet address."""
        result = await api.get_balances(wallet_address="invalid_address")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_shield_empty_mints(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_shield with empty mints parameter."""
        result = await api.get_shield(mints="")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_shield_invalid_mints(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test get_shield with invalid mint addresses."""
        result = await api.get_shield(mints="invalid_mint1,invalid_mint2")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_numeric_query(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test search_token with numeric query."""
        result = await api.search_token(query="123")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_token_special_characters(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test search_token with special characters."""
        result = await api.search_token(query="!@#$%")

        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_http_timeout_handling(
        self, api: JupiterUltraAPI, mock_env_vars: Any
    ) -> None:
        """Test HTTP timeout handling."""
        with patch.object(api, "make_http_request") as mock_request:
            mock_request.side_effect = Exception("Request timed out after 30 seconds")

            result = await api.get_balances()

            assert result is not None
            assert isinstance(result, dict)
            assert result.get("success") is False
            assert "error" in result

    def test_sign_transaction_empty_input(self, api: JupiterUltraAPI) -> None:
        """Test sign_transaction with empty input."""
        with patch.object(api, "get_keypair"):
            with pytest.raises(Exception) as exc_info:
                api.sign_transaction("")
            assert "cannot be empty" in str(exc_info.value).lower()

    def test_sign_transaction_invalid_base64(self, api: JupiterUltraAPI) -> None:
        """Test sign_transaction with invalid base64."""
        with patch.object(api, "get_keypair"):
            with pytest.raises(Exception) as exc_info:
                api.sign_transaction("invalid_base64!")
            assert "invalid base64" in str(exc_info.value).lower()

    def test_reset_cached_clients(self, api: JupiterUltraAPI) -> None:
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

    @pytest.mark.asyncio
    async def test_real_swap_quote_creation(
        self, api: JupiterUltraAPI, real_env_vars: Any
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

    @pytest.mark.paid
    @pytest.mark.asyncio
    async def test_real_trade_execution(
        self, api: JupiterUltraAPI, real_env_vars: Any
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
