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
    target_chat_id: int
    target_thread_id: int
    timezone: str
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
            target_chat_id=int(_required("TARGET_CHAT_ID")),
            target_thread_id=int(_required("TARGET_THREAD_ID")),
            timezone=os.getenv("TIMEZONE", "UTC"),
            database_path=Path(os.getenv("DATABASE_PATH", "data/tg_digest_bot.sqlite3")),
            perplexity_model=os.getenv("PERPLEXITY_MODEL", "sonar"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required.")
    return value
