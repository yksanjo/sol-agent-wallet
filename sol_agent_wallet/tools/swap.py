"""Swap tools — execute token swaps via Jupiter."""

from __future__ import annotations

import math

from mcp.types import Tool, TextContent
from ..clients.solana_rpc import SolanaRPCClient
from ..clients.jupiter import JupiterClient
from ..config import get_config, TxCapExceeded
from ..wallet.manager import WalletManager


LAMPORTS_PER_SOL = 1_000_000_000
SOL_MINT = "So11111111111111111111111111111111111111112"

# Safety guards for LLM-supplied parameters.
MAX_SLIPPAGE_BPS = 500  # 5% — refuse anything looser
MAX_PRICE_IMPACT_PCT = 5.0  # refuse swaps with >5% price impact


class AmountError(ValueError):
    """Raised when a user-supplied amount is invalid."""


def _validate_amount(amount) -> float:
    """Reject non-positive / non-finite amounts before lamport conversion."""
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise AmountError("Amount must be a number.")
    if not math.isfinite(amount):
        raise AmountError("Amount must be a finite number.")
    if amount <= 0:
        raise AmountError("Amount must be greater than zero.")
    return amount


def _clamp_slippage_bps(slippage_pct: float) -> int:
    """Convert a percent slippage to bps, clamped to a sane maximum."""
    bps = int(slippage_pct * 100)
    if bps < 0:
        bps = 0
    if bps > MAX_SLIPPAGE_BPS:
        bps = MAX_SLIPPAGE_BPS
    return bps


def _decimals_for_mint(mint: str, rpc: SolanaRPCClient) -> int:
    """Decimals for a mint. SOL is known; everything else is looked up."""
    if mint == SOL_MINT:
        return 9
    return rpc.get_token_decimals(mint)


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
    slippage = arguments.get("slippage", 0.5)
    slippage_bps = _clamp_slippage_bps(slippage)

    try:
        amount = _validate_amount(arguments["amount"])
    except AmountError as e:
        return [TextContent(type="text", text=f"❌ {e}")]

    with SolanaRPCClient() as rpc:
        try:
            input_decimals = _decimals_for_mint(input_mint, rpc)
            output_decimals = _decimals_for_mint(output_mint, rpc)
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Could not resolve token decimals: {e}")]

    amount_base_units = int(amount * (10 ** input_decimals))

    with JupiterClient() as jup:
        quote = jup.get_quote(input_mint, output_mint, amount_base_units, slippage_bps)

        if not quote:
            return [TextContent(type="text", text="❌ Could not get a quote. Check token addresses and try again.")]

        in_amount = float(quote.get("inAmount", 0)) / (10 ** input_decimals)
        out_amount = float(quote.get("outAmount", 0)) / (10 ** output_decimals)
        # Jupiter returns priceImpactPct as a decimal fraction ("0.01" == 1%).
        price_impact = float(quote.get("priceImpactPct", 0) or 0) * 100
        routes = len(quote.get("routePlan", []))

        result = f"🔄 Swap Quote\n\n"
        result += f"  Input:  {amount} → {in_amount:.6f}\n"
        result += f"  Output: {out_amount:.6f}\n"
        result += f"  Price Impact: {price_impact:.2f}%\n"
        result += f"  Routes: {routes}\n"
        result += f"  Slippage: {slippage}%\n\n"
        result += f"To execute this swap, use sol_swap with the same parameters."

        return [TextContent(type="text", text=result)]


def _quoted_sol_value(
    input_mint: str,
    output_mint: str,
    amount: float,
    amount_base_units: int,
    quote: dict,
    output_decimals: int,
    jup: JupiterClient,
) -> float | None:
    """Best-effort SOL value of a swap, used to enforce the spend cap on
    SPL-input swaps. Returns None if it cannot be determined."""
    # SOL on either leg gives the value directly.
    if input_mint == SOL_MINT:
        return amount
    if output_mint == SOL_MINT:
        return float(quote.get("outAmount", 0)) / LAMPORTS_PER_SOL
    # Neither leg is SOL: quote the input -> SOL to price the spend in SOL.
    sol_quote = jup.get_quote(input_mint, SOL_MINT, amount_base_units, 50)
    if sol_quote:
        return float(sol_quote.get("outAmount", 0)) / LAMPORTS_PER_SOL
    return None


async def handle_swap(arguments: dict, wallet: WalletManager) -> list[TextContent]:
    input_mint = arguments["input_mint"]
    output_mint = arguments["output_mint"]
    slippage = arguments.get("slippage", 0.5)
    slippage_bps = _clamp_slippage_bps(slippage)
    cfg = get_config()

    try:
        keypair = wallet.require_write()
    except PermissionError as e:
        return [TextContent(type="text", text=f"❌ {e}")]

    try:
        amount = _validate_amount(arguments["amount"])
    except AmountError as e:
        return [TextContent(type="text", text=f"❌ {e}")]

    # Fast path: SOL input is already denominated in SOL, so enforce the cap
    # immediately — before any network call.
    if input_mint == SOL_MINT:
        try:
            cfg.check_tx_cap(amount)
        except TxCapExceeded as e:
            return [TextContent(type="text", text=f"⛔ {e}")]

    with SolanaRPCClient() as rpc:
        try:
            input_decimals = _decimals_for_mint(input_mint, rpc)
            output_decimals = _decimals_for_mint(output_mint, rpc)
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Could not resolve token decimals: {e}")]

    amount_base_units = int(amount * (10 ** input_decimals))

    with JupiterClient() as jup:
        quote = jup.get_quote(input_mint, output_mint, amount_base_units, slippage_bps)
        if not quote:
            return [TextContent(type="text", text="❌ Could not get a quote for this swap.")]

        # Spend cap — enforced for ALL swaps, denominated in SOL. For SPL
        # inputs we price the spend in SOL via the quote so "swap all my USDC"
        # cannot bypass the cap.
        sol_value = _quoted_sol_value(
            input_mint, output_mint, amount, amount_base_units, quote, output_decimals, jup
        )
        if sol_value is None:
            return [TextContent(
                type="text",
                text="❌ Could not price this swap in SOL to enforce the spend cap. Aborting.",
            )]
        try:
            cfg.check_tx_cap(sol_value)
        except TxCapExceeded as e:
            return [TextContent(type="text", text=f"⛔ {e}")]

        # Price-impact guard — refuse swaps that move the price too much.
        # Jupiter returns priceImpactPct as a decimal FRACTION string
        # (e.g. "0.01" == 1%), so multiply by 100 to get a percentage.
        price_impact_pct = abs(float(quote.get("priceImpactPct", 0) or 0)) * 100
        if price_impact_pct > MAX_PRICE_IMPACT_PCT:
            return [TextContent(
                type="text",
                text=(
                    f"⛔ Price impact {price_impact_pct:.2f}% exceeds the "
                    f"{MAX_PRICE_IMPACT_PCT:.0f}% limit. Swap refused."
                ),
            )]

        try:
            result = jup.execute_swap(quote, keypair)

            if result.get("success"):
                sig = result.get("signature", "")
                out_amount = float(quote.get("outAmount", 0)) / (10 ** output_decimals)
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
