"""Shared pytest fixtures and env-var hygiene."""

from __future__ import annotations

import os

import base58
import pytest
from solders.keypair import Keypair

from sol_agent_wallet.config import get_config


SOLANA_ENV_VARS = (
    "SOLANA_PRIVATE_KEY",
    "SOLANA_NETWORK",
    "SOLANA_RPC_URL",
    "SOLANA_MAX_TX_SOL",
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Strip Solana env vars before every test and reset the config cache."""
    for var in SOLANA_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    get_config.cache_clear()
    yield
    get_config.cache_clear()


@pytest.fixture
def fresh_keypair() -> Keypair:
    """A throw-away keypair — never funded, never recovered."""
    return Keypair()


@pytest.fixture
def fresh_private_key_b58(fresh_keypair: Keypair) -> str:
    return base58.b58encode(bytes(fresh_keypair)).decode()
