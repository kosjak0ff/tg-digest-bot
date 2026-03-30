from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from tg_digest_bot.services.thread_matching import matches_thread
from tg_digest_bot.services.digest_builder import DigestService


logger = logging.getLogger(__name__)


def create_commands_router(
    source_chat_id: int,
    source_thread_id: int | None,
    digest_service: DigestService,
) -> Router:
    router = Router(name="commands")

    @router.message(Command("digest_now"), F.chat.id == source_chat_id)
    async def handle_digest_now(message: Message) -> None:
        if not matches_thread(message, source_thread_id):
            logger.info(
                "Manual digest command ignored: chat=%s thread=%s expected_thread=%s",
                message.chat.id,
                message.message_thread_id,
                source_thread_id,
            )
            return

        status = await digest_service.run_digest()
        if status == "busy":
            await message.reply("Дайджест уже собирается. Подождите немного.")
        elif status == "empty":
            await message.reply("Новых постов для дайджеста пока нет.")
        else:
            await message.reply("Дайджест собран и отправлен в целевой topic.")
        logger.info(
            "Manual digest command handled: chat=%s thread=%s status=%s",
            message.chat.id,
            message.message_thread_id,
            status,
        )

    return router
