"""Sol Agent Wallet — The first write-capable Solana AI agent.

Run with:
    uvx sol-agent-wallet
    # or
    python -m sol_agent_wallet.server

To enable write operations, set SOLANA_PRIVATE_KEY environment variable:
    export SOLANA_PRIVATE_KEY='your_base58_private_key'
    python -m sol_agent_wallet.server
"""

from __future__ import annotations

import asyncio
import os
import sys

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from .tools import balances, transfer, swap
from .wallet.manager import WalletManager


def create_server() -> tuple[Server, WalletManager]:
    """Create the MCP server and initialize wallet."""
    # Initialize wallet
    wallet = WalletManager.from_env()

    server = Server("sol-agent-wallet")

    # Define tools
    TOOLS: list[Tool] = [
        # Read tools (always available)
        balances.get_balance_tool(),
        balances.get_portfolio_tool(),
        swap.get_quote_tool(),
        swap.get_search_tool(),
    ]

    # Write tools (only if wallet has private key)
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


async def main():
    server, wallet = create_server()

    # Print startup info
    mode = "🔓 WRITE CAPABLE" if not wallet.is_read_only else "👁️ READ ONLY"
    print(f"\n{'='*50}")
    print(f"  ☀️ Sol Agent Wallet")
    print(f"  {'='*50}")
    print(f"  Mode: {mode}")
    if wallet.address:
        print(f"  Wallet: {wallet.address}")
    if wallet.is_read_only:
        print(f"\n  💡 To enable transactions, set:")
        print(f"     export SOLANA_PRIVATE_KEY='your_base58_private_key'")
    print(f"{'='*50}\n")

    async with server.run() as running:
        await running.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
