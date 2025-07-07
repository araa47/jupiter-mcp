# Jupiter Ultra MCP Server

A Python MCP (Model Context Protocol) server for the [Jupiter Ultra API](https://dev.jup.ag/docs/ultra-api/) - Solana's premier DEX aggregator.

## 🚀 Features

- **Jupiter Ultra API Integration**: Access all Jupiter Ultra endpoints
- **Secure Wallet Management**: Uses your Solana private key for transactions
- **Built-in Referral System**: Automatically includes referral fees for development support
- **Comprehensive Testing**: Safe testing with mock and real trade execution
- **Type-Safe**: Full type annotations for Python

## ⚡ Quick Start (MCP Configuration)

You need:
- [uv](https://docs.astral.sh/uv/getting-started/installation/) -> Python dependency manager
- [npx](https://docs.npmjs.com/cli/v10/commands/npx) (comes with Node.js) -> Used to run Node packages without installing them globally (temporarily used since cursor doesn't support )

Once uv is installed, restart your shell and add this to your MCP client configuration:

Cursor
```json
{
  "mcpServers": {
    "jupiter-ultra-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/araa47/jupiter-ultra-mcp",
        "jupiter-ultra-mcp"
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

### Alternative Configuration (Using .env file)

If you prefer to load environment variables from a `.env` file to avoid storing sensitive data in your MCP configuration:

```json
{
  "mcpServers": {
    "jupiter-ultra-mcp": {
      "command": "npx",
      "args": [
        "envmcp",
        "--env-file",
        ".env",
        "uvx",
        "--from",
        "git+https://github.com/araa47/jupiter-ultra-mcp",
        "jupiter-ultra-mcp",
        "$SOLANA_RPC_URL",
        "$PRIVATE_KEY"
      ]
    }
  }
}
```

This approach uses `envmcp` to securely load your PRIVATE_KEY from a `.env` file without exposing it in configuration files.

### Environment Variables Required:
- `PRIVATE_KEY`: Your base58 encoded Solana private key (from Phantom wallet export)
- Optional: Override `SOLANA_RPC_URL` if you have a custom RPC endpoint

## 🛠️ Available Tools

| Tool | Description | Parameters | Cost |
|------|-------------|------------|------|
| `get_swap_quote` | Get a swap quote and unsigned transaction | `input_mint`, `output_mint`, `amount` | **FREE** |
| `execute_swap_transaction` | Execute a signed swap transaction | `transaction`, `request_id` | **PAID** |
| `get_balances` | Get token balances for a wallet | `wallet_address?` | **FREE** |
| `get_shield` | Get token security information | `mints` | **FREE** |
| `search_token` | Search for tokens | `query` | **FREE** |


## 🔧 Alternative Installation (Development)

For local development or testing:

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Setup
```bash
git clone https://github.com/araa47/jupiter-ultra-mcp
cd jupiter-ultra-mcp
uv sync
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
- Mock execution tests
- API quote/balance checks
- Token searches and security checks
- Error handling validation

**💰 Paid Tests** (Requires `--run-paid-tests` flag):
- Real trade execution on mainnet
- Uses tiny amounts (0.0001 SOL ≈ $0.015)
- Full transaction signing and broadcasting

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
- **Paid tests clearly marked** with `@pytest.mark.paid`
- **Minimal trade amounts** (0.0001 SOL) for real execution
- **Clear warnings** before spending real money
- **Transaction confirmations** with blockchain signatures

## 💡 Important Notes

### Free vs Paid Operations
- **🆓 FREE**: `get_swap_quote`, `get_balances`, `get_shield`, `search_token` - API calls only
- **💰 PAID**: `execute_swap_transaction` - Executes real trades and spends SOL

### Automatic Referral System
- All orders include a 255 basis point (2.55%) referral fee (maximum allowed)
- Referral wallet: `8cK8hCyRQCp52nVuPLnLL71afkRvRcFibSwHMjGFT8bm` ([Referral Dashboard](https://referral.jup.ag/))
- **Note**: Fees only collected for tokens with referral token accounts (currently SOL)
- Supports development and maintenance

### Security
- 🔐 Private keys never leave your machine
- 🛡️ All API calls use HTTPS
- ⚠️ Never commit `.env` files to version control

## 🐛 Troubleshooting

### Common Issues

1. **"PRIVATE_KEY environment variable is required"**
   - Copy `env.example` to `.env` and set your private key

2. **"Invalid PRIVATE_KEY format"**
   - Use base58 encoded private key (from Phantom wallet export)

3. **Connection timeouts**
   - Try different RPC URL or increase `REQUEST_TIMEOUT`

## 🎉 Ready to Trade!

Your Jupiter Ultra MCP server is ready for Solana DeFi interactions! 🚀
