from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable


def _format_item(row) -> list[str]:
    title = row["title"]
    source = row["source"]
    published = row["published_raw"]
    line = f"- **{title}** ({source})"
    if published:
        line += f" — {published}"
    return [line, f"  {row['link']}"]


def generate_report(
    items: Iterable, target_date: date, per_category_limit: int
) -> str:
    grouped: dict[str, list] = defaultdict(list)
    for row in items:
        grouped[row["category"]].append(row)

    lines: list[str] = [f"# Daily Brief — {target_date.isoformat()}", ""]

    for category in sorted(grouped.keys()):
        lines.append(f"## {category}")
        category_items = grouped[category][:per_category_limit]
        for row in category_items:
            lines.extend(_format_item(row))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def write_report(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
