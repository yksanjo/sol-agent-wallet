# X / Twitter thread — sol-agent-wallet v0.1.0

**When:** ~17:00 JST / 00:00 PT for global reach.
**Tag:** @solana @jupiterexchange @AnthropicAI @cursor_ai (one per post max, naturally).

---

## Post 1 — Hook

> Every Solana MCP server is read-only. You can ask Claude "what's my balance?" but you can't actually do anything.
>
> So I built **sol-agent-wallet** — the first write-capable Solana MCP. Your AI agent can now swap, send, and manage SOL.
>
> `uvx sol-agent-wallet` to try.
>
> 🧵👇

*(Attach: demo GIF — 0.1 SOL → USDC end-to-end)*

---

## Post 2 — The demo

> Here's the full loop in Claude Desktop:
>
> 1. *"Swap 0.1 SOL for USDC"*
> 2. MCP server signs + submits via Jupiter
> 3. You get back a Solscan link
>
> Total time: ~6 seconds. No copy-pasting addresses. No leaving the conversation.

*(Attach: 30-second clip or screenshot of completed swap + Solscan)*

---

## Post 3 — Why this matters

> Read-only MCPs are fine for dashboards. They're not enough for actual agents.
>
> The interesting use cases all need writes:
>  – autonomous rebalancing
>  – agent crews with on-chain treasuries
>  – AI coding tools that pay for their own compute
>  – DCA bots that don't need a custom UI
>
> They all need a wallet that an LLM can call.

---

## Post 4 — Safety (this matters; lead with it)

> Putting "AI agent" and "private key" in the same sentence is scary. So the defaults are paranoid:
>
> ✅ Devnet by default — no real funds touched on first run
> ✅ Per-tx SOL cap (1.0 by default, configurable)
> ✅ Write tools only register when SOLANA_PRIVATE_KEY is set
> ✅ Use a burner wallet — never your daily driver
>
> Mainnet is one env var away when you're ready.

---

## Post 5 — Install (frictionless)

> Works with everything that speaks MCP:
>
>  – Claude Desktop
>  – Cursor
>  – Cline
>  – Continue.dev
>  – Zed
>  – Windsurf
>
> Copy-paste configs for each: github.com/yksanjo/sol-agent-wallet/tree/main/install
>
> One line:
> `{"command":"uvx","args":["sol-agent-wallet"]}`

---

## Post 6 — What's next

> v0.1.0 ships: SOL transfers + Jupiter swaps.
>
> Roadmap:
>  – SPL token transfers (any token, not just SOL)
>  – Staking via Marinade/Jito
>  – Lending (MarginFi, Kamino)
>  – NFT buy/sell (Tensor)
>  – DCA orders
>
> What should I build first? Reply with your use case.

---

## Post 7 — Call to action

> Try it: `uvx sol-agent-wallet`
>
> ⭐️ github.com/yksanjo/sol-agent-wallet
> 📦 pypi.org/project/sol-agent-wallet/
>
> PRs welcome. If you ship something interesting on top of it, send it — I'll boost.

---

## Reply strategy

- **First 30 min**: own the thread. Reply to every comment, even one-emoji ones.
- **First 2 hours**: post the demo GIF directly under any "show me" reply.
- **If a high-profile account boosts**: thank by reply, not by retweet — keeps the original thread climbing.
- **If asked about competitors**: don't trash them. Acknowledge Helius/QuickNode read-only servers, position as "the missing write piece."
