"""Trim prompt messages to fit a token budget while preserving priority.

Mirrors the JS sibling:

1. Sort messages by ``priority`` (descending; default ``0``).
2. Walk in that order; accept each if its tokens fit the remaining budget.
3. Re-emit kept messages in their **original** order (so the prompt reads
   naturally for the LLM).

The Python addition: ``preserve_system=True`` (default) always keeps
``role == "system"`` entries even if they overflow the budget.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Mapping


@dataclass
class TrimResult:
    """Result of :func:`trim`.

    Attributes:
        messages: Kept messages, restored to original order.
        tokens: Total tokens consumed.
        dropped: Count of messages dropped.
    """

    messages: List[dict]
    tokens: int
    dropped: int


def estimate_tokens(text) -> int:
    """``ceil(len(text) / 4)`` -- matches the JS sibling's heuristic."""
    s = "" if text is None else str(text)
    if not s:
        return 0
    return math.ceil(len(s) / 4)


def _priority_of(msg: Mapping) -> float:
    p = msg.get("priority") if isinstance(msg, Mapping) else None
    return float(p) if p is not None else 0.0


def _is_system(msg: Mapping) -> bool:
    return isinstance(msg, Mapping) and msg.get("role") == "system"


def trim(
    messages: Iterable[Mapping],
    budget: int,
    *,
    preserve_system: bool = True,
) -> TrimResult:
    """Trim ``messages`` to fit under ``budget`` tokens by priority.

    Order of operations:

    1. Always-keep system messages first (if ``preserve_system``); they
       consume the budget but cannot be dropped.
    2. Sort the rest by priority desc; greedily accept those that fit.
    3. Re-emit kept messages in original order.
    """
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget < 0:
        raise TypeError("trim: budget must be a non-negative number")
    if messages is None:
        raise TypeError("trim: messages must be iterable, got None")

    # Tag each message with its original index so we can restore order at the end.
    tagged: List[tuple] = []
    for index, msg in enumerate(messages):
        if not isinstance(msg, Mapping):
            continue
        tokens = estimate_tokens(msg.get("content", ""))
        tagged.append((index, dict(msg), tokens))

    used = 0
    kept_indices: set = set()

    # Pass 1: protected systems first (in original order).
    if preserve_system:
        for index, msg, tokens in tagged:
            if _is_system(msg):
                kept_indices.add(index)
                used += tokens

    # Pass 2: priority-sorted greedy. Skip already-kept (system) entries.
    by_priority = sorted(
        (t for t in tagged if t[0] not in kept_indices),
        key=lambda t: -_priority_of(t[1]),
    )
    for index, msg, tokens in by_priority:
        if used + tokens <= budget:
            kept_indices.add(index)
            used += tokens

    kept = [msg for index, msg, _ in tagged if index in kept_indices]
    dropped = len(tagged) - len(kept)
    return TrimResult(messages=kept, tokens=used, dropped=dropped)


def trim_messages(messages: Iterable[Mapping], *, max_tokens: int) -> TrimResult:
    """JS-parity alias for ``trimMessages(messages, {maxTokens})``."""
    return trim(messages, budget=max_tokens, preserve_system=False)
