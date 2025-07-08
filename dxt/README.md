# Jupiter MCP Desktop Extension (DXT)

A Claude Desktop Extension (DXT) for the Jupiter MCP Server - enabling Solana DEX trading through Jupiter's APIs directly in Claude Desktop.

## 🚀 Quick Installation

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

**Note**: Jupiter MCP is installed directly from the GitHub repository `https://github.com/araa47/jupiter-mcp` using uvx, not from PyPI.

### Installation Methods

#### Option 1: Double-Click Installation (Recommended)
1. Download `jupiter-mcp-0.1.0.dxt` from releases
2. Double-click the `.dxt` file
3. Claude Desktop will automatically install the extension
4. Follow the configuration prompts

#### Option 2: Manual Installation
1. Download `jupiter-mcp-0.1.0.dxt`
2. Open Claude Desktop
3. Go to Settings → Extensions
4. Click "Install Extension" and select the `.dxt` file

### Configuration

During installation, you'll be prompted to configure:

#### Installation Requirements Check
- ✅ Confirms `npx` and `uv` are installed on your system
- ❌ If not installed, follow the prerequisites above

#### Environment File Path
Provide the path to your `.env` file containing:

```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
PRIVATE_KEY=your_base58_encoded_private_key_here
SOLANA_NETWORK=mainnet-beta
REQUEST_TIMEOUT=30
```

**Example paths:**
- macOS/Linux: `/Users/yourname/.env` or `/home/yourname/.env`
- Windows: `C:\Users\yourname\.env`

## 🔧 How It Works

1. **uvx Installation**: The extension uses `uvx` to install Jupiter MCP directly from GitHub
2. **Environment Loading**: Your `.env` file provides secure credential storage
3. **MCP Communication**: Claude Desktop communicates with the Jupiter MCP server
4. **Solana Trading**: Execute trades and manage limit orders through Jupiter APIs

## 🛠 Available Tools

Once installed, you'll have access to:

### Trading Tools
- `get_swap_quote` - Get quotes for immediate swaps
- `execute_swap_transaction` - Execute trades (requires SOL for fees)
- `create_limit_order` - Create conditional limit orders
- `execute_limit_order` - Execute limit orders (requires SOL for fees)
- `cancel_limit_order` - Cancel individual orders
- `cancel_limit_orders` - Cancel multiple orders

### Information Tools
- `get_balances` - Check wallet token balances
- `get_shield` - Get token security information
- `search_token` - Find tokens by name/symbol
- `get_limit_orders` - View active/historical orders

## 🔒 Security Notes

- **Private Keys**: Store your private key securely in the `.env` file
- **File Permissions**: Ensure your `.env` file has restricted permissions
- **Network**: Use mainnet-beta for production, devnet for testing
- **Backup**: Always backup your private keys securely

## 🐛 Troubleshooting

### Extension Won't Install
- Ensure you have the latest Claude Desktop version
- Check that both `npx` and `uvx` are installed and in your PATH

### Server Won't Start
Check Claude Desktop logs for debug messages starting with `[Jupiter Wrapper Debug]`:

**Common Issues:**
- `ENV_FILE_PATH not provided` → Check extension configuration
- `uvx not found` → Install uv/uvx from official docs
- `No solution found when resolving dependencies` → This should be fixed with git installation

### Permission Errors
- Ensure your `.env` file exists at the specified path
- Check file permissions allow reading

### API Errors
- Verify your `SOLANA_RPC_URL` is accessible
- Confirm your `PRIVATE_KEY` is valid base58 format
- Check your wallet has SOL for transaction fees

## 📞 Support

- **Issues**: https://github.com/araa47/jupiter-mcp/issues
- **Documentation**: https://github.com/araa47/jupiter-mcp#readme
- **Jupiter API**: https://station.jup.ag/api-docs

## 📄 License

MIT License - see the main repository for details.
