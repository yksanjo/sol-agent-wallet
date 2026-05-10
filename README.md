# ☀️ Sol Agent Wallet

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-00D4AA)](https://modelcontextprotocol.io)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/yksanjo/sol-agent-wallet/pulls)

**The first write-capable Solana AI agent.** Not just read-only queries — actually execute transactions through natural language.

> Swap tokens, send SOL, manage your portfolio — all through Claude, Cursor, or any MCP-compatible AI agent.

---

## ✨ What Makes This Different

Every other Solana MCP server is **read-only**. You can ask "what's my balance?" but you can't do anything.

**Sol Agent Wallet lets you actually DO things:**

| Tool | Read-Only MCPs | Sol Agent Wallet |
|------|---------------|-----------------|
| Check balance | ✅ Yes | ✅ Yes |
| View portfolio | ✅ Yes | ✅ Yes |
| Get swap quote | ✅ Yes | ✅ Yes |
| **Execute swap** | ❌ No | **✅ Yes** |
| **Send SOL** | ❌ No | **✅ Yes** |
| **Manage wallet** | ❌ No | **✅ Yes** |

---

## 🚀 Quick Start

### Read-Only Mode (No Key Needed)

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

### Write Mode (Enable Transactions)

```bash
# Set your private key (base58 format)
export SOLANA_PRIVATE_KEY='your_base58_private_key_here'

# Run the server
uvx sol-agent-wallet
```

> **Security Note:** Your private key stays local. It's only used to sign transactions on your machine.

---

## 💡 Example Prompts

### Read-Only (Always Available)

> *"What's my SOL balance?"*
>
> *"Show me my full portfolio with estimated USD value"*
>
> *"Get a quote for swapping 0.5 SOL to USDC"*
>
> *"Search for the BONK token"*

### Write Operations (Requires Private Key)

> *"Send 0.1 SOL to wallet 7EcDhSYGxXyscszYEp35KHN8vvw3svAuLKTzXwCFLtVf"*
>
> *"Swap 0.5 SOL for USDC on Jupiter"*
>
> *"Swap 10 USDC for BONK with 1% slippage"*

---

## 🔒 Security

- **Private key never leaves your machine** — it's only used for local transaction signing
- **Read-only by default** — no key needed for queries
- **Opt-in for writes** — you explicitly enable transaction execution
- **All transactions are confirmed** — you get a Solscan link for every transaction

### Getting Your Private Key

**From Phantom:**
1. Open Phantom → Settings → Security & Privacy → Export Private Key
2. Copy the base58 string
3. `export SOLANA_PRIVATE_KEY='your_key_here'`

**From Solana CLI:**
```bash
solana config get keypair
cat ~/.config/solana/id.json  # JSON array format
export SOLANA_PRIVATE_KEY=$(solana keygen pubkey  # or use the file directly)
```

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  AI Agent   │────▶│ Sol Agent Wallet │────▶│  Solana Network  │
│  (Claude,   │     │  (MCP Server)    │     │  (RPC + Jupiter) │
│  Cursor...) │     │                  │     │                  │
└─────────────┘     └──────────────────┘     └──────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Wallet      │
                    │  Manager     │
                    │              │
                    │ • Read-only  │
                    │ • Write mode │
                    │ • Key mgmt  │
                    └─────────────┘
```

---

## 🗺️ Roadmap

- [ ] **Token Transfers** — Send any SPL token, not just SOL
- [ ] **Staking** — Stake SOL on Marinade/Jito
- [ ] **Lending** — Supply/borrow on Marginfi
- [ ] **NFT Buying** — Buy NFTs on Tensor
- [ ] **DCA Orders** — Automated dollar-cost averaging
- [ ] **Portfolio Rebalancing** — One-click rebalance
- [ ] **Web Dashboard** — Visual interface

---

## 🤝 Contributing

PRs welcome! This is the first write-capable Solana AI agent — let's make it the standard.

- [Open an Issue](https://github.com/yksanjo/sol-agent-wallet/issues)
- [Submit a PR](https://github.com/yksanjo/sol-agent-wallet/pulls)

---

## 📄 License

MIT

---

<div align="center">
  <strong>⭐ Star if you want AI agents that can actually DO things on Solana</strong>
  <br>
  <em>Built by <a href="https://github.com/yksanjo">Yoshi Kondo</a> · Music Ai Lab</em>
</div>
