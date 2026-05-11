"""Runtime configuration loaded from environment variables.

Security defaults:
- Network defaults to devnet. Set SOLANA_NETWORK=mainnet-beta to opt in to real funds.
- Per-transaction SOL cap defaults to 1.0. Override with SOLANA_MAX_TX_SOL.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


NETWORK_RPC: dict[str, str] = {
    "devnet": "https://api.devnet.solana.com",
    "mainnet-beta": "https://api.mainnet-beta.solana.com",
    "testnet": "https://api.testnet.solana.com",
}

DEFAULT_NETWORK = "devnet"
DEFAULT_MAX_TX_SOL = 1.0


class ConfigError(ValueError):
    """Raised when environment configuration is invalid."""


@dataclass(frozen=True)
class Config:
    network: str
    rpc_endpoint: str
    max_tx_sol: float

    @property
    def is_mainnet(self) -> bool:
        return self.network == "mainnet-beta"

    @property
    def solscan_suffix(self) -> str:
        # Solscan uses ?cluster=devnet|testnet|custom for non-mainnet
        if self.network in ("devnet", "testnet"):
            return f"?cluster={self.network}"
        if self.network == "custom":
            return "?cluster=custom"
        return ""

    def check_tx_cap(self, amount_sol: float) -> None:
        """Raise if amount exceeds the per-tx SOL cap."""
        if amount_sol > self.max_tx_sol:
            raise TxCapExceeded(
                f"Transaction amount {amount_sol} SOL exceeds the per-tx cap of "
                f"{self.max_tx_sol} SOL. Raise the cap with "
                f"`export SOLANA_MAX_TX_SOL={amount_sol * 2:g}` (or higher) and restart."
            )


class TxCapExceeded(PermissionError):
    """Raised when a transaction would exceed the configured SOL cap."""


def _resolve_rpc(network: str) -> tuple[str, str]:
    """Return (canonical_network_name, rpc_endpoint)."""
    explicit = os.getenv("SOLANA_RPC_URL")
    if explicit:
        return ("custom", explicit)
    if network in NETWORK_RPC:
        return (network, NETWORK_RPC[network])
    if network.startswith("http://") or network.startswith("https://"):
        return ("custom", network)
    raise ConfigError(
        f"SOLANA_NETWORK={network!r} is not recognized. "
        f"Use one of {sorted(NETWORK_RPC)} or a full RPC URL."
    )


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Load and cache config from env. Reset with `get_config.cache_clear()` in tests."""
    network_raw = os.getenv("SOLANA_NETWORK", DEFAULT_NETWORK).strip().lower()
    network, rpc_endpoint = _resolve_rpc(network_raw)

    cap_raw = os.getenv("SOLANA_MAX_TX_SOL", str(DEFAULT_MAX_TX_SOL))
    try:
        max_tx_sol = float(cap_raw)
    except ValueError as exc:
        raise ConfigError(f"SOLANA_MAX_TX_SOL={cap_raw!r} is not a number") from exc
    if max_tx_sol <= 0:
        raise ConfigError(f"SOLANA_MAX_TX_SOL must be positive, got {max_tx_sol}")

    return Config(network=network, rpc_endpoint=rpc_endpoint, max_tx_sol=max_tx_sol)
