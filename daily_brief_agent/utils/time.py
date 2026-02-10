"""Time utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo


class TimezoneError(ValueError):
    """Raised when timezone is invalid."""


def get_timezone(name: str | None) -> ZoneInfo:
    """Return ZoneInfo for name or UTC if None."""
    if not name:
        return ZoneInfo("UTC")
    try:
        return ZoneInfo(name)
    except Exception as exc:  # pragma: no cover - exact error varies by platform
        raise TimezoneError(f"Invalid timezone '{name}'.") from exc


@dataclass(frozen=True)
class UtcDateRange:
    start: datetime
    end: datetime


def utc_now() -> datetime:
    """Return current UTC datetime with tzinfo."""
    return datetime.now(timezone.utc)


def parse_date(value: str) -> date:
    """Parse YYYY-MM-DD date string."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format.") from exc


def date_range_utc(target: date, tz: ZoneInfo) -> UtcDateRange:
    """Return UTC range for a target date in given timezone."""
    start_local = datetime.combine(target, time.min).replace(tzinfo=tz)
    end_local = datetime.combine(target, time.max).replace(tzinfo=tz)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    return UtcDateRange(start=start_utc, end=end_utc)
