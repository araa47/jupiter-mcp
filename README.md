# Jupiter MCP

A Model Context Protocol server for Jupiter API, Solana's premier DEX aggregator. Supports immediate swaps through Ultra API and limit orders through Trigger API.

## 📦 Pre-built Desktop Extension (DXT)

### Prerequisites
Before installing the extension, ensure you have:

1. **Node.js and npx** (for envmcp support)
   - Download from: https://nodejs.org/
   - Verify with: `npx --version`

2. **uv/uvx** (Python package manager)
   - Install from: https://docs.astral.sh/uv/getting-started/installation/
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Verify with: `uvx --version`


Once you have prereqs for easy installation in Claude Desktop:

**[Download jupiter-mcp-latest.dxt](https://github.com/araa47/jupiter-mcp/raw/main/jupiter-mcp-latest.dxt)** 📥

The DXT includes:
- ✅ One-click installation in Claude Desktop
- ✅ Automatic dependency management with uvx
- ✅ Secure environment variable configuration
- ✅ Built-in error handling and debugging

> **Note**: The DXT file is automatically updated on every commit for the latest features and fixes.

## 🚀 Quick Installation Options

### Option 1: Claude Desktop DXT (Recommended) 🖱️
Download the DXT file and double-click to install. See `dxt/README.md` for detailed instructions.

### Option 2: Quick Install with Cursor 🎯

**Instructions:**
1. Copy the link below (click the copy button in the code block)
2. Paste it into your browser address bar or Cursor's command palette
3. Follow the prompts to complete installation
4. You'll be prompted to replace `REPLACE_THIS` with your actual solana private key!


**🚀 Install with Direct Input:**
```
cursor://anysphere.cursor-deeplink/mcp/install?name=jupiter-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2FyYWE0Ny9qdXBpdGVyLW1jcCIsImp1cGl0ZXItbWNwIl0sImVudiI6eyJQUklWQVRFX0tFWSI6IlJFUExBQ0VfVEhJUyIsIlNPTEFOQV9SUENfVVJMIjoiaHR0cHM6Ly9hcGkubWFpbm5ldC1iZXRhLnNvbGFuYS5jb20iLCJTT0xBTkFfTkVUV09SSyI6Im1haW5uZXQtYmV0YSIsIlJFUVVFU1RfVElNRU9VVCI6IjMwIn19
```
**Note:** These links only work in Cursor

**Manual config for .env file approach:**

```json
{
  "mcpServers": {
    "jupiter-mcp": {
      "command": "npx",
      "args": [
        "envmcp",
        "--env-file",
        "/path/to/your/.env",
        "uvx",
        "--from",
        "git+https://github.com/araa47/jupiter-mcp",
        "jupiter-mcp"
      ]
    }
  }
}
```

Replace `/path/to/your/.env` with your actual env file path (e.g., `/Users/yourname/.env`)

**Pre-configured values:**

* `SOLANA_RPC_URL`: <https://api.mainnet-beta.solana.com>
* `SOLANA_NETWORK`: mainnet-beta
* `REQUEST_TIMEOUT`: 30 seconds
* `PRIVATE_KEY`: You'll need to replace `REPLACE_THIS` with your base58 encoded private key

## ⚡ Quick Start (MCP Configuration)

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "jupiter-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/araa47/jupiter-mcp",
        "jupiter-mcp"
      ],
      "env": {
        "SOLANA_RPC_URL": "https://api.mainnet-beta.solana.com",
        "PRIVATE_KEY": "${PRIVATE_KEY}",
        "SOLANA_NETWORK": "mainnet-beta",
        "REQUEST_TIMEOUT": "30"
      }
    }
  }
}
```

## 🔐 Client-Side Key Handling (Enhanced Security)

Jupiter MCP supports **client-side mode** for enhanced security where private keys never leave your local environment:

### 🚀 Quick Start - Client-Side Mode

```bash
# Start in secure client-side mode
jupiter-mcp --client-side

# Or with environment variable
export CLIENT_SIDE_MODE=true
jupiter-mcp
```

### 🔄 Client-Side Workflow

In client-side mode, the typical workflow is:

1. **Build Raw Transaction**: Get unsigned transaction data
2. **Sign Locally**: Use your wallet/hardware device to sign
3. **Submit**: Send the signed transaction to the blockchain

```python
# Example workflow (in client-side mode)
# 1. Build unsigned transaction
raw_tx = await api.build_raw_swap_tx(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount="1000000",
    user_address="YourWalletAddress"
)

# 2. Sign with your wallet/hardware (external process)
signed_tx = your_signing_function(raw_tx["data"]["transaction"])

# 3. Submit signed transaction
result = await api.submit_signed_transaction(
    signed_transaction=signed_tx,
    request_id=raw_tx["data"]["requestId"]
)
```

### 🛡️ Security Benefits

- **🔒 Private keys never leave your client**
- **🔧 Compatible with hardware wallets**
- **⚡ Perfect for production environments**
- **🎯 Enhanced control over transaction signing**

### 📋 Client-Side Mode Methods

| Method | Purpose | Security |
|--------|---------|----------|
| `build_raw_swap_tx` | Create unsigned swap transactions | ✅ Safe |
| `submit_signed_transaction` | Submit pre-signed transactions | ⚠️ Executes trades |
| `create_limit_order` | Create unsigned limit orders | ✅ Safe |
| `get_balances` | Check balances (requires wallet address) | ✅ Safe |

**Disabled in client-side mode:**
- `execute_swap_transaction` - Use `build_raw_swap_tx` + `submit_signed_transaction`
- `execute_limit_order` - Use `create_limit_order` + `submit_signed_transaction`

### Alternative Configuration (Using .env file)

If you prefer to load environment variables from a `.env` file to avoid storing sensitive data in your MCP configuration:

```json
{
  "mcpServers": {
    "jupiter-mcp": {
      "command": "npx",
      "args": [
        "envmcp",
        "--env-file",
        "${ENV_FILE_PATH}",
        "uvx",
        "--from",
        "git+https://github.com/araa47/jupiter-mcp",
        "jupiter-mcp"
      ],
      "env": {
        "ENV_FILE_PATH": ".env"
      }
    }
  }
}
```

This approach uses `envmcp` to securely load your PRIVATE_KEY from a `.env` file without exposing it in configuration files. Replace `ENV_FILE_PATH` with the absolute path to your `.env` file (e.g., `/Users/yourname/.env` or `/home/user/.env`).

### Environment Variables Required:

* `PRIVATE_KEY`: Your base58 encoded Solana private key (from Phantom wallet export)
* Optional: Override `SOLANA_RPC_URL` if you have a custom RPC endpoint

## 🎉 Available Tools

### 💱 Ultra API (Immediate Swaps)

| Tool                       | Description                               | Parameters                        | Cost     |
| -------------------------- | ----------------------------------------- | --------------------------------- | -------- |
| get\_swap\_quote           | Get a swap quote and unsigned transaction | input\_mint, output\_mint, amount | **FREE** |
| execute\_swap\_transaction | Execute a signed swap transaction         | transaction, request\_id          | **PAID** |
| get\_balances              | Get token balances for a wallet           | wallet\_address?                  | **FREE** |
| get\_shield                | Get token security information            | mints                             | **FREE** |
| search\_token              | Search for tokens                         | query                             | **FREE** |

### 📊 Trigger API (Limit Orders)

| Tool                  | Description                        | Parameters                                                                              | Cost     |
| --------------------- | ---------------------------------- | --------------------------------------------------------------------------------------- | -------- |
| create\_limit\_order  | Create a limit order transaction   | input\_mint, output\_mint, making\_amount, taking\_amount, slippage\_bps?, expired\_at? | **FREE** |
| execute\_limit\_order | Execute a limit order transaction  | transaction, request\_id                                                                | **PAID** |
| cancel\_limit\_order  | Cancel a single limit order        | order                                                                                   | **FREE** |
| cancel\_limit\_orders | Cancel multiple limit orders       | orders?                                                                                 | **FREE** |
| get\_limit\_orders    | Get active/historical limit orders | order\_status, wallet\_address?, input\_mint?, output\_mint?, page?                     | **FREE** |

### Key Differences: Swaps vs Limit Orders

* **Swaps** (Ultra API): Execute immediately at current market price
* **Limit Orders** (Trigger API): Execute automatically when your target price is reached

## 🛠️ Development & CI/CD

### Automated DXT Building

This project includes automated DXT building integrated with pre-commit hooks:

- **Pre-commit Hook**: Automatically builds DXT files when changes are made to `dxt/` folder
- **Simple Naming**: Always creates `jupiter-mcp-latest.dxt` for easy downloads
- **Auto-update**: The latest DXT file is always current with the main branch

### Manual DXT Build

```bash
# Build DXT
./scripts/build-dxt.sh

# Output: jupiter-mcp-latest.dxt
```

### Pre-commit Setup

```bash
# Install pre-commit hooks (includes DXT building)
pre-commit install

# The DXT will be automatically built when changes are detected in:
# - dxt/ directory
# - scripts/build-dxt.sh
```

## 🔧 Alternative Installation (Development)

For local development or testing:

### Prerequisites

* Python 3.12+
* uv for dependency management
* direnv

### Setup

```bash
git clone https://github.com/araa47/jupiter-mcp
cd jupiter-mcp
direnv allow
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables (.env file)

```bash
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
PRIVATE_KEY=your_base58_encoded_private_key_here
SOLANA_NETWORK=mainnet-beta
REQUEST_TIMEOUT=30
```

### Local Development Usage

```bash
# Start the server locally
uv run python run_server.py
```

## 🧪 Testing

The project includes comprehensive testing with safety features:

### Test Types

**🆓 Free Tests** (Default - No SOL spent):

* Mock execution tests
* API quote/balance checks
* Token searches and security checks
* Error handling validation

**💰 Paid Tests** (Requires `--run-paid-tests` flag):

* Real trade execution on mainnet
* Swap tests: Uses tiny amounts (0.0001 SOL ≈ $0.015)
* Limit order tests: Creates orders 20% above market price
   * Uses 0.04 SOL (≈ $6) to meet minimum requirements
   * Orders won't execute at the high price
   * Automatically cancelled after verification
* Full transaction signing and broadcasting

### Running Tests

```bash
# Safe tests only (default)
uv run pytest tests/ -v

# Include real trade execution (spends tiny amounts)
uv run pytest tests/ -v --run-paid-tests

# Test with detailed output
uv run pytest tests/ -v --run-paid-tests -s
```

### Test Safety Features

* **Paid tests clearly marked** with `@pytest.mark.paid`
* **Minimal trade amounts** for real execution
* **Limit orders use out-of-range prices** that won't execute
* **Clear warnings** before spending real money
* **Transaction confirmations** with blockchain signatures

## 💡 Important Notes

### Free vs Paid Operations

* **🆓 FREE**: `get_swap_quote`, `get_balances`, `get_shield`, `search_token`, `create_limit_order`, `cancel_limit_order`, `cancel_limit_orders`, `get_limit_orders` - API calls only
* **💰 PAID**: `execute_swap_transaction`, `execute_limit_order` - Executes real trades and spends SOL

### Automatic Referral System

* All orders include a 255 basis point (2.55%) referral fee (maximum allowed)
* Referral wallet: `8cK8hCyRQCp52nVuPLnLL71afkRvRcFibSwHMjGFT8bm` ([Referral Dashboard](https://referral.jup.ag/dashboard/8cK8hCyRQCp52nVuPLnLL71afkRvRcFibSwHMjGFT8bm))
* **Note**: Fees only collected for tokens with referral token accounts (currently SOL)
* Supports development and maintenance

### Security

* 🔐 Private keys never leave your machine
* 🛡️ All API calls use HTTPS
* ⚠️ Never commit `.env` files to version control

## 🐛 Troubleshooting

### Common Issues

1. **"PRIVATE\_KEY environment variable is required"**
   * Copy `env.example` to `.env` and set your private key
2. **"Invalid PRIVATE\_KEY format"**
   * Use base58 encoded private key (from Phantom wallet export)
3. **Connection timeouts**
   * Try different RPC URL or increase `REQUEST_TIMEOUT`

## 🎉 Ready to Trade!

Your Jupiter MCP server is ready for Solana DeFi interactions! 🚀
