from datetime import date

from daily_brief_agent.reporting.markdown import generate_report


def test_report_grouping():
    items = [
        {
            "title": "First",
            "source": "Source A",
            "published_raw": "2024-01-01",
            "category": "Tech",
            "link": "https://example.com/1",
        },
        {
            "title": "Second",
            "source": "Source B",
            "published_raw": None,
            "category": "Science",
            "link": "https://example.com/2",
        },
    ]
    report = generate_report(items, date(2024, 1, 1), per_category_limit=10)
    assert "## Science" in report
    assert "## Tech" in report
    assert "**First**" in report
    assert "**Second**" in report
