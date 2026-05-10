# 📢 Reddit Post — sol-agent-wallet

---

## r/solana (2M+ subs)

**Title:** I built the first AI agent that can actually DO things on Solana, not just look 👀

**Body:**

Every Solana "AI agent" out there is read-only. You can ask "what's my balance?" but you can't actually do anything.

So I built one that can execute transactions.

**sol-agent-wallet** lets you ask Claude/Cursor:

> *"Send 0.1 SOL to wallet 7EcD..."*
>
> *"Swap 0.5 SOL for USDC on Jupiter"*
>
> *"What's my portfolio worth?"*

**How it works:**
- Read-only mode: No key needed, works out of the box
- Write mode: Set your private key as an env var, and your AI agent can sign + send transactions
- Your key never leaves your machine — it's only used for local signing

**Why this matters:**
Every other Solana MCP server is read-only. This is the first one that can actually execute swaps, transfers, and manage your wallet through natural language.

```json
{
  "mcpServers": {
    "solana-wallet": {
      "command": "uvx",
      "args": ["sol-agent-wallet"]
    }
  }
}
```

Then ask Claude: *"Swap 0.5 SOL for USDC"*

Open source (MIT): github.com/yksanjo/sol-agent-wallet

Would love feedback! What else should an AI agent be able to do on Solana?

---

## r/solana_dev (100K+ devs)

**Title:** sol-agent-wallet: Open-source write-capable Solana AI agent (MCP server with transaction execution)

**Body:**

Hey devs — I built an open-source MCP server for Solana that can actually execute transactions, not just read data.

**Stack:** Python, solders, Jupiter API, Solana RPC

**Key features:**
- `sol_balance` — SOL + token balances
- `sol_portfolio` — Full portfolio with USD value
- `sol_quote` — Swap quotes via Jupiter
- `sol_search` — Token search
- `sol_transfer` — Send SOL (write)
- `sol_swap` — Execute token swaps via Jupiter (write)

**Security model:**
- Read-only by default (no key needed)
- Write mode requires `SOLANA_PRIVATE_KEY` env var
- Key stays local, only used for signing
- All transactions return Solscan links for verification

**GitHub:** github.com/yksanjo/sol-agent-wallet

PRs welcome! Looking to add:
- SPL token transfers
- Staking (Marinade/Jito)
- Lending (Marginfi)
- NFT buying (Tensor)
- DCA orders

What would you want an AI agent to do on Solana?
