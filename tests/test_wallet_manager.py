"""Tests for the key-management entry points."""

from __future__ import annotations

import json
from pathlib import Path

import base58
import pytest
from solders.keypair import Keypair

from sol_agent_wallet.wallet.manager import WalletManager


def test_read_only_without_env():
    wallet = WalletManager.from_env()
    assert wallet.is_read_only
    assert wallet.address is None
    assert wallet.keypair is None


def test_from_env_loads_base58_key(monkeypatch, fresh_keypair, fresh_private_key_b58):
    monkeypatch.setenv("SOLANA_PRIVATE_KEY", fresh_private_key_b58)
    wallet = WalletManager.from_env()
    assert not wallet.is_read_only
    assert wallet.address == str(fresh_keypair.pubkey())


def test_from_env_rejects_garbage(monkeypatch):
    monkeypatch.setenv("SOLANA_PRIVATE_KEY", "not-a-valid-base58-key!!!!")
    with pytest.raises(ValueError):
        WalletManager.from_env()


def test_from_private_key_round_trip(fresh_keypair, fresh_private_key_b58):
    wallet = WalletManager.from_private_key(fresh_private_key_b58)
    assert wallet.address == str(fresh_keypair.pubkey())


def test_require_write_blocks_read_only():
    wallet = WalletManager()
    with pytest.raises(PermissionError):
        wallet.require_write()


def test_require_write_returns_keypair(fresh_keypair):
    wallet = WalletManager(fresh_keypair)
    assert wallet.require_write() is fresh_keypair


def test_from_file_json_array(tmp_path: Path, fresh_keypair):
    path = tmp_path / "id.json"
    path.write_text(json.dumps(list(bytes(fresh_keypair))))
    wallet = WalletManager.from_file(path)
    assert wallet.address == str(fresh_keypair.pubkey())


def test_from_file_base58(tmp_path: Path, fresh_keypair, fresh_private_key_b58):
    path = tmp_path / "key.txt"
    path.write_text(fresh_private_key_b58)
    wallet = WalletManager.from_file(path)
    assert wallet.address == str(fresh_keypair.pubkey())


def test_from_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        WalletManager.from_file(tmp_path / "nope.json")


def test_from_file_unparseable_raises(tmp_path: Path):
    path = tmp_path / "garbage.txt"
    path.write_text("definitely not a key")
    with pytest.raises(ValueError):
        WalletManager.from_file(path)
