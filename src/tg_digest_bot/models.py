from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class StoredPost:
    id: int
    source_chat_id: int
    source_message_id: int
    text: str
    content_hash: str
    original_link: str | None
    original_chat_title: str | None
    original_chat_username: str | None
    original_message_id: int | None
    original_message_date: datetime | None
    raw_json: str
    received_at: datetime
    digested_at: datetime | None


@dataclass(slots=True)
class DigestTopic:
    title: str
    summary: str
    post_ids: list[int]


@dataclass(slots=True)
class DigestSummary:
    overview: str
    topics: list[DigestTopic]
    raw_text: str
