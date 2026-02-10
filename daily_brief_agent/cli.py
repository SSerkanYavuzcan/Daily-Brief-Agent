"""Command-line interface."""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv

from daily_brief_agent.config import AppConfig, ConfigError, load_config
from daily_brief_agent.db import init_db, insert_items, query_items_for_date
from daily_brief_agent.delivery.telegram import send_telegram_message
from daily_brief_agent.fetchers.rss import fetch_feed
from daily_brief_agent.reporting.markdown import generate_report
from daily_brief_agent.utils.time import date_range_utc, get_timezone, parse_date, utc_now


def _configure_logging(verbose: bool) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger("daily_brief_agent")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily Brief Agent")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--date", help="Target date YYYY-MM-DD")
    parser.add_argument("--max-per-feed", type=int, default=50)
    parser.add_argument("--per-category-limit", type=int, default=30)
    parser.add_argument("--include-history", action="store_true")
    parser.add_argument("--no-telegram", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--print-config", action="store_true")
    return parser


def _load_config(path: str, logger: logging.Logger) -> AppConfig:
    try:
        return load_config(path)
    except ConfigError as exc:
        logger.error(str(exc))
        raise


def _collect_items(config: AppConfig, max_per_feed: int, logger: logging.Logger) -> list[dict]:
    items: list[dict] = []
    fetched_at = utc_now().isoformat()
    for feed in config.feeds:
        try:
            feed_items = fetch_feed(feed.name, feed.url, feed.category, max_per_feed)
        except Exception as exc:
            logger.error("Failed to fetch feed %s: %s", feed.name, exc)
            continue
        for item in feed_items:
            item["fetched_at_utc"] = fetched_at
        items.extend(feed_items)
    return items


def _write_report(report_path: Path, content: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    logger = _configure_logging(args.verbose)
    load_dotenv()

    try:
        config = _load_config(args.config, logger)
    except ConfigError:
        sys.exit(1)

    if args.print_config:
        import yaml

        print(yaml.safe_dump(config.to_safe_dict(), sort_keys=False))
        return

    tz = get_timezone(config.timezone)
    target_date = parse_date(args.date) if args.date else utc_now().astimezone(tz).date()

    items = _collect_items(config, args.max_per_feed, logger)
    if args.dry_run:
        logger.info("Dry run enabled: skipping database writes.")
        report = generate_report(items, target_date, args.per_category_limit)
        print(report)
        return

    db_path = config.storage.db_path
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    init_db(conn)
    inserted_count = insert_items(conn, items)
    logger.info("Inserted %s new items.", inserted_count)

    date_range = date_range_utc(target_date, tz)
    rows = query_items_for_date(conn, date_range.start, date_range.end, args.include_history)
    conn.close()

    report_items = [dict(row) for row in rows]
    report = generate_report(report_items, target_date, args.per_category_limit)

    report_path = config.storage.reports_dir / f"{target_date:%Y-%m-%d}.md"
    _write_report(report_path, report)
    logger.info("Report written to %s", report_path)

    if config.delivery.telegram.enabled and not args.no_telegram:
        message = (
            f"Daily Brief ready: {target_date:%Y-%m-%d} — {inserted_count} new items. "
            f"Report: {report_path.resolve()}"
        )
        send_telegram_message(message, logger)


if __name__ == "__main__":
    main()
