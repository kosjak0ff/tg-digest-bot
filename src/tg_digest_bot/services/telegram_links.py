from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiogram.types import Message

PUBLIC_TME_LINK_RE = re.compile(r"https://t\.me/([A-Za-z0-9_]+)/(\d+)")


def extract_original_post_context(message: "Message") -> dict[str, Any]:
    context: dict[str, Any] = {
        "original_link": None,
        "original_chat_title": None,
        "original_chat_username": None,
        "original_message_id": None,
        "original_message_date": None,
    }

    forward_origin = getattr(message, "forward_origin", None)
    if forward_origin is not None:
        origin_type = getattr(forward_origin, "type", None)

        if origin_type == "channel":
            chat = getattr(forward_origin, "chat", None)
            message_id = getattr(forward_origin, "message_id", None)
            date = getattr(forward_origin, "date", None)
            username = getattr(chat, "username", None)
            title = getattr(chat, "title", None)

            context["original_chat_title"] = title
            context["original_chat_username"] = username
            context["original_message_id"] = message_id
            context["original_message_date"] = _as_iso(date)

            if username and message_id:
                context["original_link"] = f"https://t.me/{username}/{message_id}"

            return context

    forward_from_chat = getattr(message, "forward_from_chat", None)
    forward_from_message_id = getattr(message, "forward_from_message_id", None)
    forward_date = getattr(message, "forward_date", None)

    if forward_from_chat is not None:
        username = getattr(forward_from_chat, "username", None)
        title = getattr(forward_from_chat, "title", None)
        context["original_chat_title"] = title
        context["original_chat_username"] = username
        context["original_message_id"] = forward_from_message_id
        context["original_message_date"] = _as_iso(forward_date)

        if username and forward_from_message_id:
            context["original_link"] = f"https://t.me/{username}/{forward_from_message_id}"

    if context["original_link"] is None:
        explicit_link = extract_original_link_from_text(message.text or message.caption or "")
        if explicit_link is not None:
            context["original_link"] = explicit_link
            parsed = parse_public_tme_link(explicit_link)
            if parsed is not None:
                username, message_id = parsed
                context["original_chat_username"] = username
                context["original_message_id"] = message_id

    return context


def extract_original_link_from_text(text: str) -> str | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not line.lower().startswith("original:"):
            continue
        candidate = line.split(":", 1)[1].strip()
        parsed = parse_public_tme_link(candidate)
        if parsed is None:
            continue
        username, message_id = parsed
        return f"https://t.me/{username}/{message_id}"
    return None


def parse_public_tme_link(value: str) -> tuple[str, int] | None:
    match = PUBLIC_TME_LINK_RE.search(value.strip())
    if match is None:
        return None
    return match.group(1), int(match.group(2))


def _as_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
