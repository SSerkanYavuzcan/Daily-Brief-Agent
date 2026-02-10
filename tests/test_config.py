from pathlib import Path

import pytest
import yaml

from daily_brief_agent.config import ConfigError, load_config


def _write_config(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_load_config_success(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        {
            "storage": {"db_path": "brief.sqlite", "reports_dir": "reports"},
            "feeds": [
                {"name": "Feed", "url": "https://example.com/rss", "category": "Tech"}
            ],
            "delivery": {"telegram": {"enabled": False}},
            "timezone": "UTC",
        },
    )
    config = load_config(config_path)
    assert config.storage.db_path.name == "brief.sqlite"
    assert config.feeds[0].name == "Feed"


def test_load_config_missing_feeds(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        {
            "storage": {"db_path": "brief.sqlite", "reports_dir": "reports"},
            "feeds": [],
            "delivery": {"telegram": {"enabled": False}},
        },
    )
    with pytest.raises(ConfigError):
        load_config(config_path)


def test_load_config_invalid_timezone(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        {
            "storage": {"db_path": "brief.sqlite", "reports_dir": "reports"},
            "feeds": [
                {"name": "Feed", "url": "https://example.com/rss", "category": "Tech"}
            ],
            "delivery": {"telegram": {"enabled": False}},
            "timezone": "Invalid/Timezone",
        },
    )
    with pytest.raises(ConfigError):
        load_config(config_path)
