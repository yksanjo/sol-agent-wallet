"""Transfer tools — execute SOL and token transfers."""

from __future__ import annotations

from mcp.types import Tool, TextContent
from ..clients.solana_rpc import SolanaRPCClient
from ..wallet.manager import WalletManager


def get_transfer_tool() -> Tool:
    return Tool(
        name="sol_transfer",
        description="Send SOL from your wallet to another address. Requires SOLANA_PRIVATE_KEY to be set.",
        inputSchema={
            "type": "object",
            "properties": {
                "to_address": {
                    "type": "string",
                    "description": "Recipient's Solana wallet address (base58)",
                },
                "amount": {
                    "type": "number",
                    "description": "Amount of SOL to send",
                },
                "memo": {
                    "type": "string",
                    "description": "Optional memo for the transaction",
                },
            },
            "required": ["to_address", "amount"],
        },
    )


async def handle_transfer(arguments: dict, wallet: WalletManager) -> list[TextContent]:
    to_address = arguments["to_address"]
    amount = arguments["amount"]
    memo = arguments.get("memo", "")

    # Require write access
    try:
        keypair = wallet.require_write()
    except PermissionError as e:
        return [TextContent(type="text", text=f"❌ {e}")]

    with SolanaRPCClient() as client:
        try:
            result = client.transfer_sol(keypair, to_address, amount)

            if result.get("success"):
                sig = result.get("signature", "")
                slot = result.get("slot", 0)
                return [TextContent(
                    type="text",
                    text=f"✅ Transfer Successful!\n"
                         f"   Sent: {amount} SOL\n"
                         f"   To: {to_address}\n"
                         f"   Signature: {sig}\n"
                         f"   Slot: {slot}\n"
                         f"   View: https://solscan.io/tx/{sig}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Transfer failed.\n"
                         f"   Signature: {result.get('signature', 'N/A')}\n"
                         f"   Status: {result.get('status', 'unknown')}"
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Transfer error: {e}")]
