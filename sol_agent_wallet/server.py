"""Sol Agent Wallet — a write-capable Solana MCP server.

Run with:
    uvx sol-agent-wallet
    # or
    python -m sol_agent_wallet.server

By default the server talks to Solana devnet. To enable mainnet write operations:
    export SOLANA_PRIVATE_KEY='your_base58_private_key'
    export SOLANA_NETWORK=mainnet-beta
    uvx sol-agent-wallet

Per-transaction SOL cap defaults to 1.0. Override with SOLANA_MAX_TX_SOL.
"""

from __future__ import annotations

import asyncio
import sys

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import __version__
from .config import get_config
from .tools import balances, transfer, swap
from .wallet.manager import WalletManager


def create_server() -> tuple[Server, WalletManager]:
    """Create the MCP server and initialize wallet."""
    wallet = WalletManager.from_env()
    server = Server("sol-agent-wallet")

    TOOLS: list[Tool] = [
        balances.get_balance_tool(),
        balances.get_portfolio_tool(),
        swap.get_quote_tool(),
        swap.get_search_tool(),
    ]

    if not wallet.is_read_only:
        TOOLS.extend([
            transfer.get_transfer_tool(),
            swap.get_swap_tool(),
        ])

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        wallet_address = wallet.address

        if name == "sol_balance":
            return await balances.handle_balance(arguments, wallet_address)
        elif name == "sol_portfolio":
            return await balances.handle_portfolio(arguments, wallet_address)
        elif name == "sol_quote":
            return await swap.handle_quote(arguments, wallet)
        elif name == "sol_search":
            return await swap.handle_search(arguments, wallet)
        elif name == "sol_transfer":
            return await transfer.handle_transfer(arguments, wallet)
        elif name == "sol_swap":
            return await swap.handle_swap(arguments, wallet)
        else:
            raise ValueError(f"Unknown tool: {name}")

    return server, wallet


def _print_banner(wallet: WalletManager) -> None:
    cfg = get_config()
    mode = "🔓 WRITE CAPABLE" if not wallet.is_read_only else "👁️  READ ONLY"
    network_label = cfg.network.upper()
    if cfg.is_mainnet:
        network_label += "  ⚠️  REAL FUNDS"
    print(f"\n{'='*54}", file=sys.stderr)
    print(f"  ☀️  Sol Agent Wallet v{__version__}", file=sys.stderr)
    print(f"  {'='*52}", file=sys.stderr)
    print(f"  Mode:     {mode}", file=sys.stderr)
    print(f"  Network:  {network_label}", file=sys.stderr)
    print(f"  RPC:      {cfg.rpc_endpoint}", file=sys.stderr)
    print(f"  Max tx:   {cfg.max_tx_sol} SOL  (SOLANA_MAX_TX_SOL)", file=sys.stderr)
    if wallet.address:
        print(f"  Wallet:   {wallet.address}", file=sys.stderr)
    if wallet.is_read_only:
        print(f"\n  💡 To enable transactions:", file=sys.stderr)
        print(f"     export SOLANA_PRIVATE_KEY='your_base58_private_key'", file=sys.stderr)
    if not cfg.is_mainnet and not wallet.is_read_only:
        print(f"\n  💡 Devnet-first default. To trade real SOL:", file=sys.stderr)
        print(f"     export SOLANA_NETWORK=mainnet-beta", file=sys.stderr)
    print(f"{'='*54}\n", file=sys.stderr)


async def main() -> None:
    server, wallet = create_server()
    _print_banner(wallet)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sol-agent-wallet",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def cli() -> None:
    """Entry point used by `uvx sol-agent-wallet`."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
