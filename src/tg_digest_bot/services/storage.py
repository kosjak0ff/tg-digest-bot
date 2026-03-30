from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram.types import Message

from tg_digest_bot.repositories.posts import PostRepository
from tg_digest_bot.services.dedup import build_content_hash
from tg_digest_bot.services.telegram_links import extract_original_post_context


logger = logging.getLogger(__name__)


class PostStorageService:
    def __init__(self, repository: PostRepository) -> None:
        self.repository = repository

    async def store_message(self, message: Message) -> bool:
        text = (message.text or message.caption or "").strip()
        if not text:
            logger.info("Skip message without text content: chat=%s message=%s", message.chat.id, message.message_id)
            return False

        original_context = extract_original_post_context(message)
        content_hash = build_content_hash(
            text=text,
            original_link=original_context.get("original_link"),
            original_chat_username=original_context.get("original_chat_username"),
            original_message_id=original_context.get("original_message_id"),
        )

        payload = {
            "source_chat_id": message.chat.id,
            "source_message_id": message.message_id,
            "text": text,
            "content_hash": content_hash,
            "original_link": original_context.get("original_link"),
            "original_chat_title": original_context.get("original_chat_title"),
            "original_chat_username": original_context.get("original_chat_username"),
            "original_message_id": original_context.get("original_message_id"),
            "original_message_date": original_context.get("original_message_date"),
            "raw_json": message.model_dump_json(),
            "received_at": datetime.now(timezone.utc).isoformat(),
        }
        stored = await self.repository.save_post(payload)
        if stored:
            logger.info(
                "Stored post: chat=%s message=%s original_link=%s",
                message.chat.id,
                message.message_id,
                payload["original_link"],
            )
        else:
            logger.info("Duplicate skipped: chat=%s message=%s", message.chat.id, message.message_id)
        return stored
