# Changelog

All notable changes are documented here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — unreleased

First public release.

### Added
- MCP server with six tools: `sol_balance`, `sol_portfolio`, `sol_quote`, `sol_search`, `sol_transfer`, `sol_swap`
- `WalletManager` supporting env-var, file, and in-memory keypairs
- Jupiter v6 integration for swap quotes and execution
- Solana RPC client with transfer and confirmation handling
- `SOLANA_NETWORK` config (devnet default), `SOLANA_RPC_URL` override
- `SOLANA_MAX_TX_SOL` per-transaction cap (default 1.0 SOL)
- `[project.scripts]` entry point so `uvx sol-agent-wallet` works
- One-click install configs for Claude Desktop, Cursor, Cline, Continue.dev, Zed, Windsurf
- GitHub Actions workflow for PyPI trusted publishing on tag push
- Test suite covering wallet manager, config loading, and tx-cap enforcement
- `SECURITY.md` with disclosure policy and threat model

### Security defaults
- Network defaults to **devnet** — `SOLANA_NETWORK=mainnet-beta` required to touch real funds
- Per-transaction SOL cap of **1.0** by default — raise with `SOLANA_MAX_TX_SOL`
- Solscan links auto-append `?cluster=devnet` on non-mainnet networks

[0.1.0]: https://github.com/yksanjo/sol-agent-wallet/releases/tag/v0.1.0
