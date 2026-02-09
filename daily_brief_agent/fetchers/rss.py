from __future__ import annotations

import logging
from typing import Iterable

import feedparser

from daily_brief_agent.config import FeedConfig
from daily_brief_agent.db import FeedItem
from daily_brief_agent.utils.hashing import hash_link
from daily_brief_agent.utils.time import utc_now

logger = logging.getLogger(__name__)


def _canonical_link(entry: dict) -> str | None:
    if link := entry.get("link"):
        return link
    for link_info in entry.get("links", []) or []:
        if link_info.get("rel") == "alternate" and link_info.get("href"):
            return link_info["href"]
    return None


def fetch_feed_items(
    feeds: Iterable[FeedConfig], max_per_feed: int
) -> list[FeedItem]:
    items: list[FeedItem] = []
    fetched_at = utc_now()
    for feed in feeds:
        logger.info("Fetching feed: %s", feed.name)
        try:
            parsed = feedparser.parse(feed.url)
        except Exception:
            logger.exception("Failed to fetch feed %s", feed.url)
            continue
        if parsed.bozo:
            logger.warning("Feed had parsing issues: %s", feed.url)

        for entry in parsed.entries[:max_per_feed]:
            link = _canonical_link(entry)
            if not link:
                logger.debug("Skipping entry without link in %s", feed.name)
                continue
            item = FeedItem(
                item_id=hash_link(link),
                fetched_at_utc=fetched_at,
                published_raw=entry.get("published"),
                category=feed.category,
                source=feed.name,
                title=(entry.get("title") or "(untitled)").strip(),
                link=link,
                summary_raw=entry.get("summary"),
            )
            items.append(item)
    return items
