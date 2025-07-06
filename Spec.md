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

## Tools to Implement

- **get-order**: https://dev.jup.ag/docs/ultra-api/get-order
- **execute-order**: https://dev.jup.ag/docs/ultra-api/execute-order
- **get-balances**: https://dev.jup.ag/docs/ultra-api/get-balances
- **get-shield**: https://dev.jup.ag/docs/ultra-api/get-shield
- **search-token**: https://dev.jup.ag/docs/ultra-api/search-token

## Testing

### Free Tests
- Test `get-balances` for the provided private key
- Test `get-orders` functionality
- Test `search-token` functionality
- Test `get-shield` functionality

### Paid Tests (Optional)
- Test `execute-order` with minimal SOL amount (0.01 SOL → USDC → SOL)
- Only run when `--run-paid-tests` flag is passed to pytest


## Notes

- Keep code simple, leverage existing libraries
- Dependencies managed with `uv` in `pyproject.toml`
