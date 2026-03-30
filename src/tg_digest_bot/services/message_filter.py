from __future__ import annotations

from typing import Any


def should_store_source_message(message: Any) -> bool:
    text = (getattr(message, "text", None) or getattr(message, "caption", None) or "").strip()
    if not text:
        return False
    if text.startswith("/"):
        return False
    return True
