from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from tg_digest_bot.services.storage import PostStorageService


logger = logging.getLogger(__name__)


def create_forwarded_posts_router(
    source_chat_id: int,
    storage_service: PostStorageService,
) -> Router:
    router = Router(name="forwarded_posts")

    @router.message(F.chat.id == source_chat_id)
    async def handle_source_message(message: Message) -> None:
        stored = await storage_service.store_message(message)
        if stored:
            logger.info("Accepted source message: chat=%s message=%s", message.chat.id, message.message_id)

    return router
