from daily_brief_agent.utils.hashing import hash_link


def test_hash_link_deterministic():
    link = "https://example.com/item"
    assert hash_link(link) == hash_link(link)
    assert hash_link(link) != hash_link("https://example.com/other")
