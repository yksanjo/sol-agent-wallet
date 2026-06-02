"""Solana RPC client with transaction building support."""

from __future__ import annotations

import json
from typing import Any

import httpx
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import Message
from solders.transaction import Transaction
from solders.keypair import Keypair
from solders.hash import Hash
from solders.system_program import transfer, TransferParams
from solders.commitment_config import CommitmentLevel
import base58


LAMPORTS_PER_SOL = 1_000_000_000


class SolanaRPCClient:
    """Client for interacting with Solana RPC nodes.

    Supports both read and write operations.
    """

    def __init__(
        self,
        rpc_endpoint: str | None = None,
        timeout: float = 30.0,
    ):
        if rpc_endpoint is None:
            from ..config import get_config
            rpc_endpoint = get_config().rpc_endpoint
        self.rpc_endpoint = rpc_endpoint
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _call(self, method: str, params: list[Any] | None = None) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }
        resp = self._client.post(
            self.rpc_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise Exception(f"Solana RPC error: {data['error']}")
        return data["result"]

    # --- Read Methods ---

    def get_balance(self, address: str) -> int:
        return self._call("getBalance", [address])

    def get_balance_sol(self, address: str) -> float:
        result = self.get_balance(address)
        if isinstance(result, dict):
            return result.get("value", 0) / LAMPORTS_PER_SOL
        return result / LAMPORTS_PER_SOL

    def get_token_accounts_by_owner(self, owner: str) -> list[dict[str, Any]]:
        result = self._call(
            "getTokenAccountsByOwner",
            [
                owner,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"},
            ],
        )
        return result.get("value", [])

    def get_token_balances(self, owner: str) -> list[dict[str, Any]]:
        accounts = self.get_token_accounts_by_owner(owner)
        balances = []
        for acc in accounts:
            account_data = acc.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
            token_amount = account_data.get("tokenAmount", {})
            mint = account_data.get("mint", "")
            amount = int(token_amount.get("amount", "0"))
            decimals = token_amount.get("decimals", 0)
            ui_amount = token_amount.get("uiAmount", 0)
            balances.append({
                "mint": mint,
                "amount": amount,
                "decimals": decimals,
                "ui_amount": ui_amount,
                "address": acc.get("pubkey", ""),
            })
        return balances

    def get_signatures_for_address(self, address: str, limit: int = 10) -> list[dict[str, Any]]:
        return self._call("getSignaturesForAddress", [address, {"limit": limit}])

    def get_latest_blockhash(self) -> str:
        result = self._call("getLatestBlockhash")
        return result.get("value", {}).get("blockhash", "")

    def get_token_supply(self, mint: str) -> dict[str, Any]:
        return self._call("getTokenSupply", [mint])

    def get_token_decimals(self, mint: str) -> int:
        """Return the on-chain decimals for a token mint.

        Raises if the mint cannot be resolved — callers must NOT silently
        fall back to a hardcoded decimals value, since that corrupts the
        lamports/UI-amount conversion and can move the wrong amount of funds.
        """
        result = self.get_token_supply(mint)
        value = result.get("value", {}) if isinstance(result, dict) else {}
        decimals = value.get("decimals")
        if decimals is None:
            raise Exception(f"Could not resolve decimals for mint {mint}")
        return int(decimals)

    def get_account_info(self, address: str) -> dict[str, Any] | None:
        try:
            return self._call("getAccountInfo", [address, {"encoding": "jsonParsed"}])
        except Exception:
            return None

    # --- Write Methods ---

    def send_transaction(self, transaction: Transaction) -> str:
        """Send a signed transaction to the network.

        Args:
            transaction: A signed Transaction object

        Returns:
            Transaction signature as a string
        """
        tx_bytes = bytes(transaction)
        tx_b58 = base58.b58encode(tx_bytes).decode()
        result = self._call("sendTransaction", [tx_b58, {"encoding": "base58"}])
        return result

    def send_and_confirm_transaction(
        self, transaction: Transaction, max_retries: int = 3
    ) -> dict[str, Any]:
        """Send and confirm a transaction.

        Args:
            transaction: A signed Transaction object
            max_retries: Maximum confirmation retries

        Returns:
            Dict with signature, slot, and confirmation status
        """
        signature = self.send_transaction(transaction)
        
        # Wait for confirmation
        for _ in range(max_retries):
            import time
            time.sleep(2)
            try:
                status = self._call("getSignatureStatuses", [[signature]])
                statuses = status.get("value", [])
                if statuses and statuses[0]:
                    confirmation = statuses[0].get("confirmationStatus", "")
                    if confirmation in ("confirmed", "finalized"):
                        slot = statuses[0].get("slot", 0)
                        return {
                            "signature": signature,
                            "slot": slot,
                            "status": confirmation,
                            "success": statuses[0].get("err") is None,
                        }
            except Exception:
                continue
        
        return {"signature": signature, "status": "unknown", "success": False}

    def transfer_sol(
        self,
        from_keypair: Keypair,
        to_address: str,
        amount_sol: float,
    ) -> dict[str, Any]:
        """Transfer SOL from one account to another.

        Args:
            from_keypair: The sender's keypair
            to_address: The recipient's Solana address
            amount_sol: Amount of SOL to send

        Returns:
            Transaction result with signature
        """
        from_pubkey = from_keypair.pubkey()
        to_pubkey = Pubkey.from_string(to_address)
        lamports = int(amount_sol * LAMPORTS_PER_SOL)

        # Get recent blockhash. The RPC returns a base58 string, but
        # solders.Transaction needs a Hash — convert it explicitly.
        blockhash = Hash.from_string(self.get_latest_blockhash())

        # Create transfer instruction
        ix = transfer(
            TransferParams(
                from_pubkey=from_pubkey,
                to_pubkey=to_pubkey,
                lamports=lamports,
            )
        )

        # Build and sign transaction
        message = Message([ix], from_pubkey)
        tx = Transaction([from_keypair], message, blockhash)

        return self.send_and_confirm_transaction(tx)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
