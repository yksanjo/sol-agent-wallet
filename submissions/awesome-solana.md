# Submission: awesome-solana

**Target candidates** (check which is most active before submitting):
- https://github.com/solana-developers/awesome-solana  ← preferred
- https://github.com/CryptoFlow88/awesome-solana
- https://github.com/abhi3700/awesome-solana

**Section:** `README.md` → "Tools" or "Wallets" (varies — check the TOC).

## PR Title

```
Add Sol Agent Wallet — Solana MCP server for AI agents
```

## PR Body

```markdown
Adds `sol-agent-wallet` to the list.

**What it is:** A Solana MCP (Model Context Protocol) server that lets AI agents like Claude and Cursor execute on-chain actions through natural language: swap tokens via Jupiter, send SOL, query balances and portfolios.

**Why this matters for Solana devs:**
- Bridges the AI agent ecosystem (MCP) and the Solana stack — first write-capable implementation
- Built on Jupiter v6 + standard Solana RPC; no proprietary middleware
- Pure Python, MIT, easy to fork and add your own protocol (Marinade, Tensor, etc.)
- Safety defaults: devnet-first, per-tx SOL cap, read-only without a key

**Listing details:**
- Name: Sol Agent Wallet
- Repo: https://github.com/yksanjo/sol-agent-wallet
- Tags: MCP, AI agents, Jupiter, wallet, dev tools
- Install: `uvx sol-agent-wallet`

Let me know if you'd like me to place it under a different section.
```

## Diff entry

```markdown
- [Sol Agent Wallet](https://github.com/yksanjo/sol-agent-wallet) - MCP server giving AI agents (Claude, Cursor, Cline) the ability to swap, send, and manage SOL via natural language. Jupiter + Solana RPC, Python, MIT.
```

## Notes for the submitter

- If `solana-developers/awesome-solana` is the choice, follow its CONTRIBUTING.md exactly. They are strict about alphabetical order and the trailing period.
- Some forks accept entries via Issues rather than PRs — check the README footer.
