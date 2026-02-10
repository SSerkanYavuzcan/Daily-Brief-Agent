from datetime import date

from daily_brief_agent.reporting.markdown import generate_report


def test_report_grouping_order():
    items = [
        {
            "category": "Tech",
            "source": "Beta",
            "title": "Zeta",
            "link": "https://example.com/zeta",
            "published_raw": None,
        },
        {
            "category": "Business",
            "source": "Alpha",
            "title": "Alpha News",
            "link": "https://example.com/alpha",
            "published_raw": "2024-01-01",
        },
        {
            "category": "Tech",
            "source": "Alpha",
            "title": "Alpha Tech",
            "link": "https://example.com/alpha-tech",
            "published_raw": None,
        },
    ]

    report = generate_report(items, date(2024, 1, 2), per_category_limit=30)
    business_index = report.index("## Business")
    tech_index = report.index("## Tech")
    assert business_index < tech_index

    lines = report.splitlines()
    tech_start = lines.index("## Tech") + 1
    tech_section = []
    for line in lines[tech_start:]:
        if line.startswith("## "):
            break
        if line.startswith("- **"):
            tech_section.append(line)

    assert "Alpha Tech" in tech_section[0]
