"""Hashing utilities."""

from __future__ import annotations

import hashlib


def sha256_hex(value: str) -> str:
    """Return a SHA-256 hex digest for the given string."""
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
