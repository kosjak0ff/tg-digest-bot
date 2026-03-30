from __future__ import annotations

import asyncio
import logging

from tg_digest_bot.bot import create_bot, create_dispatcher
from tg_digest_bot.config import Settings
from tg_digest_bot.db import init_db
from tg_digest_bot.logging_setup import configure_logging
from tg_digest_bot.repositories.posts import PostRepository
from tg_digest_bot.services.digest_builder import DigestService
from tg_digest_bot.services.perplexity import PerplexityClient
from tg_digest_bot.services.scheduler import create_scheduler
from tg_digest_bot.services.storage import PostStorageService


logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)

    connection = await init_db(settings.database_path)
    repository = PostRepository(connection)
    storage_service = PostStorageService(repository)
    perplexity_client = PerplexityClient(
        api_key=settings.perplexity_api_key,
        model=settings.perplexity_model,
    )
    bot = create_bot(settings.bot_token)
    digest_service = DigestService(
        repository=repository,
        perplexity_client=perplexity_client,
        bot=bot,
        target_chat_id=settings.target_chat_id,
        target_thread_id=settings.target_thread_id,
    )
    dispatcher = create_dispatcher(
        source_chat_id=settings.source_chat_id,
        source_thread_id=settings.source_thread_id,
        storage_service=storage_service,
        digest_service=digest_service,
    )
    scheduler = create_scheduler(
        digest_service=digest_service,
        timezone_name=settings.timezone,
        schedule_times=settings.digest_schedule_times,
    )
    scheduler.start()

    logger.info(
        (
            "Bot started: source_chat_id=%s source_thread_id=%s "
            "target_chat_id=%s target_thread_id=%s timezone=%s schedule_times=%s"
        ),
        settings.source_chat_id,
        settings.source_thread_id,
        settings.target_chat_id,
        settings.target_thread_id,
        settings.timezone,
        ", ".join(settings.digest_schedule_times),
    )

    try:
        await dispatcher.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
