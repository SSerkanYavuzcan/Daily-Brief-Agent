"""RSS fetching."""

from __future__ import annotations

from typing import Any

import feedparser

from daily_brief_agent.utils.hashing import sha256_hex


def _select_canonical_link(entry: dict[str, Any]) -> str | None:
    links = entry.get("links") or []
    for link in links:
        if link.get("rel") == "alternate" and link.get("href"):
            return link["href"]
    return entry.get("link")


def fetch_feed(
    feed_name: str, url: str, category: str, max_entries: int
) -> list[dict[str, str | None]]:
    parsed = feedparser.parse(url)
    if parsed.bozo:
        raise ValueError(parsed.bozo_exception)

    items: list[dict[str, str | None]] = []
    for entry in parsed.entries[:max_entries]:
        link = _select_canonical_link(entry) or ""
        if not link:
            continue
        item = {
            "id": sha256_hex(link),
            "published_raw": entry.get("published") or entry.get("updated"),
            "category": category,
            "source": feed_name,
            "title": entry.get("title") or "(untitled)",
            "link": link,
            "summary_raw": entry.get("summary") or entry.get("description"),
        }
        items.append(item)
    return items
