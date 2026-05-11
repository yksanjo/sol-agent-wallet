# r/solana — self post

**Subreddit rules check before posting:** r/solana allows tool launches but bans "shilling." Lead with utility, not hype. No price talk.

**Flair:** `Dev / Tools` (or whatever the current dev flair is)

---

## Title

```
I built a Solana MCP server that lets Claude / Cursor actually execute transactions (not just read)
```

## Body

```markdown
**TL;DR:** `uvx sol-agent-wallet` — gives any MCP-compatible AI agent (Claude Desktop, Cursor, Cline, Continue.dev, Zed, Windsurf) the ability to swap tokens via Jupiter and send SOL, through natural language. Devnet by default, MIT licensed.

Repo: https://github.com/yksanjo/sol-agent-wallet
PyPI: https://pypi.org/project/sol-agent-wallet/

---

### Why I built this

I was using the existing Solana MCP servers and got frustrated — they all let your agent *read* on-chain state but none of them can actually *do* anything. "What's my balance?" works. "Swap 0.1 SOL for USDC" doesn't.

So I wrote one that signs and submits transactions.

### What it does (v0.1.0)

- `sol_swap` — execute a Jupiter swap
- `sol_transfer` — send SOL to an address
- `sol_balance`, `sol_portfolio`, `sol_quote`, `sol_search` — the usual read ops

The agent calls these tools through MCP. You see the tool call in your client's UI (Claude Desktop shows an approval prompt) and the transaction goes through.

### Safety defaults

This is the part that took the longest to get right. Defaults are intentionally paranoid:

- **Devnet by default.** Mainnet is `export SOLANA_NETWORK=mainnet-beta`. You can't accidentally trade real SOL on day one.
- **Per-tx SOL cap.** Default 1.0 SOL, configurable via `SOLANA_MAX_TX_SOL`. A malformed prompt can't drain a wallet in one shot.
- **Read-only without `SOLANA_PRIVATE_KEY`.** No key, no write tools registered — the agent literally can't see them.
- **Burner wallet recommended.** Don't paste your daily driver. README has full instructions.

### How it works under the hood

Python, MCP over stdio, Jupiter v6 for swaps, standard Solana RPC for transfers. solders for signing. ~500 LOC of actual code. Test suite covers config parsing, key handling, and tx-cap enforcement.

### Install

One-liner for Claude Desktop / Cursor / etc.:

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

Configs for all six major MCP clients are in [`install/`](https://github.com/yksanjo/sol-agent-wallet/tree/main/install).

### What I'd love feedback on

1. Are there other Solana protocols you'd want exposed as MCP tools? Staking and lending are next.
2. Is the 1 SOL default tx cap too high / too low?
3. Anything obviously wrong in how I'm building / signing transactions?

PRs welcome. Roast it.
```

---

## Reply prep

- **"How is this different from [X]"** — name the read-only one, point at the comparison table in the README. Don't trash; acknowledge their strengths (e.g., Helius has better indexer access).
- **"Isn't this dangerous?"** — explicitly walk through the four safety defaults. Mention burner wallet. Mention you've never seen a production system *not* eventually have a bug — that's why caps exist.
- **"Why not [Anchor / Rust]?"** — fair question. Python because MCP servers run as subprocesses of agent UIs, and Python's startup cost is fine for that. Rust port would be welcome contribution.
- **"Can it stake / lend?"** — not yet, on roadmap; ask which protocol they'd want first.
