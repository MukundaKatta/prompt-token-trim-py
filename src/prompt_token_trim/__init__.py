"""prompt_token_trim -- trim prompt messages to fit a token budget.

Public surface (mirrors the JS sibling):

* ``trim(messages, budget, *, preserve_system=True)`` -- priority-based trim.
* ``trim_messages(messages, *, max_tokens=...)`` -- JS-parity alias.
* ``estimate_tokens(text)`` -- ``ceil(len(text) / 4)`` heuristic.
* ``TrimResult`` -- dataclass returned by :func:`trim`.

Note: prompt-token-trim is **message-level** priority trimming. For full
history-fitting strategies (drop-oldest, drop-middle, priority,
preserve-first/last-N, partial-result modes) use ``agentfit-py``.
"""

from .trim import TrimResult, estimate_tokens, trim, trim_messages

__version__ = "0.1.0"
VERSION = __version__

__all__ = [
    "VERSION",
    "TrimResult",
    "estimate_tokens",
    "trim",
    "trim_messages",
]
