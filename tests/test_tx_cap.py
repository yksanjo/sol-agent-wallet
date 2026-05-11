"""The tx cap is the load-bearing safety control. Test it from every angle."""

from __future__ import annotations

import pytest

from sol_agent_wallet.config import get_config
from sol_agent_wallet.tools.swap import SOL_MINT, handle_swap
from sol_agent_wallet.tools.transfer import handle_transfer
from sol_agent_wallet.wallet.manager import WalletManager


@pytest.fixture
def write_wallet(fresh_keypair) -> WalletManager:
    return WalletManager(fresh_keypair)


@pytest.fixture
def low_cap(monkeypatch):
    monkeypatch.setenv("SOLANA_MAX_TX_SOL", "0.5")
    get_config.cache_clear()


@pytest.mark.asyncio
async def test_transfer_over_cap_is_rejected_without_network(low_cap, write_wallet):
    # 0.6 > cap (0.5) — handler must reject BEFORE building or sending a transaction.
    # We don't mock the RPC; if the cap check is skipped, we'd hit devnet and the
    # test would either pass for the wrong reason or fail with a network error.
    [reply] = await handle_transfer(
        {"to_address": "11111111111111111111111111111111", "amount": 0.6},
        write_wallet,
    )
    assert "⛔" in reply.text
    assert "0.5 SOL" in reply.text
    assert "SOLANA_MAX_TX_SOL" in reply.text


@pytest.mark.asyncio
async def test_swap_over_cap_when_input_is_sol(low_cap, write_wallet):
    [reply] = await handle_swap(
        {
            "input_mint": SOL_MINT,
            "output_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "amount": 2.0,
            "slippage": 0.5,
        },
        write_wallet,
    )
    assert "⛔" in reply.text
    assert "SOLANA_MAX_TX_SOL" in reply.text


@pytest.mark.asyncio
async def test_swap_cap_does_not_apply_when_input_is_non_sol(low_cap, write_wallet, monkeypatch):
    # When you're swapping USDC → SOL, the `amount` is in USDC units. The SOL cap
    # doesn't apply at this stage — Jupiter handles the slippage envelope.
    # We expect the handler to attempt the swap path (which will fail without a real
    # quote), NOT to short-circuit with a cap error.
    quote_calls = []

    class FakeJupiterClient:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get_quote(self, *a, **kw):
            quote_calls.append((a, kw))
            return None  # Force the handler down the "no quote" branch
        def execute_swap(self, *a, **kw): pytest.fail("Should not reach execute")

    monkeypatch.setattr("sol_agent_wallet.tools.swap.JupiterClient", FakeJupiterClient)

    [reply] = await handle_swap(
        {
            "input_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "output_mint": SOL_MINT,
            "amount": 10000,
            "slippage": 0.5,
        },
        write_wallet,
    )
    # The cap check was skipped (input not SOL) → we reached Jupiter's quote call.
    assert len(quote_calls) == 1
    assert "Could not get a quote" in reply.text


@pytest.mark.asyncio
async def test_transfer_under_cap_proceeds_past_cap_check(low_cap, write_wallet, monkeypatch):
    # Under cap → must NOT short-circuit with ⛔. We stub the RPC to confirm
    # the handler tried to talk to the network rather than blocking on the cap.
    transfer_calls = []

    class FakeRPC:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def transfer_sol(self, keypair, to_address, amount):
            transfer_calls.append((to_address, amount))
            return {"success": True, "signature": "FAKE_SIG", "slot": 0, "status": "confirmed"}

    monkeypatch.setattr("sol_agent_wallet.tools.transfer.SolanaRPCClient", FakeRPC)

    [reply] = await handle_transfer(
        {"to_address": "11111111111111111111111111111111", "amount": 0.4},
        write_wallet,
    )
    assert "⛔" not in reply.text
    assert "✅" in reply.text
    assert len(transfer_calls) == 1
    assert transfer_calls[0] == ("11111111111111111111111111111111", 0.4)


@pytest.mark.asyncio
async def test_read_only_wallet_cannot_transfer():
    wallet = WalletManager()  # read-only
    [reply] = await handle_transfer(
        {"to_address": "11111111111111111111111111111111", "amount": 0.001},
        wallet,
    )
    assert "❌" in reply.text
    # Hint should point users at the env var
    assert "SOLANA_PRIVATE_KEY" in reply.text


@pytest.mark.asyncio
async def test_solscan_link_uses_devnet_cluster_on_devnet(write_wallet, monkeypatch):
    class FakeRPC:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def transfer_sol(self, *a, **kw):
            return {"success": True, "signature": "DEVNET_SIG", "slot": 1, "status": "confirmed"}

    monkeypatch.setattr("sol_agent_wallet.tools.transfer.SolanaRPCClient", FakeRPC)

    [reply] = await handle_transfer(
        {"to_address": "11111111111111111111111111111111", "amount": 0.001},
        write_wallet,
    )
    assert "https://solscan.io/tx/DEVNET_SIG?cluster=devnet" in reply.text


@pytest.mark.asyncio
async def test_solscan_link_no_suffix_on_mainnet(write_wallet, monkeypatch):
    monkeypatch.setenv("SOLANA_NETWORK", "mainnet-beta")
    get_config.cache_clear()

    class FakeRPC:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def transfer_sol(self, *a, **kw):
            return {"success": True, "signature": "MAIN_SIG", "slot": 1, "status": "confirmed"}

    monkeypatch.setattr("sol_agent_wallet.tools.transfer.SolanaRPCClient", FakeRPC)

    [reply] = await handle_transfer(
        {"to_address": "11111111111111111111111111111111", "amount": 0.001},
        write_wallet,
    )
    assert "https://solscan.io/tx/MAIN_SIG" in reply.text
    assert "?cluster=" not in reply.text
