"""Tests for sol_agent_wallet.config — security defaults are load-bearing."""

from __future__ import annotations

import pytest

from sol_agent_wallet.config import (
    Config,
    ConfigError,
    DEFAULT_MAX_TX_SOL,
    DEFAULT_NETWORK,
    NETWORK_RPC,
    TxCapExceeded,
    get_config,
)


def test_default_is_devnet():
    cfg = get_config()
    assert cfg.network == "devnet"
    assert cfg.rpc_endpoint == NETWORK_RPC["devnet"]
    assert cfg.is_mainnet is False
    assert cfg.max_tx_sol == DEFAULT_MAX_TX_SOL


def test_default_network_constant_is_devnet():
    # Guardrail: nobody flips this to mainnet without thinking.
    assert DEFAULT_NETWORK == "devnet"


def test_mainnet_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("SOLANA_NETWORK", "mainnet-beta")
    get_config.cache_clear()
    cfg = get_config()
    assert cfg.is_mainnet
    assert cfg.rpc_endpoint == NETWORK_RPC["mainnet-beta"]
    assert cfg.solscan_suffix == ""


def test_devnet_solscan_suffix(monkeypatch):
    cfg = get_config()
    assert cfg.solscan_suffix == "?cluster=devnet"


def test_custom_rpc_url(monkeypatch):
    monkeypatch.setenv("SOLANA_NETWORK", "https://my.helius.example/rpc")
    get_config.cache_clear()
    cfg = get_config()
    assert cfg.network == "custom"
    assert cfg.rpc_endpoint == "https://my.helius.example/rpc"


def test_explicit_rpc_url_overrides_network(monkeypatch):
    monkeypatch.setenv("SOLANA_NETWORK", "mainnet-beta")
    monkeypatch.setenv("SOLANA_RPC_URL", "https://my.helius.example/rpc")
    get_config.cache_clear()
    cfg = get_config()
    # SOLANA_RPC_URL wins and re-tags as custom
    assert cfg.rpc_endpoint == "https://my.helius.example/rpc"
    assert cfg.network == "custom"


def test_unknown_network_rejected(monkeypatch):
    monkeypatch.setenv("SOLANA_NETWORK", "not-a-real-network")
    get_config.cache_clear()
    with pytest.raises(ConfigError):
        get_config()


def test_max_tx_sol_override(monkeypatch):
    monkeypatch.setenv("SOLANA_MAX_TX_SOL", "5.5")
    get_config.cache_clear()
    cfg = get_config()
    assert cfg.max_tx_sol == 5.5


def test_max_tx_sol_must_be_positive(monkeypatch):
    monkeypatch.setenv("SOLANA_MAX_TX_SOL", "0")
    get_config.cache_clear()
    with pytest.raises(ConfigError):
        get_config()


def test_max_tx_sol_must_be_numeric(monkeypatch):
    monkeypatch.setenv("SOLANA_MAX_TX_SOL", "not-a-number")
    get_config.cache_clear()
    with pytest.raises(ConfigError):
        get_config()


def test_check_tx_cap_passes_under_limit():
    cfg = Config(network="devnet", rpc_endpoint="x", max_tx_sol=1.0)
    cfg.check_tx_cap(0.99)
    cfg.check_tx_cap(1.0)  # exactly at cap is allowed


def test_check_tx_cap_raises_over_limit():
    cfg = Config(network="devnet", rpc_endpoint="x", max_tx_sol=1.0)
    with pytest.raises(TxCapExceeded) as exc:
        cfg.check_tx_cap(1.01)
    msg = str(exc.value)
    assert "1.01" in msg
    assert "SOLANA_MAX_TX_SOL" in msg


def test_tx_cap_exceeded_is_permission_error():
    # Handlers catch PermissionError to gate write ops — this must stay subclassed.
    assert issubclass(TxCapExceeded, PermissionError)
