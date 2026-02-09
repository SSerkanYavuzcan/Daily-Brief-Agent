from __future__ import annotations

import hashlib


def hash_link(link: str) -> str:
    """Return a deterministic SHA-256 hex digest for a link."""
    return hashlib.sha256(link.encode("utf-8")).hexdigest()
