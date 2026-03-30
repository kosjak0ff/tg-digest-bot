from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from tg_digest_bot.handlers.forwarded_posts import create_forwarded_posts_router
from tg_digest_bot.services.storage import PostStorageService


def create_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))


def create_dispatcher(
    source_chat_id: int,
    storage_service: PostStorageService,
) -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(
        create_forwarded_posts_router(
            source_chat_id=source_chat_id,
            storage_service=storage_service,
        )
    )
    return dispatcher
