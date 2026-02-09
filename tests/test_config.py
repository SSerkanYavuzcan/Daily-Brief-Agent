from pathlib import Path

import pytest

from daily_brief_agent.config import ConfigError, load_config


def test_load_config(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
feeds:
  - name: Example
    url: https://example.com/rss
    category: Tech
storage:
  db_path: agentos.sqlite
reports:
  output_dir: reports
telegram:
  enabled: true
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)
    assert config.feeds[0].name == "Example"
    assert config.db_path.name == "agentos.sqlite"
    assert config.reports_dir.name == "reports"
    assert config.telegram.enabled is True


def test_load_config_missing(tmp_path: Path):
    with pytest.raises(ConfigError):
        load_config(tmp_path / "missing.yaml")
