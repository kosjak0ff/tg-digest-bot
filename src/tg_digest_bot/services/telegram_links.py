from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from aiogram.types import Message


def extract_original_post_context(message: Message) -> dict[str, Any]:
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

    return context


def _as_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
