# ☀️ Sol Agent Wallet

[![PyPI version](https://img.shields.io/pypi/v/sol-agent-wallet.svg)](https://pypi.org/project/sol-agent-wallet/)
[![PyPI downloads](https://img.shields.io/pypi/dm/sol-agent-wallet.svg)](https://pypi.org/project/sol-agent-wallet/)
[![Python](https://img.shields.io/pypi/pyversions/sol-agent-wallet.svg)](https://pypi.org/project/sol-agent-wallet/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-00D4AA)](https://modelcontextprotocol.io)

> **Write-capable Solana MCP server.** Swap, send, and manage SOL through Claude, Cursor, or any MCP-compatible agent — using natural language.

```
You: swap 0.1 SOL for USDC

Agent: ✅ Swap Executed!
   Swapped: 0.1 → 14.823 USDC
   Signature: 5x7K…aF2
   View: https://solscan.io/tx/5x7K…aF2
```

---

## ⚡ Quick Install

| Client | One-line config | Path |
|---|---|---|
| **Claude Desktop** | `{"command":"uvx","args":["sol-agent-wallet"]}` | [`install/claude-desktop.json`](./install/claude-desktop.json) |
| **Cursor** | `{"command":"uvx","args":["sol-agent-wallet"]}` | [`install/cursor.json`](./install/cursor.json) |
| **Cline** | `{"command":"uvx","args":["sol-agent-wallet"]}` | [`install/cline.json`](./install/cline.json) |
| **Continue.dev** | stdio → `uvx sol-agent-wallet` | [`install/continue.json`](./install/continue.json) |
| **Zed** | `context_servers.sol-agent-wallet.command` → `uvx` | [`install/zed.json`](./install/zed.json) |
| **Windsurf** | `{"command":"uvx","args":["sol-agent-wallet"]}` | [`install/windsurf.json`](./install/windsurf.json) |

Anything that speaks [MCP](https://modelcontextprotocol.io) over stdio works. See the [install README](./install/README.md) for read-only vs write-mode variants.

---

## 🎬 Demo

![Demo: swap 0.1 SOL → USDC end-to-end](./demo/demo.gif)

*60-second cast: Claude Desktop → `swap 0.1 SOL for USDC` → tx lands → Solscan link opens. Recording recipe in [`demo/script.md`](./demo/script.md).*

---

## 🤔 Why this exists

Every other Solana MCP server is **read-only**. You can ask "what's my balance?" but you can't do anything.

| Server | Reads | Writes (swap / send) |
|---|---|---|
| [Solana MCP](https://github.com/modelcontextprotocol/servers) | ✅ | ❌ |
| Helius MCP | ✅ | ❌ |
| QuickNode MCP | ✅ | ❌ |
| **sol-agent-wallet** | ✅ | **✅** |

Write-capable matters because the interesting agent use cases — autonomous rebalancing, paying for compute in SOL, on-chain crew treasuries — all require signing transactions, not just inspecting them.

---

## 🚀 Quick Start

### Read-only (no key needed)

Paste into your MCP client config:

```json
{
  "mcpServers": {
    "sol-agent-wallet": {
      "command": "uvx",
      "args": ["sol-agent-wallet"]
    }
  }
}
```

### Write mode (devnet by default — safe to test)

```bash
export SOLANA_PRIVATE_KEY='your_base58_private_key'
uvx sol-agent-wallet
```

That's it. By default this runs on **Solana devnet** — no real funds at risk. Ask your agent to airdrop some SOL (`"airdrop 1 SOL to my wallet"` via Phantom or `solana airdrop`) and try a swap.

### Write mode on mainnet (real money)

```bash
export SOLANA_PRIVATE_KEY='your_burner_wallet_base58_key'
export SOLANA_NETWORK=mainnet-beta
export SOLANA_MAX_TX_SOL=1.0    # default; raise as needed
uvx sol-agent-wallet
```

---

## 💡 Example Prompts

**Read-only (always available):**
- *"What's my SOL balance?"*
- *"Show me my full portfolio with USD value"*
- *"Get a quote for swapping 0.5 SOL to USDC"*
- *"Search for the BONK token"*

**Write operations (require `SOLANA_PRIVATE_KEY`):**
- *"Send 0.1 SOL to 7EcDhSYG…CFLtVf"*
- *"Swap 0.5 SOL for USDC on Jupiter"*
- *"Swap 10 USDC for BONK with 1% slippage"*

---

## ⚠️ Security

**This is beta software that can sign transactions on mainnet. Read this section before pasting a real private key.**

### Defaults that protect you

| Default | Why |
|---|---|
| **Network = devnet** | First run never touches real funds. Set `SOLANA_NETWORK=mainnet-beta` to opt in. |
| **Max tx = 1.0 SOL** | A malformed LLM call can't drain your wallet in one transaction. Raise with `SOLANA_MAX_TX_SOL`. |
| **Read-only without `SOLANA_PRIVATE_KEY`** | No key, no write tools registered. The agent literally cannot call `sol_swap` or `sol_transfer`. |

### Use a burner wallet

**Do not paste your daily-driver wallet's private key.** Create a new wallet in Phantom (Settings → Add / Connect Wallet → Create New Wallet), fund it with the minimum you need, and export *that* key. If something goes wrong — bad prompt, leaked env, library bug — the blast radius is limited to that burner.

### What the server has access to

- ✅ Signs and submits transactions you (or your agent) explicitly request via tool calls
- ❌ Never sends your private key over the network. It stays in the process memory of `uvx sol-agent-wallet` on your machine
- ❌ No telemetry, no analytics, no remote logging

### Reporting issues

Vulnerabilities → see [SECURITY.md](./SECURITY.md). Please don't open public issues for security bugs.

---

## ⚙️ Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `SOLANA_PRIVATE_KEY` | *(unset → read-only)* | Base58-encoded private key. Enables write tools. |
| `SOLANA_NETWORK` | `devnet` | One of `devnet`, `mainnet-beta`, `testnet`, or a full RPC URL. |
| `SOLANA_RPC_URL` | *(derived from network)* | Override the RPC endpoint without changing `SOLANA_NETWORK`. |
| `SOLANA_MAX_TX_SOL` | `1.0` | Per-transaction SOL cap. Applies to transfers and SOL→token swaps. |

---

## 🛠️ Tools exposed via MCP

| Tool | Mode | What it does |
|---|---|---|
| `sol_balance` | read | SOL + SPL token balances for any address |
| `sol_portfolio` | read | Full portfolio with USD estimate |
| `sol_quote` | read | Jupiter swap quote (no execution) |
| `sol_search` | read | Find a token by symbol or name |
| `sol_transfer` | write | Send SOL to an address |
| `sol_swap` | write | Execute a swap via Jupiter |

Write tools are only registered when `SOLANA_PRIVATE_KEY` is set — your agent literally can't see them in read-only mode.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  AI Agent   │────▶│ Sol Agent Wallet │────▶│  Solana Network  │
│  (Claude,   │ MCP │  (Python stdio)  │ RPC │  + Jupiter v6    │
│  Cursor…)   │     │                  │     │                  │
└─────────────┘     └────────┬─────────┘     └──────────────────┘
                             │
                    ┌────────┴────────┐
                    │  WalletManager  │  ← env / file / keypair
                    │  Config         │  ← network + tx cap
                    └─────────────────┘
```

---

## 📦 Install from source

```bash
git clone https://github.com/yksanjo/sol-agent-wallet.git
cd sol-agent-wallet
pip install -e '.[dev]'
sol-agent-wallet            # or: python -m sol_agent_wallet
pytest                      # run the test suite
```

---

## 🗺️ Roadmap

- [ ] Send any SPL token (not just SOL)
- [ ] Staking (Marinade / Jito)
- [ ] Lending (MarginFi / Kamino)
- [ ] NFT buy/sell (Tensor / Magic Eden)
- [ ] DCA orders
- [ ] Portfolio rebalancing

---

## 📜 License

MIT — see [LICENSE](./LICENSE).

## 🙏 Contributing

PRs welcome. Run `pytest` before opening. Security issues → [SECURITY.md](./SECURITY.md).

---

<div align="center">
  <em>Built by <a href="https://github.com/yksanjo">Yoshi Kondo</a> · Music Ai Lab</em>
</div>
