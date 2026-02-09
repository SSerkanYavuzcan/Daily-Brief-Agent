from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class FeedConfig:
    name: str
    url: str
    category: str


@dataclass(frozen=True)
class TelegramConfig:
    enabled: bool


@dataclass(frozen=True)
class AppConfig:
    feeds: list[FeedConfig]
    db_path: Path
    reports_dir: Path
    telegram: TelegramConfig


class ConfigError(ValueError):
    pass


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"Expected '{name}' to be a mapping.")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConfigError(f"Expected '{name}' to be a list.")
    return value


def _require_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Expected '{name}' to be a non-empty string.")
    return value.strip()


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        raise ConfigError("Config file is empty.")
    root = _require_mapping(data, "config")

    feeds_data = _require_list(root.get("feeds"), "feeds")
    feeds: list[FeedConfig] = []
    for idx, feed in enumerate(feeds_data, start=1):
        feed_map = _require_mapping(feed, f"feeds[{idx}]")
        feeds.append(
            FeedConfig(
                name=_require_str(feed_map.get("name"), f"feeds[{idx}].name"),
                url=_require_str(feed_map.get("url"), f"feeds[{idx}].url"),
                category=_require_str(
                    feed_map.get("category"), f"feeds[{idx}].category"
                ),
            )
        )

    storage = _require_mapping(root.get("storage"), "storage")
    db_path = Path(_require_str(storage.get("db_path"), "storage.db_path"))

    reports = _require_mapping(root.get("reports"), "reports")
    reports_dir = Path(
        _require_str(reports.get("output_dir"), "reports.output_dir")
    )

    telegram = _require_mapping(root.get("telegram"), "telegram")
    telegram_enabled = bool(telegram.get("enabled", False))

    return AppConfig(
        feeds=feeds,
        db_path=db_path,
        reports_dir=reports_dir,
        telegram=TelegramConfig(enabled=telegram_enabled),
    )
