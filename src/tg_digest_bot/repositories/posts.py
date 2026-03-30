from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

import aiosqlite

from tg_digest_bot.models import StoredPost


class PostRepository:
    def __init__(self, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def save_post(self, payload: dict[str, Any]) -> bool:
        query = """
        INSERT OR IGNORE INTO posts (
            source_chat_id,
            source_message_id,
            text,
            content_hash,
            original_link,
            original_chat_title,
            original_chat_username,
            original_message_id,
            original_message_date,
            raw_json,
            received_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = await self.connection.execute(
            query,
            (
                payload["source_chat_id"],
                payload["source_message_id"],
                payload["text"],
                payload["content_hash"],
                payload.get("original_link"),
                payload.get("original_chat_title"),
                payload.get("original_chat_username"),
                payload.get("original_message_id"),
                payload.get("original_message_date"),
                payload["raw_json"],
                payload["received_at"],
            ),
        )
        await self.connection.commit()
        return cursor.rowcount > 0

    async def get_pending_posts(self) -> list[StoredPost]:
        query = """
        SELECT
            id,
            source_chat_id,
            source_message_id,
            text,
            content_hash,
            original_link,
            original_chat_title,
            original_chat_username,
            original_message_id,
            original_message_date,
            raw_json,
            received_at,
            digested_at
        FROM posts
        WHERE digested_at IS NULL
        ORDER BY received_at ASC
        """
        cursor = await self.connection.execute(query)
        rows = await cursor.fetchall()
        return [self._row_to_post(row) for row in rows]

    async def create_digest_record(
        self,
        started_at: datetime,
        finished_at: datetime,
        posts_count: int,
        summary_text: str,
    ) -> int:
        query = """
        INSERT INTO digests (
            started_at,
            finished_at,
            posts_count,
            summary_text
        ) VALUES (?, ?, ?, ?)
        """
        cursor = await self.connection.execute(
            query,
            (
                started_at.isoformat(),
                finished_at.isoformat(),
                posts_count,
                summary_text,
            ),
        )
        await self.connection.commit()
        return int(cursor.lastrowid)

    async def mark_posts_digested(
        self,
        post_ids: list[int],
        digested_at: datetime,
        digest_id: int,
    ) -> None:
        if not post_ids:
            return

        placeholders = ",".join("?" for _ in post_ids)
        query = f"""
        UPDATE posts
        SET digested_at = ?, digest_id = ?
        WHERE id IN ({placeholders})
        """
        await self.connection.execute(
            query,
            (digested_at.isoformat(), digest_id, *post_ids),
        )
        await self.connection.commit()

    def _row_to_post(self, row: aiosqlite.Row) -> StoredPost:
        original_message_date = (
            datetime.fromisoformat(row["original_message_date"])
            if row["original_message_date"]
            else None
        )
        digested_at = (
            datetime.fromisoformat(row["digested_at"])
            if row["digested_at"]
            else None
        )
        return StoredPost(
            id=row["id"],
            source_chat_id=row["source_chat_id"],
            source_message_id=row["source_message_id"],
            text=row["text"],
            content_hash=row["content_hash"],
            original_link=row["original_link"],
            original_chat_title=row["original_chat_title"],
            original_chat_username=row["original_chat_username"],
            original_message_id=row["original_message_id"],
            original_message_date=original_message_date,
            raw_json=row["raw_json"],
            received_at=datetime.fromisoformat(row["received_at"]),
            digested_at=digested_at,
        )
