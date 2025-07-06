# Jupiter Ultra MCP Server

A Python MCP (Model Context Protocol) server that provides tools to access the [Jupiter Ultra API](https://dev.jup.ag/docs/ultra-api/) for Solana blockchain interactions.

## 🚀 Features

- **Complete Jupiter Ultra API Integration**: Access all Jupiter Ultra endpoints
- **Clean Architecture**: Separated API client and MCP server for better testability
- **Secure Wallet Management**: Uses your Solana private key for transactions
- **Async Operations**: Built with FastMCP for high-performance async operations
- **Comprehensive Testing**: Includes both API unit tests and MCP integration tests
- **Type-Safe**: Full TypeScript-style type annotations for Python
- **Error Handling**: Robust error handling with detailed error messages

## 🛠️ Available Tools

| Tool | Description | Parameters | Cost |
|------|-------------|------------|------|
| `get_order` | Get a swap order/quote from Jupiter Ultra API | `input_mint`, `output_mint`, `amount`, `taker?`, `referral_account?`, `referral_fee?` | **FREE** |
| `execute_order` | Execute a signed swap transaction | `signed_transaction`, `request_id` | **PAID** |
| `get_balances` | Get token balances for a wallet | `wallet_address?` | **FREE** |
| `get_shield` | Get token security information | `mints` | **FREE** |
| `search_token` | Search for tokens by symbol, name, or address | `query` | **FREE** |

## 📋 Available Resources

| Resource | Description |
|----------|-------------|
| `wallet://info` | Get wallet configuration details |

## 📁 Project Structure

```
jupiter-ultra-mcp/
├── src/
│   ├── __init__.py
│   ├── jupiter_ultra_api.py    # Jupiter Ultra API client class
│   └── server.py               # MCP server with tool registrations
├── tests/
│   ├── conftest.py             # Pytest configuration
│   ├── test_jupiter_ultra_api.py    # API unit tests
│   └── test_jupiter_ultra_mcp.py    # MCP server integration tests
├── run_server.py               # Server entry point
├── env.example                 # Environment variables template
├── pyproject.toml             # Dependencies and project config
└── README.md                  # This file
```

## 🔧 Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management

### Setup
1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd jupiter-ultra-mcp
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Set your environment variables in `.env`:**
   ```bash
   SOLANA_RPC_URL=https://api.devnet.solana.com
   PRIVATE_KEY=your_base58_encoded_private_key_here
   SOLANA_NETWORK=devnet
   REQUEST_TIMEOUT=30
   ```

## 🎯 Usage

### Starting the Server
```bash
# Using the entry point script
python run_server.py

# Or directly with uv
uv run python run_server.py
```

### Server Output
```
============================================================
🚀 Jupiter Ultra MCP Server
============================================================
📡 Solana Network: devnet
🔗 RPC URL: https://api.devnet.solana.com
💼 Wallet Address: Your_Wallet_Address

🔧 Available Tools:
  • get_order - Get swap quotes from Jupiter Ultra
  • execute_order - Execute signed swap transactions
  • get_balances - Get token balances for a wallet
  • get_shield - Get token security information
  • search_token - Search for tokens

📋 Available Resources:
  • wallet://info - Get wallet configuration details

🎯 Server starting...
============================================================
```

## 🧪 Testing

The project includes comprehensive tests for both the API client and MCP server:

### Test Categories

**Free Tests** (No SOL required):
- ✅ `get_order` - Getting quotes/orders (no execution)
- ✅ `get_balances` - Checking wallet balances
- ✅ `get_shield` - Token security checks
- ✅ `search_token` - Token search functionality
- ✅ `execute_order` - Mocked execution testing
- ✅ Error handling and edge cases

**Paid Tests** (Requires funded wallet):
- 💰 Real balance checking with your wallet
- 💰 Real order creation (ready for execution)
- 💰 Real token security verification

### Running Tests

```bash
# Run free tests only (default)
uv run python -m pytest tests/ -v

# Run all tests including paid tests
uv run python -m pytest tests/ -v --run-paid-tests

# Run specific test files
uv run python -m pytest tests/test_jupiter_ultra_api.py -v
uv run python -m pytest tests/test_jupiter_ultra_mcp.py -v

# Run with detailed output for paid tests
uv run python -m pytest tests/ -v --run-paid-tests -s
```

## 💡 Important Notes

### Free vs Paid Operations

- **🆓 FREE**: `get_order`, `get_balances`, `get_shield`, `search_token` - These only make API calls and don't cost SOL
- **💰 PAID**: `execute_order` - This requires a signed transaction and will spend SOL for the actual swap

### Transaction Execution

The `execute_order` tool expects an **already signed transaction**. The signing process must be handled separately, typically by:

1. Getting an order with `get_order`
2. Signing the returned transaction with your private key
3. Passing the signed transaction to `execute_order`

### Security

- ⚠️  **Never commit your `.env` file or private keys to version control**
- 🔐 Your private key is only used locally and never sent to external APIs
- 🛡️  All API calls use HTTPS for secure communication

## 🛠️ Development

### Project Architecture

1. **`src/jupiter_ultra_api.py`**: Clean API client class with all Jupiter Ultra methods
2. **`src/server.py`**: MCP server that registers API methods as tools
3. **`tests/`**: Comprehensive test suite with both unit and integration tests

### Adding New Features

To add a new Jupiter Ultra API endpoint:

1. Add the method to `JupiterUltraAPI` class in `src/jupiter_ultra_api.py`
2. Register it as a tool in `src/server.py` using `mcp.tool()(api.new_method)`
3. Add tests in `tests/test_jupiter_ultra_api.py`

## 📚 API Documentation

For detailed information about Jupiter Ultra API endpoints, visit:
- [Jupiter Ultra API Documentation](https://dev.jup.ag/docs/ultra-api/)

## 🐛 Troubleshooting

### Common Issues

1. **"PRIVATE_KEY environment variable is required"**
   - Make sure you've copied `env.example` to `.env` and set your private key

2. **"Invalid PRIVATE_KEY format"**
   - Ensure your private key is base58 encoded (from Phantom wallet export)

3. **Connection timeouts**
   - Try using a different RPC URL (QuickNode, Helius, etc.)
   - Increase `REQUEST_TIMEOUT` in your `.env`

### Getting Help

- Check the [Jupiter Ultra API docs](https://dev.jup.ag/docs/ultra-api/)
- Review test files for usage examples
- Ensure your wallet has sufficient SOL for devnet testing

## 🎉 Ready to Use!

Your Jupiter Ultra MCP server is now ready for Solana DeFi interactions! 🚀
