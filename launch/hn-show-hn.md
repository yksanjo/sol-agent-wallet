# Hacker News — Show HN

**When:** Tuesday or Wednesday, ~08:00 PT (peak HN traffic). Avoid Mondays (front page is sticky from weekend posts) and Fridays.

**Submitter etiquette:**
- Submit yourself. Don't have anyone else submit.
- Don't ask for upvotes anywhere; HN penalizes detected vote rings hard.
- Be present in the comments for the first 2–3 hours. The algorithm rewards activity.

---

## Title

```
Show HN: Sol Agent Wallet – Solana MCP server that lets AI agents actually swap and send
```

(Title length: 80 chars budget. This is 78.)

**Notes on the title:**
- "actually" is doing work — implies a contrast with read-only competitors without naming them.
- "Solana MCP server" front-loads the keywords HN's algorithm and humans scan for.
- "swap and send" is concrete; avoid "manage" or "interact with" which are vague.

## URL

```
https://github.com/yksanjo/sol-agent-wallet
```

(GitHub front-pages well on Show HN. Avoid the PyPI page — looks like marketing.)

---

## First comment (post this immediately after submitting)

```
Hi HN — author here. Quick context on what's actually new:

Every existing Solana MCP server is read-only. Your AI agent can ask "what's my balance?" but it can't sign a transaction. This one can — it exposes `sol_swap` (Jupiter v6) and `sol_transfer` (native SOL) as MCP tools alongside the usual read ops.

Why MCP and not a CLI/SDK: the Model Context Protocol is becoming the standard interface between LLM clients (Claude Desktop, Cursor, Cline, Zed, Windsurf, Continue.dev) and external tools. Writing a Solana MCP server means every one of those clients gets Solana writes for free.

The safety defaults are intentionally paranoid:

  - Defaults to devnet. Mainnet requires SOLANA_NETWORK=mainnet-beta.
  - Per-tx SOL cap (default 1.0, configurable). A malformed LLM tool call can't drain a wallet in one shot.
  - Write tools are only registered if SOLANA_PRIVATE_KEY is set. No key, no transfer/swap tools visible to the agent.
  - README explicitly recommends a burner wallet.

The interesting thing I learned building this: the right authorization layer for agent-driven transactions is *the agent client's tool-approval UI*, not the MCP server itself. Claude Desktop shows you the exact tool call before it runs; Cursor does the same. The server's job is to enforce defense-in-depth limits (caps, network gating, key handling) — not to second-guess the user's intent.

Stack: Python, mcp SDK, solders, httpx. Jupiter v6 for swaps, plain RPC for transfers. ~500 LOC. Tests cover config, wallet manager, and the tx-cap enforcement paths.

Happy to go deep on:
  - The trust-boundary decisions (why the cap is 1.0 SOL and not 0.1)
  - How I think about composing this with CrewAI or LangChain for multi-agent treasuries
  - Why I chose stdio MCP over SSE / HTTP transports

Roast it.
```

---

## Things to have ready for the comments

- A clean GIF or asciinema cast at a URL you control (not just GitHub raw — they sometimes 404 under HN load)
- The full test output from `pytest -v` ready to paste if someone asks for proof
- A one-paragraph answer for the inevitable "this is just a wrapper around Jupiter" comment — yes, plus key management + safety defaults + MCP plumbing, and those are 80% of the actual work
