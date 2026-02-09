from __future__ import annotations

from datetime import date, datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def utc_date(dt: datetime) -> date:
    return dt.astimezone(timezone.utc).date()
