# Submission: punkpeye/awesome-mcp-servers

**Target:** https://github.com/punkpeye/awesome-mcp-servers
**Section:** `README.md` → "Finance & Fintech" (or "Blockchain / Crypto" if that section exists at submission time — verify before editing).

## PR Title

```
Add sol-agent-wallet (write-capable Solana MCP server)
```

## PR Body

```markdown
Adds `sol-agent-wallet` to the list — first MCP server that lets agents **execute** Solana transactions (swap, send) instead of just reading state.

**Why it's worth listing:**
- Different from existing Solana MCPs (Helius, QuickNode, etc.) which are read-only
- Works with Claude Desktop, Cursor, Cline, Continue.dev, Zed, Windsurf via copy-paste configs in [`install/`](https://github.com/yksanjo/sol-agent-wallet/tree/main/install)
- Safe defaults: devnet-by-default, 1 SOL per-tx cap, read-only without a private key

**Listing details:**
- Name: Sol Agent Wallet
- Repo: https://github.com/yksanjo/sol-agent-wallet
- Language: Python (`uvx sol-agent-wallet`)
- License: MIT
- Category: Finance / Blockchain

I've followed the contribution guidelines: alphabetical placement, single-line description, valid URL. Happy to adjust if you want a different section or category.
```

## Diff entry

Most "awesome" lists use this single-line format. Insert alphabetically under the appropriate category. punkpeye's list uses emoji prefixes for language — Python is `🐍`.

```markdown
- [Sol Agent Wallet](https://github.com/yksanjo/sol-agent-wallet) 🐍 - Write-capable Solana MCP server. Swap, send SOL, and manage wallets via Jupiter and Solana RPC. Devnet-by-default with a per-transaction SOL cap.
```

If the list uses badges instead of emoji, swap the emoji for `<img src="https://img.shields.io/badge/python-3776AB?logo=python&logoColor=white" />` per repo convention.

## Notes for the submitter

- Check current category names before opening (they reorganize periodically).
- Run their `awesome-lint` if a CI is set up.
- If they want it under "AI Tools" or "Agents" instead, fine — let the maintainer decide.
