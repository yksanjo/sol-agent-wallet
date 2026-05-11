# Submission: Solana Foundation developer resources

**Target candidates** (in order of leverage):
1. https://github.com/solana-foundation/developer-content — Powers docs at solana.com/developers. PR a tool/MCP page under `content/cookbook/` or `content/resources/`.
2. https://solana.com/developers/ecosystem — Listing form, not a PR. Submit via the form once that exists at `solana.com/ecosystem/submit` (check current URL).
3. Discord: **Solana Tech** server, `#tools` and `#mcp-builders` channels.

## PR Title (for developer-content)

```
docs: add Sol Agent Wallet to MCP / AI agent tooling
```

## PR Body

```markdown
Adds a short page covering Sol Agent Wallet, an MCP server that lets AI coding agents and chat clients execute Solana transactions on behalf of users.

**Why this fits the developer-content site:**
- MCP is the emerging standard for tool-using AI agents; Solana needs a write-capable reference implementation in this space
- The repo includes copy-paste configs for the six major MCP clients (Claude Desktop, Cursor, Cline, Continue.dev, Zed, Windsurf), which removes a real friction point for builders
- Devnet-by-default + per-tx SOL cap are honest safety defaults that I think the docs site should be promoting for any AI-agent tooling

**Suggested placement:** under `content/cookbook/agents/` or wherever MCP / AI content is grouped. Happy to move it if there's a better section.

**External links to add:**
- Repo: https://github.com/yksanjo/sol-agent-wallet
- PyPI: https://pypi.org/project/sol-agent-wallet/
```

## Diff entry — a new file

Create `content/cookbook/agents/sol-agent-wallet.md`:

```markdown
---
title: Sol Agent Wallet (MCP)
description: Run a write-capable Solana MCP server for Claude, Cursor, and other AI agents.
tags: [agents, mcp, jupiter, devtools]
---

[Sol Agent Wallet](https://github.com/yksanjo/sol-agent-wallet) is a Model Context Protocol (MCP) server that lets AI agents execute Solana transactions through natural language — swaps via Jupiter, SOL transfers, balance and portfolio queries.

## Install

\`\`\`bash
uvx sol-agent-wallet
\`\`\`

Add to your MCP client config (Claude Desktop, Cursor, etc.):

\`\`\`json
{
  "mcpServers": {
    "sol-agent-wallet": {
      "command": "uvx",
      "args": ["sol-agent-wallet"]
    }
  }
}
\`\`\`

## Enable write mode

\`\`\`bash
export SOLANA_PRIVATE_KEY='your_burner_wallet_base58_key'
export SOLANA_NETWORK=mainnet-beta   # devnet by default
export SOLANA_MAX_TX_SOL=1.0         # per-tx cap, configurable
uvx sol-agent-wallet
\`\`\`

See the [install configs](https://github.com/yksanjo/sol-agent-wallet/tree/main/install) for every major MCP client.
```

## Notes for the submitter

- Match whatever frontmatter schema the rest of the cookbook uses — check a neighboring file before opening the PR.
- The Solana Foundation team also takes ecosystem submissions via the form at solana.com/developers/ecosystem; submit there as well even if the docs PR is pending.
- After the PR is open, post a one-liner in the Solana Tech Discord `#tools` channel with the PR link.
