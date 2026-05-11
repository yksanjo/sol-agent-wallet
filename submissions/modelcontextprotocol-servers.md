# Submission: modelcontextprotocol/servers

**Target:** https://github.com/modelcontextprotocol/servers
**Section:** `README.md` → "🌎 Community Servers" (alphabetical, look for `s`)

## PR Title

```
docs: add sol-agent-wallet (write-capable Solana MCP server)
```

## PR Body

```markdown
Adds `sol-agent-wallet` to the Community Servers list.

**What it is:** A Python MCP server that gives any MCP-compatible client (Claude Desktop, Cursor, Cline, Continue.dev, Zed, Windsurf) the ability to **execute** Solana transactions — swap tokens via Jupiter, send SOL — through natural language. Unlike the existing read-only Solana MCP servers, this one signs transactions.

**Safety defaults:**
- Defaults to Solana devnet — mainnet requires explicit `SOLANA_NETWORK=mainnet-beta`
- Per-transaction SOL cap (default 1.0, configurable via `SOLANA_MAX_TX_SOL`)
- Read-only mode by default — write tools only register when `SOLANA_PRIVATE_KEY` is set

**Install:** `uvx sol-agent-wallet`

- Repo: https://github.com/yksanjo/sol-agent-wallet
- PyPI: https://pypi.org/project/sol-agent-wallet/
- License: MIT
- Author: @yksanjo

Tested with Claude Desktop and Cursor. Test suite covers config parsing, wallet management, and tx-cap enforcement.
```

## Diff entry

The community list is alphabetical. Insert under `S`, after the existing Solana read-only entry (if present) or in alphabetical position:

```markdown
- **[Sol Agent Wallet](https://github.com/yksanjo/sol-agent-wallet)** - Write-capable Solana MCP server. Swap tokens via Jupiter, send SOL, manage wallets through natural language. Devnet-by-default for safety.
```

## Notes for the submitter

- The official `servers` repo is curated. If they ask, point out: write-capable (existing Solana entries are read-only), devnet default, MIT, tests included.
- If they reject community PRs in favor of curated additions, fall back to opening a discussion in the repo's "Server Submissions" thread.
