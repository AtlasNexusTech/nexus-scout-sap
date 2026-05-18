"""
x402 Payment Handler — Solana USDC micropayments for Ace Data Cloud.

Uses the acedatacloud-x402 package to sign payment envelopes with a Solana
keypair. Supports both sync and async AceDataCloud clients.

No API key needed — payments flow automatically on 402 responses.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from acedatacloud_x402 import create_x402_payment_handler, SolanaKeypairSigner

logger = logging.getLogger(__name__)


def load_solana_signer(private_key_b58: Optional[str] = None) -> SolanaKeypairSigner:
    """Load Solana keypair from base58 string or env var.

    Priority: explicit param > SOLANA_PRIVATE_KEY_BASE58 env var
    """
    key = private_key_b58 or os.getenv("SOLANA_PRIVATE_KEY_BASE58")
    if not key:
        raise ValueError(
            "Solana private key required for x402 payments. "
            "Set SOLANA_PRIVATE_KEY_BASE58 or pass private_key_b58."
        )
    return SolanaKeypairSigner.from_base58(key)


def create_solana_x402_handler(
    private_key_b58: Optional[str] = None,
) -> Optional[callable]:
    """Create x402 payment handler for Solana USDC payments.

    Returns None if no private key is configured (dry-run mode).
    """
    try:
        signer = load_solana_signer(private_key_b58)
    except ValueError:
        logger.warning("⚠️ No SOLANA_PRIVATE_KEY_BASE58 — x402 payments disabled (dry-run)")
        return None
    return create_x402_payment_handler(
        network="solana",
        solana_signer=signer,
    )


class X402PaymentTracker:
    """Track and log x402 payments for audit trail."""

    def __init__(self):
        self.payments: list[dict] = []
        self.total_usdc: float = 0.0

    def record(self, service: str, amount: float, tx_id: str = ""):
        """Record a payment event."""
        entry = {
            "service": service,
            "amount_usdc": amount,
            "tx_id": tx_id,
        }
        self.payments.append(entry)
        self.total_usdc += amount
        logger.info(f"💳 x402 payment: {service} — ${amount:.6f} USDC")
        return entry

    @property
    def summary(self) -> dict:
        """Payment summary for reporting."""
        return {
            "total_payments": len(self.payments),
            "total_usdc": round(self.total_usdc, 6),
            "by_service": self._by_service(),
        }

    def _by_service(self) -> dict:
        """Group payments by service."""
        groups: dict[str, float] = {}
        for p in self.payments:
            svc = p["service"]
            groups[svc] = groups.get(svc, 0) + p["amount_usdc"]
        return groups
