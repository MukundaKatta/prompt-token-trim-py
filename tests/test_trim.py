"""Tests for ``prompt_token_trim.trim``."""

import pytest

from prompt_token_trim import TrimResult, estimate_tokens, trim, trim_messages


def _msgs(*pairs):
    out = []
    for p in pairs:
        d = {"role": p[0], "content": p[1]}
        if len(p) >= 3:
            d["priority"] = p[2]
        out.append(d)
    return out


def test_trim_returns_TrimResult():
    result = trim([], budget=100)
    assert isinstance(result, TrimResult)
    assert result.messages == []
    assert result.tokens == 0
    assert result.dropped == 0


def test_trim_under_budget_keeps_all():
    msgs = _msgs(("user", "hello"), ("assistant", "hi"))
    result = trim(msgs, budget=100)
    assert len(result.messages) == 2
    assert result.dropped == 0


def test_trim_drops_lowest_priority_first():
    msgs = _msgs(
        ("user", "x" * 40, 1),   # 10 tokens
        ("user", "x" * 40, 10),  # 10 tokens
        ("user", "x" * 40, 5),   # 10 tokens
    )
    result = trim(msgs, budget=20, preserve_system=False)
    contents = [m["content"] for m in result.messages]
    assert len(contents) == 2
    # Highest-priority pair wins.
    assert msgs[1] in result.messages  # priority=10
    assert msgs[2] in result.messages  # priority=5
    assert msgs[0] not in result.messages  # priority=1


def test_trim_preserves_original_order_in_output():
    msgs = _msgs(
        ("user", "first",  1),
        ("user", "second", 10),
        ("user", "third",  5),
    )
    result = trim(msgs, budget=100)
    assert [m["content"] for m in result.messages] == ["first", "second", "third"]


def test_trim_preserve_system_keeps_system_even_over_budget():
    msgs = _msgs(
        ("system", "S" * 80),  # 20 tokens
        ("user",   "U" * 40, 10),  # 10 tokens
    )
    result = trim(msgs, budget=5, preserve_system=True)
    roles = [m["role"] for m in result.messages]
    assert "system" in roles


def test_trim_preserve_system_false_lets_system_drop():
    msgs = _msgs(
        ("system", "S" * 80),
        ("user",   "U" * 40, 10),
    )
    result = trim(msgs, budget=5, preserve_system=False)
    roles = [m["role"] for m in result.messages]
    assert roles == [] or "system" not in roles


def test_trim_negative_budget_raises():
    with pytest.raises(TypeError):
        trim([], budget=-1)


def test_trim_messages_alias_works():
    msgs = _msgs(("user", "hi", 1))
    result = trim_messages(msgs, max_tokens=100)
    assert result.messages == msgs


def test_estimate_tokens_basic():
    assert estimate_tokens("") == 0
    assert estimate_tokens(None) == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcdefgh") == 2
