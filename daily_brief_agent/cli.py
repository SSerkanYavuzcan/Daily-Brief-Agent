from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

from daily_brief_agent import __version__
from daily_brief_agent.config import ConfigError, load_config
from daily_brief_agent.db import FeedItem, fetch_items_by_date, get_connection, init_db, insert_items
from daily_brief_agent.delivery.telegram import send_notification
from daily_brief_agent.fetchers.rss import fetch_feed_items
from daily_brief_agent.reporting.markdown import generate_report, write_report
from daily_brief_agent.utils.time import parse_date, utc_date, utc_now

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily Brief Agent")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    parser.add_argument("--max-per-feed", type=int, default=50)
    parser.add_argument("--per-category-limit", type=int, default=30)
    parser.add_argument("--no-telegram", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-history", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _report_path(reports_dir: Path, target_date: date) -> Path:
    filename = f"{target_date.isoformat()}.md"
    return reports_dir / filename


def _items_to_rows(items: Iterable[FeedItem]) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        rows.append(
            {
                "title": item.title,
                "source": item.source,
                "published_raw": item.published_raw,
                "category": item.category,
                "link": item.link,
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    load_dotenv()

    try:
        config = load_config(Path(args.config))
    except ConfigError as exc:
        logger.error("Config error: %s", exc)
        return 1

    target_date = parse_date(args.date) if args.date else utc_date(utc_now())
    logger.info("Generating report for %s", target_date.isoformat())

    items = fetch_feed_items(config.feeds, max_per_feed=args.max_per_feed)

    report_content: str
    report_path = _report_path(config.reports_dir, target_date)

    if args.dry_run:
        report_content = generate_report(
            _items_to_rows(items), target_date, args.per_category_limit
        )
        print(report_content)
    else:
        with get_connection(config.db_path) as conn:
            init_db(conn)
            inserted = insert_items(conn, items)
            logger.info("Inserted %s new items", inserted)
            rows = fetch_items_by_date(conn, target_date, args.include_history)
            report_content = generate_report(rows, target_date, args.per_category_limit)
            write_report(report_content, report_path)
            logger.info("Report written to %s", report_path)

    if not args.dry_run:
        if args.no_telegram:
            logger.info("Telegram disabled by CLI flag.")
        else:
            message = (
                f"Daily Brief ready: {target_date.isoformat()} — {len(items)} new items. "
                f"Report: {report_path}"
            )
            send_notification(message, enabled=config.telegram.enabled)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
