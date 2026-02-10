import pytest

from daily_brief_agent.utils.hashing import sha256_hex


def test_sha256_hex_consistency():
    first = sha256_hex("hello")
    second = sha256_hex("hello")
    assert first == second


def test_sha256_hex_type_error():
    with pytest.raises(TypeError):
        sha256_hex(123)  # type: ignore[arg-type]
