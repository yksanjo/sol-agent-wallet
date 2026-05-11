# Solana Tech Discord — #showcase

**Server:** Solana Tech (the largest Solana dev Discord)
**Channel:** `#showcase` (or `#tools` / `#mcp-builders` if those exist at post time — check first)
**Format:** Single message, Discord allows ~2000 chars. Use plain text + one link, attachments separate.

---

## Message

```
just shipped **sol-agent-wallet** v0.1.0 — first write-capable Solana MCP server

every existing Solana MCP is read-only. this one signs + submits transactions, so your AI agent (Claude / Cursor / Cline / etc) can actually swap and send through natural language.

**install:** `uvx sol-agent-wallet`

**what's in:**
• `sol_swap` — Jupiter v6 swap
• `sol_transfer` — send SOL
• `sol_balance` / `sol_portfolio` / `sol_quote` / `sol_search` — read ops

**safety defaults (this part i obsessed over):**
• devnet by default — mainnet requires explicit opt-in
• 1 SOL per-tx cap, configurable
• read-only unless `SOLANA_PRIVATE_KEY` is set
• full security write-up in SECURITY.md

**install configs for every MCP client** (Claude Desktop, Cursor, Cline, Continue.dev, Zed, Windsurf): https://github.com/yksanjo/sol-agent-wallet/tree/main/install

**repo:** https://github.com/yksanjo/sol-agent-wallet
**pypi:** https://pypi.org/project/sol-agent-wallet/
**license:** MIT

would love feedback — what protocols should I add next? staking (Marinade/Jito) and lending (MarginFi/Kamino) are top of my list but happy to be redirected.
```

---

## Attachments

1. The 60-second demo GIF (under 8 MB or Discord won't inline it).
2. A screenshot of the README "Quick Install" matrix as a fallback for anyone whose Discord client doesn't render the GIF.

## Reply prep

- **"is this safe??"** → walk through the four defaults. Pin the SECURITY.md.
- **"can I add X protocol?"** → "yes — open a PR or an issue with the protocol you want, I'll prioritize."
- **DMs about partnerships / sponsorship** → polite no for now, focus on adoption.
