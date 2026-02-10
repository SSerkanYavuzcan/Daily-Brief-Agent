"""Markdown report generation."""

from __future__ import annotations

from collections import defaultdict
from datetime import date


def generate_report(
    items: list[dict[str, str | None]],
    report_date: date,
    per_category_limit: int,
) -> str:
    grouped: dict[str, dict[str, list[dict[str, str | None]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for item in items:
        grouped[item["category"]][item["source"]].append(item)

    lines: list[str] = [f"# Daily Brief — {report_date:%Y-%m-%d}", ""]

    for category in sorted(grouped):
        lines.append(f"## {category}")
        sources = grouped[category]
        category_items: list[tuple[str, dict[str, str | None]]] = []
        for source, source_items in sources.items():
            sorted_items = sorted(source_items, key=lambda x: (x["title"] or ""))
            category_items.extend((source, item) for item in sorted_items)

        category_items = sorted(
            category_items, key=lambda x: (x[0], x[1]["title"] or "")
        )[:per_category_limit]

        for source, item in category_items:
            published = item.get("published_raw")
            published_suffix = f" — {published}" if published else ""
            lines.append(f"- **{item['title']}** ({source}{published_suffix})")
            lines.append(f"  - {item['link']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
