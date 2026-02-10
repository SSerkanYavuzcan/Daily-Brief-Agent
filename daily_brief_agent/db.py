"""SQLite access layer."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Iterable


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            fetched_at_utc TEXT NOT NULL,
            published_raw TEXT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            summary_raw TEXT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_fetched_at ON items (fetched_at_utc)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items (category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_source ON items (source)")
    conn.commit()


def insert_items(conn: sqlite3.Connection, items: Iterable[dict[str, str | None]]) -> int:
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR IGNORE INTO items (
            id, fetched_at_utc, published_raw, category, source, title, link, summary_raw
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["id"],
                item["fetched_at_utc"],
                item.get("published_raw"),
                item["category"],
                item["source"],
                item["title"],
                item["link"],
                item.get("summary_raw"),
            )
            for item in items
        ],
    )
    conn.commit()
    return cursor.rowcount


def query_items_for_date(
    conn: sqlite3.Connection,
    start_utc: datetime,
    end_utc: datetime,
    include_history: bool,
) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    if include_history:
        cursor = conn.execute("SELECT * FROM items")
    else:
        cursor = conn.execute(
            "SELECT * FROM items WHERE fetched_at_utc BETWEEN ? AND ?",
            (start_utc.isoformat(), end_utc.isoformat()),
        )
    return cursor.fetchall()
