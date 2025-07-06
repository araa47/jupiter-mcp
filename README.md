# Jupiter Ultra MCP Server

A Python MCP (Model Context Protocol) server for the [Jupiter Ultra API](https://dev.jup.ag/docs/ultra-api/) - Solana's premier DEX aggregator.

## 🚀 Features

- **Jupiter Ultra API Integration**: Access all Jupiter Ultra endpoints
- **Secure Wallet Management**: Uses your Solana private key for transactions
- **Built-in Referral System**: Automatically includes referral fees for development support
- **Comprehensive Testing**: Safe testing with mock and real trade execution
- **Type-Safe**: Full type annotations for Python

## 🛠️ Available Tools

| Tool | Description | Parameters | Cost |
|------|-------------|------------|------|
| `get_order` | Get a swap order/quote | `input_mint`, `output_mint`, `amount` | **FREE** |
| `execute_order` | Execute a signed swap transaction | `transaction`, `request_id` | **PAID** |
| `get_balances` | Get token balances for a wallet | `wallet_address?` | **FREE** |
| `get_shield` | Get token security information | `mints` | **FREE** |
| `search_token` | Search for tokens | `query` | **FREE** |

## 🔧 Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Setup
```bash
git clone <repository-url>
cd jupiter-ultra-mcp
uv sync
cp env.example .env
# Edit .env with your configuration
```

### Environment Variables
```bash
SOLANA_RPC_URL=https://api.devnet.solana.com
PRIVATE_KEY=your_base58_encoded_private_key_here
SOLANA_NETWORK=devnet
REQUEST_TIMEOUT=30
```

## 🎯 Usage

```bash
# Start the server
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
- **🆓 FREE**: `get_order`, `get_balances`, `get_shield`, `search_token` - API calls only
- **💰 PAID**: `execute_order` - Executes real trades and spends SOL

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
