# LinkedIn — builder/founder post

**Tone:** technical but accessible to non-engineering founders. No jargon dumps. Specific numbers. End with a question to prompt comments (LinkedIn's algorithm loves comments).

**Length:** ~1500 chars. LinkedIn truncates at ~200 chars on the feed — make the first two sentences carry the hook.

---

## Post

```
Read-only AI agents are a demo. Write-capable agents are a product.

I just shipped sol-agent-wallet — a Solana MCP server that gives Claude, Cursor, and any MCP-compatible AI agent the ability to actually execute transactions: swap tokens via Jupiter, send SOL, manage a wallet. Not "look at" — execute.

Every existing Solana MCP server was read-only. That's fine for dashboards. It's not enough for the use cases founders are actually trying to ship right now:

→ Autonomous rebalancing bots
→ Agent crews with shared on-chain treasuries
→ AI coding tools that pay for their own compute in SOL
→ DCA strategies that don't need a custom UI

All of those need a wallet that an LLM can call. So I built one.

The interesting design problem wasn't the swap logic (Jupiter v6 handles routing). It was the safety defaults. Putting "AI agent" and "private key" in the same sentence is how people lose money. So the defaults are deliberately conservative:

• Devnet by default — first run never touches real funds
• Per-transaction SOL cap (1.0 default, configurable)
• Read-only unless you explicitly set SOLANA_PRIVATE_KEY
• Use a burner wallet, always

Install with one line: `uvx sol-agent-wallet`. Copy-paste configs for Claude Desktop, Cursor, Cline, Continue.dev, Zed, and Windsurf are all in the repo.

v0.1.0 today. Roadmap includes staking (Marinade), lending (MarginFi), NFT buys, DCA.

Open source, MIT licensed.

Repo: https://github.com/yksanjo/sol-agent-wallet

Question for builders: what's the first agent-driven on-chain workflow you'd ship if your wallet "just worked" inside Claude or Cursor? Reply below — I'm collecting use cases for v0.2.

#solana #ai #mcp #web3 #buildinpublic
```

---

## Engagement plan

- Pin to top of profile for 7 days.
- Reply to every comment within 4 hours. LinkedIn rewards rapid author engagement disproportionately.
- Don't tag big accounts unless they've already interacted with you — flag for spam filters.
- 24 hours later, post a follow-up in the comments: "Here's what people are building so far — [3-bullet summary]." This re-surfaces the post.

## Variations to test

- A version that opens with the demo GIF — LinkedIn favors video/GIF for reach but kills click-through to GitHub.
- A version that opens with the specific cost saved ("Stopped writing yet another agent-CLI wrapper. Wrote this instead."). Test against a different audience segment if first version underperforms in 48h.
