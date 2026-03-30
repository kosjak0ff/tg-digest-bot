from __future__ import annotations

from typing import Any


def matches_thread(message: Any, thread_id: int | None) -> bool:
    if thread_id is None:
        return True
    return thread_id in get_thread_candidates(message)


def get_thread_candidates(message: Any) -> set[int]:
    candidates: set[int] = set()
    _add_candidate(candidates, getattr(message, "message_thread_id", None))
    _add_candidate(candidates, getattr(message, "reply_to_top_message_id", None))

    reply_to_message = getattr(message, "reply_to_message", None)
    if reply_to_message is not None:
        _add_candidate(candidates, getattr(reply_to_message, "message_thread_id", None))
        _add_candidate(candidates, getattr(reply_to_message, "reply_to_top_message_id", None))
        _add_candidate(candidates, getattr(reply_to_message, "message_id", None))

    return candidates


def _add_candidate(candidates: set[int], value: Any) -> None:
    if isinstance(value, int):
        candidates.add(value)
