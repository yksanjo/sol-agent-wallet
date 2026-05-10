"""Balance tools — read-only queries for SOL and tokens."""

from __future__ import annotations

from mcp.types import Tool, TextContent
from ..clients.solana_rpc import SolanaRPCClient
from ..clients.jupiter import JupiterClient


def get_balance_tool() -> Tool:
    return Tool(
        name="sol_balance",
        description="Get SOL and token balances for any Solana wallet address",
        inputSchema={
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Solana wallet address (base58). If not provided, uses the connected wallet.",
                }
            },
        },
    )


def get_portfolio_tool() -> Tool:
    return Tool(
        name="sol_portfolio",
        description="Get a complete portfolio overview with estimated USD value for any wallet",
        inputSchema={
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Solana wallet address (base58). If not provided, uses the connected wallet.",
                }
            },
        },
    )


async def handle_balance(arguments: dict, wallet_address: str | None = None) -> list[TextContent]:
    address = arguments.get("address", wallet_address)
    if not address:
        return [TextContent(type="text", text="❌ No address provided and no wallet connected.")]

    with SolanaRPCClient() as client:
        sol_balance = client.get_balance_sol(address)
        tokens = client.get_token_balances(address)

        result = f"💰 Wallet: {address}\n"
        result += f"   SOL Balance: {sol_balance:.6f} SOL\n"
        if tokens:
            result += f"\n🪙 Token Holdings ({len(tokens)} tokens):\n"
            for t in tokens[:10]:
                ui_amount = t.get("ui_amount", 0)
                mint = t.get("mint", "")[:12]
                if ui_amount and ui_amount > 0:
                    result += f"  • {ui_amount:>12.6f} (mint: {mint}...)\n"
            if len(tokens) > 10:
                result += f"  ... and {len(tokens) - 10} more tokens\n"

        return [TextContent(type="text", text=result)]


async def handle_portfolio(arguments: dict, wallet_address: str | None = None) -> list[TextContent]:
    address = arguments.get("address", wallet_address)
    if not address:
        return [TextContent(type="text", text="❌ No address provided and no wallet connected.")]

    with SolanaRPCClient() as client:
        sol_balance = client.get_balance_sol(address)
        tokens = client.get_token_balances(address)

        # Try to get SOL price
        sol_price = None
        try:
            with JupiterClient() as jup:
                sol_price = jup.get_token_price("So11111111111111111111111111111111111111112")
        except Exception:
            pass

        sol_usd = sol_balance * sol_price if sol_price else 0

        result = f"📊 Portfolio: {address}\n"
        result += "━" * 40 + "\n\n"
        result += f"💰 SOL: {sol_balance:.4f} SOL"
        if sol_price:
            result += f" (${sol_usd:,.2f} USD)"
        result += "\n"

        if tokens:
            result += f"\n🪙 Tokens:\n"
            for t in sorted(tokens, key=lambda x: x.get("ui_amount", 0), reverse=True)[:15]:
                ui = t.get("ui_amount", 0)
                mint = t.get("mint", "")[:12]
                if ui and ui > 0:
                    result += f"  • {ui:>12.6f} (mint: {mint}...)\n"

        result += f"\n📈 Estimated Value: ${sol_usd:,.2f}+ (tokens not priced)\n"

        return [TextContent(type="text", text=result)]
