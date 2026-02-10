"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from daily_brief_agent.utils.time import TimezoneError, get_timezone


class ConfigError(ValueError):
    """Raised when configuration is invalid."""


@dataclass(frozen=True)
class StorageConfig:
    db_path: Path
    reports_dir: Path


@dataclass(frozen=True)
class FeedConfig:
    name: str
    url: str
    category: str


@dataclass(frozen=True)
class TelegramConfig:
    enabled: bool


@dataclass(frozen=True)
class DeliveryConfig:
    telegram: TelegramConfig


@dataclass(frozen=True)
class AppConfig:
    storage: StorageConfig
    feeds: list[FeedConfig]
    delivery: DeliveryConfig
    timezone: str | None = None

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "storage": {
                "db_path": str(self.storage.db_path),
                "reports_dir": str(self.storage.reports_dir),
            },
            "feeds": [
                {"name": feed.name, "url": feed.url, "category": feed.category}
                for feed in self.feeds
            ],
            "delivery": {"telegram": {"enabled": self.delivery.telegram.enabled}},
            "timezone": self.timezone,
        }


def _require_mapping(data: Any, context: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ConfigError(f"{context} must be a mapping.")
    return data


def _require_str(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{context} must be a non-empty string.")
    return value.strip()


def _require_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{context} must be a boolean.")
    return value


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError("Config file is not valid YAML.") from exc

    raw = _require_mapping(raw, "Config root")

    storage_raw = _require_mapping(raw.get("storage"), "storage")
    db_path = _require_str(storage_raw.get("db_path"), "storage.db_path")
    reports_dir = _require_str(storage_raw.get("reports_dir"), "storage.reports_dir")
    storage = StorageConfig(db_path=Path(db_path), reports_dir=Path(reports_dir))

    feeds_raw = raw.get("feeds")
    if not isinstance(feeds_raw, list) or not feeds_raw:
        raise ConfigError("feeds must be a non-empty list.")
    feeds: list[FeedConfig] = []
    for index, feed in enumerate(feeds_raw, start=1):
        feed_map = _require_mapping(feed, f"feeds[{index}]")
        name = _require_str(feed_map.get("name"), f"feeds[{index}].name")
        url = _require_str(feed_map.get("url"), f"feeds[{index}].url")
        category = _require_str(feed_map.get("category"), f"feeds[{index}].category")
        feeds.append(FeedConfig(name=name, url=url, category=category))

    delivery_raw = _require_mapping(raw.get("delivery") or {}, "delivery")
    telegram_raw = _require_mapping(delivery_raw.get("telegram") or {}, "delivery.telegram")
    telegram_enabled = telegram_raw.get("enabled", False)
    telegram = TelegramConfig(enabled=_require_bool(telegram_enabled, "delivery.telegram.enabled"))

    timezone_value = raw.get("timezone")
    if timezone_value is not None:
        timezone_value = _require_str(timezone_value, "timezone")
        try:
            get_timezone(timezone_value)
        except TimezoneError as exc:
            raise ConfigError(str(exc)) from exc

    return AppConfig(
        storage=storage,
        feeds=feeds,
        delivery=DeliveryConfig(telegram=telegram),
        timezone=timezone_value,
    )
