#!/usr/bin/env python3
"""
Jupiter API Client

A Python client for interacting with the Jupiter APIs (Ultra & Trigger).
"""

import asyncio
import base64
import os
from typing import Any, Dict, List, Optional

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


class JupiterAPI:
    """Jupiter API client for Solana blockchain interactions."""

    def __init__(self):
        """Initialize the Jupiter API client."""
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.network = os.getenv("SOLANA_NETWORK", "devnet")
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.base_url = "https://lite-api.jup.ag/ultra/v1"
        self.trigger_base_url = "https://lite-api.jup.ag/trigger/v1"

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

        IMPORTANT: You can check MULTIPLE tokens in a single request by comma-separating mints!
        This is much more efficient than making multiple individual requests.

        Args:
            mints: Comma-separated list of token mint addresses to check
                   Example: "mint1,mint2,mint3" (no spaces between commas)
                   No specific limit mentioned in API docs

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - data: A "warnings" object with mint addresses as keys, each containing an array of warnings
            - error: Error message if request failed

        Warning Types and Severities:
            Info level warnings:
            - NOT_VERIFIED: Token is not verified, double-check mint address
            - LOW_ORGANIC_ACTIVITY: Token has low organic trading activity
            - NEW_LISTING: Token is newly listed
            - HAS_MINT_AUTHORITY: Owner can mint more tokens (dilution risk)

            Warning level warnings:
            - HAS_FREEZE_AUTHORITY: Owner can freeze your tokens (high risk!)
            - Transfer tax tokens are disabled on Jupiter frontend

        Example:
            >>> # Check security for multiple tokens at once
            >>> mints = "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v,someTokenMint"
            >>> result = await api.get_shield(mints=mints)
            >>> if result["success"]:
            ...     warnings = result["data"]["warnings"]
            ...     for mint, mint_warnings in warnings.items():
            ...         if mint_warnings:
            ...             print(f"\n⚠️ Warnings for {mint}:")
            ...             for warning in mint_warnings:
            ...                 severity_icon = "🔴" if warning["severity"] == "warning" else "🟡"
            ...                 print(f"  {severity_icon} {warning['type']}: {warning['message']}")
            ...         else:
            ...             print(f"✅ {mint}: No warnings found")
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

        IMPORTANT: You can search for MULTIPLE tokens in a single request by comma-separating queries!
        This is much more efficient than making multiple individual requests.

        Args:
            query: Search query - can be:
                   - Single token: symbol ("SOL"), name ("Solana"), or mint address
                   - Multiple tokens: comma-separated queries (e.g., "SOL,USDC,RAY")
                   - Limit: Up to 100 mint addresses when searching by address
                   - Response limit: Returns up to 20 tokens per symbol/name search

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - query: The original search query
            - data: Array of ALL matching tokens from ALL queries combined
            - error: Error message if request failed

        Example:
            >>> # Search for a single token
            >>> result = await api.search_token(query="SOL")
            >>> if result["success"]:
            ...     for token in result["data"]:
            ...         print(f"Symbol: {token['symbol']}, Mint: {token['mint']}")
            >>>
            >>> # Search for MULTIPLE tokens at once (RECOMMENDED for efficiency!)
            >>> result = await api.search_token(query="SOL,USDC,RAY,BONK")
            >>> if result["success"]:
            ...     # Returns all matching tokens for all queries in one response
            ...     for token in result["data"]:
            ...         print(f"{token['symbol']}: {token['mint']}")
            >>>
            >>> # Search by multiple mint addresses
            >>> mints = "So11111111111111111111111111111111111111112,EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            >>> result = await api.search_token(query=mints)
            >>> if result["success"]:
            ...     # Returns detailed info for all specified mints
            ...     for token in result["data"]:
            ...         print(f"{token['symbol']}: ${token.get('usdPrice', 'N/A')}")
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

    # Phase 2: Trigger API methods for limit orders

    async def create_limit_order(
        self,
        input_mint: str,
        output_mint: str,
        making_amount: str,
        taking_amount: str,
        slippage_bps: Optional[int] = 0,
        expired_at: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a limit order that executes when target price is reached.

        This function is FREE to call and does not execute any transactions.
        It returns an unsigned transaction that must be signed and executed.

        ⚠️ IMPORTANT WARNINGS:
        1. MINIMUM ORDER SIZE: Jupiter frontend enforces $5 USD minimum to ensure keeper profitability.
           Programmatically, smaller orders are accepted but may never execute!

        2. PRICE VALIDATION: The program does NOT check if your price makes sense!
           - Buying above market price? Order executes immediately at a LOSS
           - Setting wrong rate (e.g., 1000 USDC for 1 SOL)? You LOSE the difference!
           - Jupiter frontend warns/blocks orders >5% above market - API does NOT!

        3. TRANSFER TAX: Tokens with transfer tax extensions are disabled on frontend
           but API will accept them - be careful!

        4. SLIPPAGE: By default, trigger orders execute with 0 slippage (exact price).
           Add slippage for better fill probability but at worse price.

        Args:
            input_mint: Input token mint address (token to sell)
            output_mint: Output token mint address (token to buy)
            making_amount: Amount of input token to sell in smallest unit
            taking_amount: Amount of output token to receive in smallest unit (sets the price)
            slippage_bps: Slippage in basis points (0 = exact price, >0 = accept worse price)
            expired_at: Unix timestamp when order expires (optional)

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - data: Contains 'order' (account address), 'transaction' (unsigned), and 'requestId'
            - error: Error message if request failed

        Note:
            - Uses configured wallet as maker/payer
            - Includes automatic referral (2.55%)
            - Order executes when market price reaches your target

        Example:
            >>> # SAFE: Create limit order to sell 0.1 SOL when price reaches $200
            >>> # Current market: 1 SOL = $180, so this waits for price to rise
            >>> result = await api.create_limit_order(
            ...     input_mint="So11111111111111111111111111111111111111112",  # SOL
            ...     output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            ...     making_amount="100000000",  # 0.1 SOL (9 decimals)
            ...     taking_amount="20000000",   # 20 USDC (6 decimals) = $200/SOL rate
            ...     slippage_bps=50            # 0.5% slippage for better fills
            ... )
            >>>
            >>> # DANGEROUS: Wrong price - selling 1 SOL for only 1 USDC!
            >>> # This executes immediately and you LOSE ~$179!
            >>> # DON'T DO THIS:
            >>> # result = await api.create_limit_order(
            >>> #     input_mint="So11...112",
            >>> #     output_mint="EPj...t1v",
            >>> #     making_amount="1000000000",  # 1 SOL
            >>> #     taking_amount="1000000"      # 1 USDC - HUGE LOSS!
            >>> # )
        """
        try:
            # Validate inputs
            if not input_mint or not input_mint.strip():
                return {"success": False, "error": "input_mint cannot be empty"}
            if not output_mint or not output_mint.strip():
                return {"success": False, "error": "output_mint cannot be empty"}
            if not making_amount or not making_amount.strip():
                return {"success": False, "error": "making_amount cannot be empty"}
            if not taking_amount or not taking_amount.strip():
                return {"success": False, "error": "taking_amount cannot be empty"}

            # Validate amounts are numeric and positive
            try:
                making_num = int(making_amount)
                taking_num = int(taking_amount)
                if making_num <= 0 or taking_num <= 0:
                    return {
                        "success": False,
                        "error": "amounts must be positive numbers",
                    }
            except ValueError:
                return {"success": False, "error": "amounts must be valid numbers"}

            # Get wallet as maker
            keypair = self.get_keypair()
            maker = str(keypair.pubkey())

            # Build params object
            params: Dict[str, str] = {
                "makingAmount": making_amount,
                "takingAmount": taking_amount,
            }

            # Add optional parameters to params
            if slippage_bps is not None and slippage_bps > 0:
                params["slippageBps"] = str(slippage_bps)

            if expired_at is not None:
                params["expiredAt"] = str(expired_at)

            # Add referral fee in params as feeBps
            if DEV_REFERRER_WALLET:
                params["feeBps"] = "255"  # 255 basis points (2.55%)

            # Build request payload according to API docs
            payload = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "maker": maker,
                "payer": maker,
                "params": params,
                "computeUnitPrice": "auto",
                # Note: feeAccount would be the referral token account of the output mint
                # We're not setting it here as it requires a specific token account setup
            }

            # Make the API request
            url = f"{self.trigger_base_url}/createOrder"
            response = await self.make_http_request("POST", url, json_data=payload)

            return {"success": True, "data": response}

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create limit order: {str(e)}",
            }

    async def execute_limit_order(
        self, transaction: str, request_id: str
    ) -> Dict[str, Any]:
        """
        🚨 WARNING: THIS WILL CREATE A REAL LIMIT ORDER ON-CHAIN! 🚨

        Sign and execute a limit order transaction.

        This is a PAID operation that creates a limit order on the Solana blockchain.
        The order will execute automatically when market conditions are met.

        Args:
            transaction: Base64 encoded unsigned transaction from create_limit_order
            request_id: Request ID from create_limit_order response

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the execution was successful
            - data: Contains 'signature' and status if successful
            - error: Error message if execution failed

        Note:
            - This creates a limit order that may execute later
            - Orders have fees: 0.03% (stable pairs) or 0.1% (other pairs)
            - Plus automatic referral fees (2.55%)
            - Minimum order size is $5 USD

        Example:
            >>> # First create the order
            >>> order = await api.create_limit_order(...)
            >>> if order["success"]:
            ...     # Then execute it
            ...     result = await api.execute_limit_order(
            ...         transaction=order["data"]["transaction"],
            ...         request_id=order["data"]["requestId"]
            ...     )
            ...     if result["success"]:
            ...         print(f"Limit order created! Signature: {result['data']['signature']}")
        """
        try:
            # Validate inputs
            if not transaction or not transaction.strip():
                raise ValueError("Transaction cannot be empty")
            if not request_id or not request_id.strip():
                raise ValueError("Request ID cannot be empty")

            print("🚨 WARNING: About to create a REAL limit order on-chain!")
            print(
                "🚨 This order will execute automatically when price conditions are met!"
            )

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
            print("⚡ Creating limit order on Solana blockchain...")
            payload = {"signedTransaction": signed_transaction, "requestId": request_id}

            # Make the API request
            url = f"{self.trigger_base_url}/execute"
            response = await self.make_http_request("POST", url, json_data=payload)

            print(f"🎉 Limit order created! Response: {response}")
            return {"success": True, "data": response}

        except Exception as e:
            print(f"❌ Limit order creation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def cancel_limit_order(self, order: str) -> Dict[str, Any]:
        """
        Cancel a single active limit order.

        This function is FREE to call and does not execute any transactions.
        It returns an unsigned transaction that must be signed and executed.

        Args:
            order: Order account address to cancel

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - data: Contains 'transaction' (unsigned) and 'requestId'
            - error: Error message if request failed

        Note:
            - Returns unsigned transaction that needs to be executed
            - Uses configured wallet as maker

        Example:
            >>> # Cancel a specific order
            >>> result = await api.cancel_limit_order(
            ...     order="your_order_account_address_here"
            ... )
            >>> if result["success"]:
            ...     # Execute the cancellation
            ...     exec_result = await api.execute_limit_order(
            ...         transaction=result["data"]["transaction"],
            ...         request_id=result["data"]["requestId"]
            ...     )
        """
        try:
            # Validate inputs
            if not order or not order.strip():
                return {"success": False, "error": "order address cannot be empty"}

            # Get wallet as maker
            keypair = self.get_keypair()
            maker = str(keypair.pubkey())

            # Build request payload
            payload = {
                "order": order,
                "maker": maker,
                "computeUnitPrice": "auto",
            }

            # Make the API request
            url = f"{self.trigger_base_url}/cancelOrder"
            response = await self.make_http_request("POST", url, json_data=payload)

            return {"success": True, "data": response}

        except Exception as e:
            return {"success": False, "error": f"Failed to cancel order: {str(e)}"}

    async def cancel_limit_orders(
        self, orders: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Cancel multiple limit orders (batched in groups of 5).

        This function is FREE to call and does not execute any transactions.
        It returns unsigned transactions that must be signed and executed.

        Args:
            orders: Array of order account addresses. If None/empty, cancels ALL orders

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - data: Contains 'transactions' (array of unsigned) and 'requestId'
            - error: Error message if request failed

        Note:
            - Returns multiple transactions if >5 orders
            - Each transaction needs to be signed and executed separately
            - Uses configured wallet as maker

        Example:
            >>> # Cancel specific orders
            >>> result = await api.cancel_limit_orders(
            ...     orders=["order1_address", "order2_address", "order3_address"]
            ... )
            >>>
            >>> # Cancel ALL orders
            >>> result = await api.cancel_limit_orders()
            >>> if result["success"]:
            ...     # Execute each cancellation transaction
            ...     for tx in result["data"]["transactions"]:
            ...         exec_result = await api.execute_limit_order(
            ...             transaction=tx,
            ...             request_id=result["data"]["requestId"]
            ...         )
        """
        try:
            # Get wallet as maker
            keypair = self.get_keypair()
            maker = str(keypair.pubkey())

            # Build request payload
            payload: Dict[str, Any] = {
                "maker": maker,
                "computeUnitPrice": "auto",
            }

            # Add orders if provided
            if orders is not None and len(orders) > 0:
                # Validate each order address
                for order in orders:
                    if not order or not order.strip():
                        return {
                            "success": False,
                            "error": "order addresses cannot be empty",
                        }
                payload["orders"] = orders

            # Make the API request
            url = f"{self.trigger_base_url}/cancelOrders"
            response = await self.make_http_request("POST", url, json_data=payload)

            return {"success": True, "data": response}

        except Exception as e:
            return {"success": False, "error": f"Failed to cancel orders: {str(e)}"}

    async def get_limit_orders(
        self,
        order_status: str = "active",
        wallet_address: Optional[str] = None,
        input_mint: Optional[str] = None,
        output_mint: Optional[str] = None,
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get active or historical limit orders for a wallet.

        This function is FREE to call and does not execute any transactions.

        Args:
            order_status: "active" or "history" (default: "active")
            wallet_address: Wallet to check (optional, defaults to configured wallet)
            input_mint: Filter by input token (optional)
            output_mint: Filter by output token (optional)
            page: Page number for pagination, 10 orders per page (optional)

        Returns:
            Dictionary containing:
            - success: Boolean indicating if the request was successful
            - wallet_address: The wallet address that was queried
            - data: Array of order objects with details
            - hasMoreData: Boolean indicating if there are more pages
            - error: Error message if request failed

        Example:
            >>> # Get active orders for configured wallet
            >>> result = await api.get_limit_orders(order_status="active")
            >>> if result["success"]:
            ...     for order in result["data"]:
            ...         print(f"Order {order['orderAccount']}: {order['makingAmount']} → {order['takingAmount']}")
            >>>
            >>> # Get order history with pagination
            >>> result = await api.get_limit_orders(order_status="history", page=1)
        """
        try:
            # Validate order_status
            if order_status not in ["active", "history"]:
                return {
                    "success": False,
                    "error": "order_status must be 'active' or 'history'",
                }

            # Use configured wallet if address not provided
            if wallet_address is None:
                keypair = self.get_keypair()
                wallet_address = str(keypair.pubkey())

            # Validate wallet address
            if not wallet_address or not wallet_address.strip():
                return {"success": False, "error": "wallet_address cannot be empty"}

            # Build query parameters
            params = {
                "orderStatus": order_status,
                "wallet": wallet_address,
            }

            # Add optional filters
            if input_mint:
                params["inputMint"] = input_mint
            if output_mint:
                params["outputMint"] = output_mint
            if page is not None:
                params["page"] = str(page)

            # Make the API request
            url = f"{self.trigger_base_url}/getTriggerOrders"
            response = await self.make_http_request("GET", url, params=params)

            # Extract hasMoreData flag if present
            has_more_data = response.get("hasMoreData", False)

            # Handle response format
            if "orders" in response:
                data = response["orders"]
            elif isinstance(response, list):
                data = response
            else:
                data = response

            return {
                "success": True,
                "wallet_address": wallet_address,
                "data": data,
                "hasMoreData": has_more_data,
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to get limit orders: {str(e)}"}
