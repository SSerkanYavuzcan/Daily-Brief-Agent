from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FeedItem:
    item_id: str
    fetched_at_utc: datetime
    published_raw: str | None
    category: str
    source: str
    title: str
    link: str
    summary_raw: str | None


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            fetched_at_utc TEXT NOT NULL,
            published_raw TEXT,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            summary_raw TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_items_fetched_at ON items(fetched_at_utc)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_source ON items(source)")
    conn.commit()


def insert_items(
    conn: sqlite3.Connection, items: Iterable[FeedItem], dry_run: bool = False
) -> int:
    if dry_run:
        return 0
    rows = [
        (
            item.item_id,
            item.fetched_at_utc.isoformat(),
            item.published_raw,
            item.category,
            item.source,
            item.title,
            item.link,
            item.summary_raw,
        )
        for item in items
    ]
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR IGNORE INTO items (
            id,
            fetched_at_utc,
            published_raw,
            category,
            source,
            title,
            link,
            summary_raw
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return cursor.rowcount


def fetch_items_by_date(
    conn: sqlite3.Connection, target_date: datetime.date, include_history: bool = False
) -> list[sqlite3.Row]:
    if include_history:
        cursor = conn.execute(
            """
            SELECT * FROM items
            ORDER BY fetched_at_utc ASC
            """
        )
        return list(cursor.fetchall())

    start = f"{target_date.isoformat()}T00:00:00"
    end = f"{target_date.isoformat()}T23:59:59.999999"
    cursor = conn.execute(
        """
        SELECT * FROM items
        WHERE fetched_at_utc BETWEEN ? AND ?
        ORDER BY fetched_at_utc ASC
        """,
        (start, end),
    )
    return list(cursor.fetchall())
