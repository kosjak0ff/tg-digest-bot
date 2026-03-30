from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from tg_digest_bot.services.message_filter import should_store_source_message
from tg_digest_bot.services.storage import PostStorageService
from tg_digest_bot.services.thread_matching import get_thread_candidates, matches_thread


logger = logging.getLogger(__name__)


def create_forwarded_posts_router(
    source_chat_id: int,
    source_thread_id: int | None,
    storage_service: PostStorageService,
) -> Router:
    router = Router(name="forwarded_posts")

    @router.message(F.chat.id == source_chat_id)
    async def handle_source_message(message: Message) -> None:
        if not matches_thread(message, source_thread_id):
            logger.info(
                "Ignored source message outside configured thread: chat=%s message=%s thread=%s candidates=%s expected_thread=%s",
                message.chat.id,
                message.message_id,
                message.message_thread_id,
                sorted(get_thread_candidates(message)),
                source_thread_id,
            )
            return
        if not should_store_source_message(message):
            logger.info(
                "Ignored source message without storable content: chat=%s thread=%s message=%s",
                message.chat.id,
                message.message_thread_id,
                message.message_id,
            )
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
