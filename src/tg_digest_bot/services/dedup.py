from __future__ import annotations

import hashlib


def build_content_hash(
    text: str,
    original_link: str | None,
    original_chat_username: str | None,
    original_message_id: int | None,
) -> str:
    normalized = "\n".join(
        [
            text.strip(),
            original_link or "",
            original_chat_username or "",
            str(original_message_id or ""),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
