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

# Load environment variables
load_dotenv()


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

    async def get_order(
        self,
        input_mint: str,
        output_mint: str,
        amount: str,
        taker: Optional[str] = None,
        referral_account: Optional[str] = None,
        referral_fee: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get a swap order from Jupiter Ultra API.

        Args:
            input_mint: The input token mint address
            output_mint: The output token mint address
            amount: The amount of input token to swap (in token's smallest unit)
            taker: The user's wallet address (optional, will use configured wallet if not provided)
            referral_account: The referral account address (optional)
            referral_fee: The referral fee in basis points (optional)

        Returns:
            Dictionary containing the order response with transaction and request ID
        """
        try:
            # Use configured wallet if taker not provided
            if taker is None:
                keypair = self.get_keypair()
                taker = str(keypair.pubkey())

            # Build query parameters
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "taker": taker,
            }

            if referral_account:
                params["referralAccount"] = referral_account
            if referral_fee is not None:
                params["referralFee"] = str(referral_fee)

            # Make the API request
            url = f"{self.base_url}/order"
            response = await self.make_http_request("GET", url, params=params)

            return {"success": True, "data": response}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_order(
        self, signed_transaction: str, request_id: str
    ) -> Dict[str, Any]:
        """
        Execute a signed swap transaction via Jupiter Ultra API.

        Note: This method expects an already signed transaction. It does not
        sign transactions itself - that must be done separately.

        Args:
            signed_transaction: The base64 encoded signed transaction
            request_id: The request ID from the order response

        Returns:
            Dictionary containing the execution result with status and signature
        """
        try:
            # Prepare the request payload
            payload = {"signedTransaction": signed_transaction, "requestId": request_id}

            # Make the API request
            url = f"{self.base_url}/execute"
            response = await self.make_http_request("POST", url, json_data=payload)

            return {"success": True, "data": response}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_balances(
        self, wallet_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get token balances for a wallet address via Jupiter Ultra API.

        Args:
            wallet_address: The wallet address to get balances for (optional, will use configured wallet if not provided)

        Returns:
            Dictionary containing the wallet's token balances
        """
        try:
            # Use configured wallet if address not provided
            if wallet_address is None:
                keypair = self.get_keypair()
                wallet_address = str(keypair.pubkey())

            # Make the API request
            url = f"{self.base_url}/balances/{wallet_address}"
            response = await self.make_http_request("GET", url)

            return {"success": True, "wallet_address": wallet_address, "data": response}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_shield(self, mints: str) -> Dict[str, Any]:
        """
        Get token security information via Jupiter Ultra Shield API.

        This method only retrieves security information and does not execute any transactions.

        Args:
            mints: Comma-separated list of token mint addresses to check

        Returns:
            Dictionary containing token warnings and security information
        """
        try:
            # Prepare query parameters
            params = {"mints": mints}

            # Make the API request
            url = f"{self.base_url}/shield"
            response = await self.make_http_request("GET", url, params=params)

            return {"success": True, "data": response}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_token(self, query: str) -> Dict[str, Any]:
        """
        Search for tokens via Jupiter Ultra API.

        Args:
            query: Search query (token symbol, name, or mint address)

        Returns:
            Dictionary containing search results with token information
        """
        try:
            # Prepare query parameters
            params = {"query": query}

            # Make the API request
            url = f"{self.base_url}/search"
            response = await self.make_http_request("GET", url, params=params)

            return {"success": True, "query": query, "data": response}

        except Exception as e:
            return {"success": False, "error": str(e)}

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
