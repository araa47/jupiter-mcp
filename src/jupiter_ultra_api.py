#!/usr/bin/env python3
"""
Jupiter Ultra API Client

A Python client for interacting with the Jupiter Ultra API.
"""

import asyncio
import base64
import os
from typing import Any, Dict, Optional

import aiohttp
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Load environment variables
load_dotenv()

# Constants
# https://referral.jup.ag/
DEV_REFERRER_WALLET = "8cK8hCyRQCp52nVuPLnLL71afkRvRcFibSwHMjGFT8bm"


class JupiterUltraAPI:
    """Jupiter Ultra API client for Solana blockchain interactions."""

    def __init__(self):
        """Initialize the Jupiter Ultra API client."""
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.network = os.getenv("SOLANA_NETWORK", "devnet")
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.base_url = "https://lite-api.jup.ag/ultra/v1"

        # Initialize clients
        self._solana_client: Optional[AsyncClient] = None
        self._keypair: Optional[Keypair] = None

    def get_solana_client(self) -> AsyncClient:
        """Get or create the Solana RPC client."""
        if self._solana_client is None:
            self._solana_client = AsyncClient(self.rpc_url)
        return self._solana_client

    def get_keypair(self) -> Keypair:
        """Get or create the keypair from the private key."""
        if self._keypair is None:
            if not self.private_key:
                raise ValueError("PRIVATE_KEY environment variable is required")
            try:
                # Try to decode as base58 first
                self._keypair = Keypair.from_base58_string(self.private_key)
            except Exception:
                try:
                    # Try to decode as bytes
                    private_key_bytes = base64.b64decode(self.private_key)
                    self._keypair = Keypair.from_bytes(private_key_bytes)
                except Exception as e:
                    raise ValueError(f"Invalid PRIVATE_KEY format: {e}") from e
        return self._keypair

    async def make_http_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with error handling."""
        if timeout is None:
            timeout = self.request_timeout

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
            except asyncio.TimeoutError as e:
                raise Exception(f"Request timed out after {timeout} seconds") from e
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}") from e

    async def get_swap_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: str,
    ) -> Dict[str, Any]:
        """
        Get a swap quote and unsigned transaction from Jupiter Ultra API.

        This function is FREE to call and does not execute any transactions.
        Use this to get price quotes and prepare transactions for execution.

        Args:
            input_mint: The input token mint address (e.g., SOL: "So11111111111111111111111111111111111111112")
            output_mint: The output token mint address (e.g., USDC: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
            amount: The amount of input token to swap in smallest unit (e.g., "1000000" = 0.001 SOL)

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - data: Contains 'transaction' (unsigned) and 'requestId' for execution
            - error: Error message if request failed

        Example:
            >>> result = await api.get_swap_quote(
            ...     input_mint="So11111111111111111111111111111111111111112",  # SOL
            ...     output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            ...     amount="1000000"  # 0.001 SOL
            ... )
            >>> if result["success"]:
            ...     transaction = result["data"]["transaction"]
            ...     request_id = result["data"]["requestId"]
        """
        try:
            # Validate inputs
            if not input_mint or not input_mint.strip():
                return {"success": False, "error": "input_mint cannot be empty"}
            if not output_mint or not output_mint.strip():
                return {"success": False, "error": "output_mint cannot be empty"}
            if not amount or not amount.strip():
                return {"success": False, "error": "amount cannot be empty"}

            # Validate amount is numeric
            try:
                amount_num = int(amount)
                if amount_num <= 0:
                    return {
                        "success": False,
                        "error": "amount must be a positive number",
                    }
            except ValueError:
                return {"success": False, "error": "amount must be a valid number"}

            # Use configured wallet as taker
            keypair = self.get_keypair()
            taker = str(keypair.pubkey())

            # Build query parameters with referral
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "taker": taker,
                "referralAccount": DEV_REFERRER_WALLET,
                "referralFee": "255",  # 255 basis points (2.55%) - maximum allowed
            }

            # Make the API request
            url = f"{self.base_url}/order"
            response = await self.make_http_request("GET", url, params=params)

            return {"success": True, "data": response}

        except Exception as e:
            return {"success": False, "error": f"Failed to get swap quote: {str(e)}"}

    async def execute_swap_transaction(
        self, transaction: str, request_id: str
    ) -> Dict[str, Any]:
        """
        🚨 WARNING: THIS WILL EXECUTE A REAL TRADE AND SPEND ACTUAL SOL! 🚨

        Sign and execute a swap transaction via Jupiter Ultra API.

        This is a PAID operation that executes real trades on the Solana blockchain.
        Only call this function when you want to actually execute a trade.

        This method will:
        1. Sign the provided unsigned transaction with your configured private key
        2. Execute the signed transaction on the Solana blockchain
        3. SPEND REAL SOL/TOKENS - THIS IS NOT REVERSIBLE!

        Args:
            transaction: The base64 encoded UNSIGNED transaction from get_swap_quote
            request_id: The request ID from the swap quote response

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the execution was successful
            - data: Contains 'signature' and transaction details if successful
            - error: Error message if execution failed

        Example:
            >>> # First get a quote
            >>> quote = await api.get_swap_quote(input_mint, output_mint, amount)
            >>> if quote["success"]:
            ...     # Then execute the trade
            ...     result = await api.execute_swap_transaction(
            ...         transaction=quote["data"]["transaction"],
            ...         request_id=quote["data"]["requestId"]
            ...     )
            ...     if result["success"]:
            ...         print(f"Trade executed! Signature: {result['data']['signature']}")
        """
        try:
            # Validate inputs
            if not transaction or not transaction.strip():
                raise ValueError("Transaction cannot be empty")
            if not request_id or not request_id.strip():
                raise ValueError("Request ID cannot be empty")

            print("🚨 WARNING: About to sign and execute a REAL trade!")
            print("🚨 This will spend actual SOL/tokens on the blockchain!")

            # Step 1: Sign the transaction
            print("🔐 Signing transaction with your private key...")
            try:
                signed_transaction = self.sign_transaction(transaction)
                print("✅ Transaction signed successfully")
            except Exception as sign_error:
                print(f"❌ Transaction signing failed: {str(sign_error)}")
                return {
                    "success": False,
                    "error": f"Failed to sign transaction: {str(sign_error)}",
                }

            # Step 2: Execute the signed transaction
            print("⚡ Executing transaction on Solana blockchain...")
            payload = {"signedTransaction": signed_transaction, "requestId": request_id}

            # Make the API request
            url = f"{self.base_url}/execute"
            response = await self.make_http_request("POST", url, json_data=payload)

            print(f"🎉 Transaction executed! Response: {response}")
            return {"success": True, "data": response}

        except Exception as e:
            print(f"❌ Transaction execution failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_balances(
        self, wallet_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get token balances for a wallet address via Jupiter Ultra API.

        This function is FREE to call and does not execute any transactions.
        Use this to check wallet holdings before making trades.

        Args:
            wallet_address: The wallet address to get balances for (optional, will use configured wallet if not provided)

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - wallet_address: The wallet address that was queried
            - data: Array of token balances with mint addresses, amounts, and decimals
            - error: Error message if request failed

        Example:
            >>> # Get balances for configured wallet
            >>> result = await api.get_balances()
            >>> if result["success"]:
            ...     balances = result["data"]
            ...     for balance in balances:
            ...         print(f"Token: {balance['mint']}, Amount: {balance['amount']}")
            >>>
            >>> # Get balances for specific wallet
            >>> result = await api.get_balances(wallet_address="11111111111111111111111111111112")
        """
        try:
            # Use configured wallet if address not provided
            if wallet_address is None:
                keypair = self.get_keypair()
                wallet_address = str(keypair.pubkey())

            # Validate wallet address
            if not wallet_address or not wallet_address.strip():
                return {"success": False, "error": "wallet_address cannot be empty"}

            # Make the API request
            url = f"{self.base_url}/balances/{wallet_address}"
            response = await self.make_http_request("GET", url)

            return {"success": True, "wallet_address": wallet_address, "data": response}

        except Exception as e:
            return {"success": False, "error": f"Failed to get balances: {str(e)}"}

    async def get_shield(self, mints: str) -> Dict[str, Any]:
        """
        Get token security information via Jupiter Ultra Shield API.

        This function is FREE to call and does not execute any transactions.
        Use this to check token security before making trades. Essential for avoiding scam tokens.

        Args:
            mints: Comma-separated list of token mint addresses to check (e.g., "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - data: Security information including warnings for each token
            - error: Error message if request failed

        Example:
            >>> # Check security for SOL and USDC
            >>> result = await api.get_shield(
            ...     mints="So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            ... )
            >>> if result["success"]:
            ...     for token_info in result["data"]:
            ...         if token_info.get("warnings"):
            ...             print(f"⚠️ Security warnings for {token_info['mint']}: {token_info['warnings']}")
        """
        try:
            # Validate inputs
            if not mints or not mints.strip():
                return {"success": False, "error": "mints parameter cannot be empty"}

            # Prepare query parameters
            params = {"mints": mints}

            # Make the API request
            url = f"{self.base_url}/shield"
            response = await self.make_http_request("GET", url, params=params)

            return {"success": True, "data": response}

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get shield information: {str(e)}",
            }

    async def search_token(self, query: str) -> Dict[str, Any]:
        """
        Search for tokens via Jupiter Ultra API.

        This function is FREE to call and does not execute any transactions.
        Use this to find token mint addresses when you only know the symbol or name.

        Args:
            query: Search query (token symbol like "SOL", name like "Solana", or partial mint address)

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - query: The original search query
            - data: Array of matching tokens with mint addresses, symbols, names, and decimals
            - error: Error message if request failed

        Example:
            >>> # Search for SOL token
            >>> result = await api.search_token(query="SOL")
            >>> if result["success"]:
            ...     for token in result["data"]:
            ...         print(f"Symbol: {token['symbol']}, Mint: {token['mint']}")
            >>>
            >>> # Search for USDC token
            >>> result = await api.search_token(query="USDC")
            >>> if result["success"]:
            ...     usdc_mint = result["data"][0]["mint"]  # Get first result
        """
        try:
            # Validate inputs
            if not query or not query.strip():
                return {"success": False, "error": "search query cannot be empty"}

            # Prepare query parameters
            params = {"query": query}

            # Make the API request
            url = f"{self.base_url}/search"
            response = await self.make_http_request("GET", url, params=params)

            return {"success": True, "query": query, "data": response}

        except Exception as e:
            return {"success": False, "error": f"Failed to search tokens: {str(e)}"}

    def get_wallet_info(self) -> Dict[str, str]:
        """Get information about the configured wallet."""
        try:
            keypair = self.get_keypair()
            return {
                "wallet_address": str(keypair.pubkey()),
                "network": self.network,
                "rpc_url": self.rpc_url,
            }
        except Exception as e:
            return {"error": str(e)}

    def reset_cached_clients(self) -> None:
        """Reset cached clients (useful for testing)."""
        self._solana_client = None
        self._keypair = None

    def sign_transaction(self, transaction_base64: str) -> str:
        """
        Sign a transaction using the configured private key.

        Args:
            transaction_base64: Base64 encoded transaction bytes

        Returns:
            Base64 encoded signed transaction
        """
        try:
            # Validate input
            if not transaction_base64:
                raise ValueError("Transaction base64 string cannot be empty")

            # Validate base64 format
            if len(transaction_base64) % 4 != 0:
                raise ValueError(
                    "Invalid base64-encoded string: number of data characters must be a multiple of 4"
                )

            # Get the keypair
            keypair = self.get_keypair()

            # Decode the transaction with better error handling
            try:
                transaction_bytes = base64.b64decode(transaction_base64, validate=True)
            except Exception as decode_error:
                raise ValueError(
                    f"Invalid base64-encoded string: {str(decode_error)}"
                ) from decode_error

            # Validate transaction bytes
            if len(transaction_bytes) == 0:
                raise ValueError("Transaction bytes cannot be empty after decoding")

            # Create VersionedTransaction from bytes
            try:
                unsigned_transaction = VersionedTransaction.from_bytes(
                    transaction_bytes
                )
            except Exception as tx_error:
                raise ValueError(
                    f"Invalid transaction format: {str(tx_error)}"
                ) from tx_error

            # Create a signed transaction with the keypair
            signed_transaction = VersionedTransaction(
                unsigned_transaction.message, [keypair]
            )

            # Return the signed transaction as base64
            return base64.b64encode(bytes(signed_transaction)).decode("utf-8")

        except Exception as e:
            raise Exception(f"Failed to sign transaction: {str(e)}") from e
