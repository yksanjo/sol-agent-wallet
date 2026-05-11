# One-Click MCP Client Configs

Copy-paste configurations for every major MCP client. **All configs default to devnet** for safety — set `SOLANA_NETWORK=mainnet-beta` once you've tested with a burner wallet.

| Client | Config file path | Link |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) | [claude-desktop.json](./claude-desktop.json) |
| Cursor | `~/.cursor/mcp.json` or project `.cursor/mcp.json` | [cursor.json](./cursor.json) |
| Cline (VS Code) | Settings → MCP Servers | [cline.json](./cline.json) |
| Continue.dev | `~/.continue/config.json` | [continue.json](./continue.json) |
| Zed | `~/.config/zed/settings.json` → `context_servers` | [zed.json](./zed.json) |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | [windsurf.json](./windsurf.json) |

## Read-only vs write mode

Every config in this folder ships in **two variants** in a single file:

- The default block uses **read-only mode** — no key required, queries only.
- The commented `_write_mode_template` block shows how to add `SOLANA_PRIVATE_KEY` and switch network. Move the keys you want into the live block.

> **Burner wallet recommendation:** create a new wallet with no significant funds. Export its base58 private key from Phantom (Settings → Security & Privacy → Export Private Key) and use that. Never paste your daily-driver wallet's key into an agent config.

## Verifying the install

After editing the config, restart the client and ask:

> *"What MCP tools do you have for Solana?"*

You should see `sol_balance`, `sol_portfolio`, `sol_quote`, `sol_search` (read-only) plus `sol_transfer` and `sol_swap` (write mode).
