import sqlite3

from daily_brief_agent.db import init_db, insert_items
from daily_brief_agent.utils.hashing import sha256_hex
from daily_brief_agent.utils.time import utc_now


def test_db_dedup_inserts_once():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    now = utc_now().isoformat()
    item = {
        "id": sha256_hex("https://example.com"),
        "fetched_at_utc": now,
        "published_raw": None,
        "category": "Tech",
        "source": "Example",
        "title": "Example Title",
        "link": "https://example.com",
        "summary_raw": None,
    }

    first_count = insert_items(conn, [item])
    second_count = insert_items(conn, [item])

    cursor = conn.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]
    conn.close()

    assert first_count == 1
    assert second_count == 0
    assert total == 1
