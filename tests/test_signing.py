"""Real (non-mocked) signing-path tests.

The rest of the suite mocks the transaction layer, so it cannot catch the
signing no-op bug (AUDIT FIX #2) or the blockhash type bug (AUDIT FIX #1).
These tests construct real solders transactions and prove the signing path
produces a well-formed, signed, submittable transaction.
"""

from __future__ import annotations

import base64

import pytest
from solders.hash import Hash
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction, VersionedTransaction

from sol_agent_wallet.clients.jupiter import JupiterClient


# A valid base58-encoded blockhash (32 bytes), as a node would return.
SAMPLE_BLOCKHASH = "EkSnNWid2cvwEVnVx9aBqaWmkkpqi51qH33gXfKZjBYn"


def _make_unsigned_jupiter_tx(payer: Pubkey) -> str:
    """Build an unsigned VersionedTransaction (base64) like Jupiter returns."""
    ix = transfer(
        TransferParams(from_pubkey=payer, to_pubkey=Keypair().pubkey(), lamports=1000)
    )
    msg = MessageV0.try_compile(payer, [ix], [], Hash.from_string(SAMPLE_BLOCKHASH))
    unsigned = VersionedTransaction.populate(msg, [Signature.default()])
    return base64.b64encode(bytes(unsigned)).decode()


def test_blockhash_string_converts_to_hash():
    """AUDIT FIX #1: a base58 blockhash string must build a Hash usable by Transaction."""
    bh = Hash.from_string(SAMPLE_BLOCKHASH)
    kp = Keypair()
    ix = transfer(
        TransferParams(from_pubkey=kp.pubkey(), to_pubkey=Keypair().pubkey(), lamports=1000)
    )
    from solders.message import Message

    msg = Message([ix], kp.pubkey())
    tx = Transaction([kp], msg, bh)  # would raise if bh were a str
    assert len(bytes(tx)) > 0


def test_execute_swap_actually_signs(monkeypatch):
    """AUDIT FIX #2: execute_swap must produce a tx with a real signature.

    Before the fix, `tx.sign([keypair])` was a no-op on the immutable
    VersionedTransaction, so the submitted tx carried an all-zero signature.
    """
    kp = Keypair()
    unsigned_b64 = _make_unsigned_jupiter_tx(kp.pubkey())

    captured = {}

    # Stub Jupiter's /swap HTTP call to return our locally-built unsigned tx.
    def fake_get_swap_transaction(self, *a, **kw):
        return {"swapTransaction": unsigned_b64}

    monkeypatch.setattr(JupiterClient, "get_swap_transaction", fake_get_swap_transaction)

    # Capture the signed tx instead of broadcasting it.
    class FakeRPC:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def send_and_confirm_transaction(self, tx, *a, **kw):
            captured["tx"] = tx
            return {"success": True, "signature": "FAKE", "slot": 0, "status": "confirmed"}

    monkeypatch.setattr("sol_agent_wallet.clients.solana_rpc.SolanaRPCClient", FakeRPC)

    with JupiterClient() as jup:
        result = jup.execute_swap({"fake": "quote"}, kp)

    assert result["success"] is True
    signed = captured["tx"]
    assert isinstance(signed, VersionedTransaction)

    # The fee-payer's signature slot must be non-zero (i.e. actually signed),
    # and verifying confirms it's a valid signature over the message.
    raw = bytes(signed)
    sig_bytes = raw[1:65]  # 1-byte sig count prefix, then first 64-byte sig
    assert sig_bytes != bytes(64), "transaction was not signed (all-zero signature)"
    assert signed.verify_with_results()[0] is True
