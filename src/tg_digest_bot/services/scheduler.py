from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from tg_digest_bot.services.digest_builder import DigestService


logger = logging.getLogger(__name__)


def create_scheduler(
    digest_service: DigestService,
    timezone_name: str,
    schedule_times: list[str],
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone_name)
    for schedule_time in schedule_times:
        hour_text, minute_text = schedule_time.split(":")
        scheduler.add_job(
            digest_service.run_digest,
            trigger=CronTrigger(
                hour=hour_text,
                minute=minute_text,
                timezone=timezone_name,
            ),
            id=f"digest_{hour_text}{minute_text}",
            replace_existing=True,
        )

    logger.info(
        "Scheduler configured for times=%s in timezone=%s",
        ", ".join(schedule_times),
        timezone_name,
    )
    return scheduler
