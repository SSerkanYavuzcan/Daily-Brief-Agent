from datetime import datetime, timezone

from daily_brief_agent.db import FeedItem, fetch_items_by_date, get_connection, init_db, insert_items


def test_db_dedup(tmp_path):
    db_path = tmp_path / "test.sqlite"
    item = FeedItem(
        item_id="abc",
        fetched_at_utc=datetime(2024, 1, 1, tzinfo=timezone.utc),
        published_raw=None,
        category="Tech",
        source="Example",
        title="Title",
        link="https://example.com",
        summary_raw=None,
    )
    with get_connection(db_path) as conn:
        init_db(conn)
        assert insert_items(conn, [item]) == 1
        assert insert_items(conn, [item]) == 0
        rows = fetch_items_by_date(conn, item.fetched_at_utc.date())
        assert len(rows) == 1
