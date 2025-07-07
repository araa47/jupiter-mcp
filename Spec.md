# Jupiter Ultra MCP

Build a Python MCP server with tools to access Jupiter Ultra API: https://dev.jup.ag/docs/ultra-api/

This MCP server requires a user's private key to access their Solana wallet and a Solana RPC URL to make transactions via the Jupiter Ultra API.

## Requirements

- Use latest Solana Python library: https://github.com/michaelhly/solana-py
- Use FastMCP: https://github.com/jlowin/fastmcp
- Build asyncio Python app
- Use python-dotenv for environment variables: `SOLANA_RPC_URL`, `PRIVATE_KEY`
- Use Context7 MCP to search latest library documentation
- Use Playwright MCP if needed to browse the internet
- Leverage the above MCP tools while building this app

## Phase 1: Ultra API Tools (Implemented)

### Implemented Tools

- **get_swap_quote**: Get a swap quote and unsigned transaction
  - Parameters:
    - `input_mint`: Input token mint address
    - `output_mint`: Output token mint address
    - `amount`: Amount of input token in smallest unit
  - Returns: transaction (unsigned) and requestId
  - Cost: FREE

- **execute_swap_transaction**: Sign and execute a swap transaction
  - Parameters:
    - `transaction`: Base64 encoded unsigned transaction from get_swap_quote
    - `request_id`: Request ID from get_swap_quote response
  - Returns: signature and transaction details
  - Cost: PAID (executes real trades)
  - Note: Handles signing internally with configured private key

- **get_balances**: Get token balances for a wallet
  - Parameters:
    - `wallet_address` (optional): Wallet to check (defaults to configured wallet)
  - Returns: Array of token balances
  - Cost: FREE

- **get_shield**: Get token security information
  - Parameters:
    - `mints`: Comma-separated list of token mint addresses
  - Returns: Security information and warnings
  - Cost: FREE

- **search_token**: Search for tokens
  - Parameters:
    - `query`: Token symbol, name, or partial mint address
  - Returns: Array of matching tokens
  - Cost: FREE

## Testing

### Free Tests
- Test `get_balances` for the provided private key
- Test `get_swap_quote` functionality
- Test `search_token` functionality
- Test `get_shield` functionality

### Paid Tests (Optional)
- Test `execute_swap_transaction` with minimal SOL amount (0.001 SOL)
- Only run when `--run-paid-tests` flag is passed to pytest

## Notes

- Keep code simple, leverage existing libraries
- Dependencies managed with `uv` in `pyproject.toml`
- All tools use automatic referral system (2.55% max fee)

# Phase 2

Add support for Jupiter Trigger API https://dev.jup.ag/docs/trigger-api/

## Jupiter Trigger API Implementation Plan

The Trigger API enables limit orders on Solana - orders that execute automatically when market conditions are met. This is different from the Ultra API's immediate swaps.

### API Endpoints

Base URLs:
- Lite: `https://lite-api.jup.ag/trigger/v1/`
- Pro: `https://api.jup.ag/trigger/v1/`

### Tools to Implement for Phase 2

#### 1. **create_limit_order**
- **Endpoint**: `POST /createOrder`
- **Purpose**: Create a limit order that executes when target price is reached
- **Parameters**:
  - `input_mint`: Input token mint address
  - `output_mint`: Output token mint address
  - `making_amount`: Amount of input token to sell
  - `taking_amount`: Amount of output token to receive (sets the price)
  - `slippage_bps` (optional): Slippage in basis points (0 for "Exact" mode, >0 for "Ultra" mode)
  - `expired_at` (optional): Unix timestamp when order expires
- **Returns**:
  - `order`: Order account address
  - `transaction`: Unsigned transaction to create the order
  - `requestId`: ID for use with execute_limit_order
- **Notes**:
  - Minimum order size is $5 USD
  - This creates but doesn't execute the order
  - Automatically uses configured wallet as maker/payer
  - Automatically includes referral (DEV_REFERRER_WALLET, 255 basis points)
  - Automatically sets compute_unit_price to "auto"

#### 2. **execute_limit_order**
- **Endpoint**: `POST /execute`
- **Purpose**: Sign and execute a limit order transaction
- **Parameters**:
  - `transaction`: Base64 encoded unsigned transaction from create_limit_order
  - `request_id`: Request ID from create_limit_order response
- **Returns**:
  - `signature`: Transaction signature
  - `status`: "Success" or "Failed"
- **Notes**:
  - Similar to execute_swap_transaction but for limit orders
  - Handles signing internally with configured private key
  - This is a PAID operation that creates the limit order on-chain

#### 3. **cancel_limit_order**
- **Endpoint**: `POST /cancelOrder`
- **Purpose**: Cancel a single active limit order
- **Parameters**:
  - `order`: Order account address to cancel
- **Returns**:
  - `transaction`: Unsigned transaction to cancel the order
  - `requestId`: ID for use with execute_limit_order
- **Notes**:
  - Automatically uses configured wallet as maker
  - Automatically sets compute_unit_price to "auto"
  - Returns unsigned transaction that needs to be executed

#### 4. **cancel_limit_orders**
- **Endpoint**: `POST /cancelOrders`
- **Purpose**: Cancel multiple limit orders (batched in groups of 5)
- **Parameters**:
  - `orders` (optional): Array of order account addresses. If empty, cancels ALL orders
- **Returns**:
  - `transactions`: Array of unsigned transactions (one per batch of 5 orders)
  - `requestId`: ID for use with execute_limit_order
- **Notes**:
  - Returns multiple transactions if >5 orders
  - Each transaction needs to be signed and executed separately
  - Automatically uses configured wallet as maker
  - Automatically sets compute_unit_price to "auto"

#### 5. **get_limit_orders**
- **Endpoint**: `GET /getTriggerOrders`
- **Purpose**: Get active or historical limit orders for a wallet
- **Parameters**:
  - `wallet_address` (optional): Wallet to check (defaults to configured wallet)
  - `order_status`: "active" or "history"
  - `input_mint` (optional): Filter by input token
  - `output_mint` (optional): Filter by output token
  - `page` (optional): Page number for pagination (10 orders per page)
- **Returns**:
  - Array of order objects with details
  - `hasMoreData`: Boolean indicating if there are more pages

### Key Differences from Ultra API

1. **Order Type**: Limit orders vs immediate swaps
2. **Execution**: Orders execute automatically when price conditions are met
3. **Fees**:
   - Stable pairs: 0.03%
   - Other pairs: 0.1%
   - Plus automatic referral fees (2.55%)
4. **Slippage Modes**:
   - "Exact" mode: `slippageBps: 0` (default)
   - "Ultra" mode: `slippageBps: custom_value` (higher success rate)

### Implementation Notes

1. Follow same patterns as Phase 1:
   - Use underscores in tool names (not hyphens)
   - Execute functions handle signing internally
   - Include automatic referral system
   - Return consistent success/error response format
2. Update JupiterUltraAPI class with new methods
3. Register new tools in FastMCP server
4. Add comprehensive tests (both free and paid)
5. Update documentation with limit order examples

### Testing Plan

#### Free Tests
- Create limit order (get unsigned transaction)
- Get active/historical limit orders
- Cancel order (get unsigned transaction)
- Test pagination for order retrieval

#### Paid Tests (with --run-paid-tests flag)
- Execute a small limit order (0.0001 SOL)
- Monitor order status
- Cancel an active order
- Test order expiry

### Safety Considerations

1. Clear warnings about limit orders being different from swaps
2. Explain that orders may not execute immediately
3. Document minimum order size ($5 USD)
4. Emphasize testing with small amounts first
