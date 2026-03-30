from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from tg_digest_bot.services.storage import PostStorageService


logger = logging.getLogger(__name__)


def create_forwarded_posts_router(
    source_chat_id: int,
    source_thread_id: int | None,
    storage_service: PostStorageService,
) -> Router:
    router = Router(name="forwarded_posts")

    @router.message(F.chat.id == source_chat_id)
    async def handle_source_message(message: Message) -> None:
        if source_thread_id is not None and message.message_thread_id != source_thread_id:
            return
        if message.text and message.text.startswith("/"):
            return
        if not _is_forwarded_message(message):
            return

        stored = await storage_service.store_message(message)
        if stored:
            logger.info(
                "Accepted source message: chat=%s thread=%s message=%s",
                message.chat.id,
                message.message_thread_id,
                message.message_id,
            )

    return router


def _is_forwarded_message(message: Message) -> bool:
    return any(
        [
            getattr(message, "forward_origin", None) is not None,
            getattr(message, "forward_from_chat", None) is not None,
            getattr(message, "forward_from", None) is not None,
            getattr(message, "forward_sender_name", None) is not None,
            bool(getattr(message, "is_automatic_forward", False)),
        ]
    )
