from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    bot_token: str
    perplexity_api_key: str
    source_chat_id: int
    source_thread_id: int | None
    target_chat_id: int
    target_thread_id: int
    timezone: str
    digest_schedule_times: list[str]
    database_path: Path
    perplexity_model: str
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        return cls(
            bot_token=_required("BOT_TOKEN"),
            perplexity_api_key=_required("PERPLEXITY_API_KEY"),
            source_chat_id=int(_required("SOURCE_CHAT_ID")),
            source_thread_id=_optional_int("SOURCE_THREAD_ID"),
            target_chat_id=int(_required("TARGET_CHAT_ID")),
            target_thread_id=int(_required("TARGET_THREAD_ID")),
            timezone=os.getenv("TIMEZONE", "UTC"),
            digest_schedule_times=_parse_schedule_times(
                os.getenv("DIGEST_SCHEDULE_TIMES", "08:00,20:00")
            ),
            database_path=Path(os.getenv("DATABASE_PATH", "data/tg_digest_bot.sqlite3")),
            perplexity_model=os.getenv("PERPLEXITY_MODEL", "sonar"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required.")
    return value


def _optional_int(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    if not value:
        return None
    return int(value)


def _parse_schedule_times(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise RuntimeError("DIGEST_SCHEDULE_TIMES must contain at least one HH:MM value.")

    parsed: list[str] = []
    for item in items:
        parts = item.split(":")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise RuntimeError(
                f"Invalid schedule value '{item}'. Expected comma-separated HH:MM values."
            )

        hour = int(parts[0])
        minute = int(parts[1])
        if hour not in range(24) or minute not in range(60):
            raise RuntimeError(
                f"Invalid schedule value '{item}'. Hour must be 00-23 and minute 00-59."
            )

        parsed.append(f"{hour:02d}:{minute:02d}")

    return parsed
