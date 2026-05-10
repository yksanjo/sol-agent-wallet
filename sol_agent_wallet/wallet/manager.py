"""WalletManager — Secure key management for Solana AI agent.

Supports multiple wallet sources:
1. Environment variable (SOLANA_PRIVATE_KEY)
2. Keypair file
3. In-memory keypair
4. Read-only mode (no key needed)
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any

from solders.keypair import Keypair
import base58


class WalletManager:
    """Manages Solana keypairs securely for the AI agent.

    The wallet can operate in two modes:
    - Read-only: No key needed, can only query data
    - Write-capable: Key provided, can execute transactions
    """

    def __init__(self, keypair: Keypair | None = None):
        self._keypair = keypair
        self._read_only = keypair is None

    @classmethod
    def from_env(cls) -> "WalletManager":
        """Create wallet from SOLANA_PRIVATE_KEY environment variable."""
        private_key_b58 = os.getenv("SOLANA_PRIVATE_KEY")
        if not private_key_b58:
            return cls()  # Read-only mode
        try:
            private_key_bytes = base58.b58decode(private_key_b58)
            keypair = Keypair.from_bytes(private_key_bytes)
            return cls(keypair)
        except Exception as e:
            raise ValueError(f"Invalid SOLANA_PRIVATE_KEY: {e}")

    @classmethod
    def from_file(cls, path: str | Path) -> "WalletManager":
        """Create wallet from a keypair file.

        Supports:
        - Solana CLI JSON format (array of 64 bytes)
        - Base58 encoded private key
        - Phantom export format
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Keypair file not found: {path}")

        content = path.read_text().strip()

        try:
            # Try JSON array format (Solana CLI)
            key_bytes = json.loads(content)
            if isinstance(key_bytes, list) and len(key_bytes) == 64:
                keypair = Keypair.from_bytes(bytes(key_bytes))
                return cls(keypair)
        except json.JSONDecodeError:
            pass

        try:
            # Try base58 format
            key_bytes = base58.b58decode(content)
            keypair = Keypair.from_bytes(key_bytes)
            return cls(keypair)
        except Exception:
            pass

        raise ValueError(f"Could not parse keypair file: {path}")

    @classmethod
    def from_private_key(cls, private_key: str) -> "WalletManager":
        """Create wallet from a base58-encoded private key."""
        try:
            key_bytes = base58.b58decode(private_key)
            keypair = Keypair.from_bytes(key_bytes)
            return cls(keypair)
        except Exception as e:
            raise ValueError(f"Invalid private key: {e}")

    @property
    def is_read_only(self) -> bool:
        """Whether the wallet is in read-only mode."""
        return self._read_only

    @property
    def address(self) -> str | None:
        """Get the wallet address, or None if read-only."""
        if self._keypair:
            return str(self._keypair.pubkey())
        return None

    @property
    def keypair(self) -> Keypair | None:
        """Get the keypair, or None if read-only."""
        return self._keypair

    def require_write(self) -> Keypair:
        """Require write access. Raises error if read-only."""
        if self._read_only or not self._keypair:
            raise PermissionError(
                "Write operations require a private key. "
                "Set SOLANA_PRIVATE_KEY environment variable or pass a keypair."
            )
        return self._keypair

    def get_public_key(self) -> str:
        """Get the public key as a base58 string."""
        if self._keypair:
            return str(self._keypair.pubkey())
        return "Read-only mode (no wallet connected)"

    def __str__(self) -> str:
        if self._read_only:
            return "Wallet: Read-only mode"
        return f"Wallet: {self.address}"
