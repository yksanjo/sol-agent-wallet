"""Swap tools — execute token swaps via Jupiter."""

from __future__ import annotations

from mcp.types import Tool, TextContent
from ..clients.solana_rpc import SolanaRPCClient
from ..clients.jupiter import JupiterClient
from ..config import get_config, TxCapExceeded
from ..wallet.manager import WalletManager


LAMPORTS_PER_SOL = 1_000_000_000
SOL_MINT = "So11111111111111111111111111111111111111112"


def get_quote_tool() -> Tool:
    return Tool(
        name="sol_quote",
        description="Get a swap quote between two tokens on Solana via Jupiter",
        inputSchema={
            "type": "object",
            "properties": {
                "input_mint": {
                    "type": "string",
                    "description": "Input token mint address (e.g., 'So11111111111111111111111111111111111111112' for SOL)",
                },
                "output_mint": {
                    "type": "string",
                    "description": "Output token mint address",
                },
                "amount": {
                    "type": "number",
                    "description": "Amount of input token to swap (in SOL or token units)",
                },
                "slippage": {
                    "type": "number",
                    "description": "Slippage tolerance in percent (default: 0.5)",
                    "default": 0.5,
                },
            },
            "required": ["input_mint", "output_mint", "amount"],
        },
    )


def get_swap_tool() -> Tool:
    return Tool(
        name="sol_swap",
        description="Execute a token swap on Solana via Jupiter. Requires SOLANA_PRIVATE_KEY to be set.",
        inputSchema={
            "type": "object",
            "properties": {
                "input_mint": {
                    "type": "string",
                    "description": "Input token mint address (e.g., 'So11111111111111111111111111111111111111112' for SOL)",
                },
                "output_mint": {
                    "type": "string",
                    "description": "Output token mint address",
                },
                "amount": {
                    "type": "number",
                    "description": "Amount of input token to swap (in SOL or token units)",
                },
                "slippage": {
                    "type": "number",
                    "description": "Slippage tolerance in percent (default: 0.5)",
                    "default": 0.5,
                },
            },
            "required": ["input_mint", "output_mint", "amount"],
        },
    )


def get_search_tool() -> Tool:
    return Tool(
        name="sol_search",
        description="Search for a Solana token by symbol or name (e.g., 'SOL', 'USDC', 'BONK', 'JUP')",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Token symbol or name to search for",
                }
            },
            "required": ["query"],
        },
    )


async def handle_quote(arguments: dict, wallet: WalletManager | None = None) -> list[TextContent]:
    input_mint = arguments["input_mint"]
    output_mint = arguments["output_mint"]
    amount = arguments["amount"]
    slippage = arguments.get("slippage", 0.5)
    slippage_bps = int(slippage * 100)

    if input_mint == SOL_MINT:
        amount_lamports = int(amount * LAMPORTS_PER_SOL)
    else:
        amount_lamports = int(amount * 1_000_000)

    with JupiterClient() as jup:
        quote = jup.get_quote(input_mint, output_mint, amount_lamports, slippage_bps)

        if not quote:
            return [TextContent(type="text", text="❌ Could not get a quote. Check token addresses and try again.")]

        in_amount = float(quote.get("inAmount", 0)) / LAMPORTS_PER_SOL
        out_amount = float(quote.get("outAmount", 0)) / LAMPORTS_PER_SOL
        price_impact = float(quote.get("priceImpactPct", 0))
        routes = len(quote.get("routePlan", []))

        result = f"🔄 Swap Quote\n\n"
        result += f"  Input:  {amount} → {in_amount:.6f}\n"
        result += f"  Output: {out_amount:.6f}\n"
        result += f"  Price Impact: {price_impact:.2f}%\n"
        result += f"  Routes: {routes}\n"
        result += f"  Slippage: {slippage}%\n\n"
        result += f"To execute this swap, use sol_swap with the same parameters."

        return [TextContent(type="text", text=result)]


async def handle_swap(arguments: dict, wallet: WalletManager) -> list[TextContent]:
    input_mint = arguments["input_mint"]
    output_mint = arguments["output_mint"]
    amount = arguments["amount"]
    slippage = arguments.get("slippage", 0.5)
    slippage_bps = int(slippage * 100)
    cfg = get_config()

    try:
        keypair = wallet.require_write()
    except PermissionError as e:
        return [TextContent(type="text", text=f"❌ {e}")]

    # Tx cap enforced only when input is SOL — the cap is denominated in SOL
    if input_mint == SOL_MINT:
        try:
            cfg.check_tx_cap(amount)
        except TxCapExceeded as e:
            return [TextContent(type="text", text=f"⛔ {e}")]

    if input_mint == SOL_MINT:
        amount_lamports = int(amount * LAMPORTS_PER_SOL)
    else:
        amount_lamports = int(amount * 1_000_000)

    with JupiterClient() as jup:
        quote = jup.get_quote(input_mint, output_mint, amount_lamports, slippage_bps)
        if not quote:
            return [TextContent(type="text", text="❌ Could not get a quote for this swap.")]

        try:
            result = jup.execute_swap(quote, keypair)

            if result.get("success"):
                sig = result.get("signature", "")
                out_amount = float(quote.get("outAmount", 0)) / LAMPORTS_PER_SOL
                network_tag = "" if cfg.is_mainnet else f" [{cfg.network}]"
                return [TextContent(
                    type="text",
                    text=f"✅ Swap Executed!{network_tag}\n"
                         f"   Swapped: {amount} → {out_amount:.6f}\n"
                         f"   Signature: {sig}\n"
                         f"   View: https://solscan.io/tx/{sig}{cfg.solscan_suffix}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Swap failed: {result.get('error', 'Unknown error')}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Swap error: {e}")]


async def handle_search(arguments: dict, wallet: WalletManager | None = None) -> list[TextContent]:
    query = arguments["query"]

    with JupiterClient() as jup:
        results = jup.search_token(query)

        if not results:
            return [TextContent(type="text", text=f"❌ No tokens found matching '{query}'")]

        result = f"🔍 Token Search Results for '{query}'\n\n"
        for r in results[:10]:
            result += f"  • {r['symbol']:8s} | {r['name']:30s} | {r['mint'][:16]}...\n"

        return [TextContent(type="text", text=result)]
