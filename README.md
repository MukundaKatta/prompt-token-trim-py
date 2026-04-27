# prompt-token-trim-py

[![PyPI](https://img.shields.io/pypi/v/prompt-token-trim-py.svg)](https://pypi.org/project/prompt-token-trim-py/)
[![Python](https://img.shields.io/pypi/pyversions/prompt-token-trim-py.svg)](https://pypi.org/project/prompt-token-trim-py/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Trim prompt messages to fit a token budget while preserving priority.** Sort messages by `priority` (descending), accept each if it fits, then re-emit them in original order. Zero runtime dependencies.

Python port of [@mukundakatta/prompt-token-trim](https://www.npmjs.com/package/@mukundakatta/prompt-token-trim).

> Note: see also [agentfit-py](https://github.com/MukundaKatta/agentfit-py). They look similar; this one is **message-level priority trimming** (drop a single message if it doesn't fit). agentfit-py is **whole-history strategy fitting** (drop-oldest, drop-middle, priority, with system-message preservation and partial-result modes).

## Install

```bash
pip install prompt-token-trim-py
```

## Quick start

```python
from prompt_token_trim import trim

messages = [
    {"role": "system", "content": "You are a helpful assistant.", "priority": 10},
    {"role": "user",   "content": "Tell me about Pluto.",          "priority": 5},
    {"role": "assistant", "content": "Pluto is a dwarf planet.",   "priority": 5},
    {"role": "user",   "content": "And Mars?",                     "priority": 1},
]

result = trim(messages, budget=20, preserve_system=True)

result.messages  # list[dict] in original order, kept under budget
result.tokens    # int -- tokens consumed
result.dropped   # int -- count of messages dropped
```

## API

### `trim(messages, budget, *, preserve_system=True) -> TrimResult`

* `messages`: list of dicts with `role`, `content`, optional `priority` (defaults to `0`).
* `budget`: token budget (`ceil(len(content) / 4)` heuristic per message).
* `preserve_system`: keep all `role == "system"` messages even if they don't fit (they consume budget anyway). Defaults to `True`.

`TrimResult` is a dataclass with:

* `messages`: kept messages, in their original order.
* `tokens`: total tokens consumed.
* `dropped`: count of messages that did not survive.

The JS sibling exposes `trimMessages({maxTokens})` -- the `trim_messages(messages, *, max_tokens=...)` alias is provided for parity.

## License

MIT
