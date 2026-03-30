from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from tg_digest_bot.services.digest_builder import DigestService


logger = logging.getLogger(__name__)


def create_scheduler(digest_service: DigestService, timezone_name: str) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone_name)
    scheduler.add_job(
        digest_service.run_digest,
        trigger=CronTrigger(hour="8,20", minute="0", timezone=timezone_name),
        id="daily_digest",
        replace_existing=True,
    )
    logger.info("Scheduler configured for 08:00 and 20:00 in timezone=%s", timezone_name)
    return scheduler
