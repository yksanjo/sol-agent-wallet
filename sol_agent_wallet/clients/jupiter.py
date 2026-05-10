"""Jupiter API client — token swaps and prices on Solana."""

from __future__ import annotations

import json
from typing import Any

import httpx
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import Message
from solders.transaction import Transaction


class JupiterClient:
    """Client for Jupiter Aggregator API — token swaps and prices."""

    def __init__(
        self,
        quote_endpoint: str = "https://quote-api.jup.ag/v6",
        price_endpoint: str = "https://price.jup.ag/v6",
        timeout: float = 30.0,
    ):
        self.quote_endpoint = quote_endpoint
        self.price_endpoint = price_endpoint
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def get_token_price(self, token_mint: str) -> float | None:
        try:
            resp = self._client.get(
                f"{self.price_endpoint}/price",
                params={"ids": token_mint},
            )
            resp.raise_for_status()
            data = resp.json()
            token_data = data.get("data", {}).get(token_mint, {})
            price = token_data.get("price")
            return float(price) if price else None
        except Exception:
            return None

    def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
    ) -> dict[str, Any] | None:
        """Get a swap quote between two tokens."""
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": slippage_bps,
        }
        try:
            resp = self._client.get(
                f"{self.quote_endpoint}/quote",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def get_swap_transaction(
        self,
        quote_response: dict[str, Any],
        wallet_address: str,
        wrap_and_unwrap_sol: bool = True,
        dynamic_compute_unit_limit: bool = True,
        prioritization_fee_lamports: int = 100_000,
    ) -> dict[str, Any] | None:
        """Get a serialized swap transaction from Jupiter.

        Args:
            quote_response: The quote from get_quote()
            wallet_address: The user's wallet address
            wrap_and_unwrap_sol: Auto-wrap/unwrap SOL
            dynamic_compute_unit_limit: Auto-estimate CU
            prioritization_fee_lamports: Priority fee in lamports

        Returns:
            Dict with swap transaction data
        """
        payload = {
            "quoteResponse": quote_response,
            "userPublicKey": wallet_address,
            "wrapAndUnwrapSol": wrap_and_unwrap_sol,
            "dynamicComputeUnitLimit": dynamic_compute_unit_limit,
            "prioritizationFeeLamports": prioritization_fee_lamports,
        }
        try:
            resp = self._client.post(
                f"{self.quote_endpoint}/swap",
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return None

    def execute_swap(
        self,
        quote_response: dict[str, Any],
        keypair: Keypair,
        prioritization_fee_lamports: int = 100_000,
    ) -> dict[str, Any]:
        """Execute a token swap via Jupiter.

        This is the full flow: get swap instructions, build transaction,
        sign, and submit.

        Args:
            quote_response: The quote from get_quote()
            keypair: The user's keypair for signing
            prioritization_fee_lamports: Priority fee

        Returns:
            Transaction result with signature
        """
        from .solana_rpc import SolanaRPCClient

        wallet_address = str(keypair.pubkey())

        # Get swap transaction data from Jupiter
        swap_data = self.get_swap_transaction(
            quote_response=quote_response,
            wallet_address=wallet_address,
            prioritization_fee_lamports=prioritization_fee_lamports,
        )

        if not swap_data:
            return {"success": False, "error": "Failed to get swap transaction from Jupiter"}

        # Deserialize the transaction
        from solders.transaction import VersionedTransaction
        import base64

        tx_bytes = base64.b64decode(swap_data["swapTransaction"])
        tx = VersionedTransaction.from_bytes(tx_bytes)

        # Sign the transaction
        tx.sign([keypair])

        # Send via RPC
        with SolanaRPCClient() as rpc:
            result = rpc.send_and_confirm_transaction(tx)

        return result

    def search_token(self, query: str) -> list[dict[str, Any]]:
        """Search for a token by symbol or name."""
        try:
            resp = self._client.get("https://token.jup.ag/strict")
            resp.raise_for_status()
            tokens = resp.json()
        except Exception:
            return []

        query = query.lower()
        results = []
        for token in tokens:
            symbol = token.get("symbol", "").lower()
            name = token.get("name", "").lower()
            if query in symbol or query in name:
                results.append({
                    "mint": token.get("address", ""),
                    "symbol": token.get("symbol", ""),
                    "name": token.get("name", ""),
                    "decimals": token.get("decimals", 0),
                })
        return results[:10]

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
