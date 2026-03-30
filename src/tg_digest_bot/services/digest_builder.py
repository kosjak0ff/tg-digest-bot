from __future__ import annotations

import asyncio
import html
import logging
from datetime import datetime, timezone

from aiogram import Bot

from tg_digest_bot.models import DigestSummary, StoredPost
from tg_digest_bot.repositories.posts import PostRepository
from tg_digest_bot.services.perplexity import PerplexityClient


logger = logging.getLogger(__name__)


class DigestService:
    def __init__(
        self,
        repository: PostRepository,
        perplexity_client: PerplexityClient,
        bot: Bot,
        target_chat_id: int,
        target_thread_id: int,
    ) -> None:
        self.repository = repository
        self.perplexity_client = perplexity_client
        self.bot = bot
        self.target_chat_id = target_chat_id
        self.target_thread_id = target_thread_id
        self._lock = asyncio.Lock()

    async def run_digest(self) -> str:
        if self._lock.locked():
            logger.info("Digest skipped: another run is already in progress.")
            return "busy"

        async with self._lock:
            posts = await self.repository.get_pending_posts()
            if not posts:
                logger.info("Digest skipped: no new posts.")
                return "empty"

            started_at = datetime.now(timezone.utc)
            summary = await self.perplexity_client.summarize_posts(posts)
            message_text = self._format_digest_message(posts, summary, started_at)
            digest_id = await self.repository.create_digest_record(
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                posts_count=len(posts),
                summary_text=summary.raw_text,
            )

            for chunk in split_for_telegram(message_text):
                await self.bot.send_message(
                    chat_id=self.target_chat_id,
                    message_thread_id=self.target_thread_id,
                    text=chunk,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )

            await self.repository.mark_posts_digested(
                post_ids=[post.id for post in posts],
                digested_at=datetime.now(timezone.utc),
                digest_id=digest_id,
            )
            logger.info("Digest sent successfully: digest_id=%s posts=%s", digest_id, len(posts))
            return "sent"

    def _format_digest_message(
        self,
        posts: list[StoredPost],
        summary: DigestSummary,
        created_at: datetime,
    ) -> str:
        post_map = {post.id: post for post in posts}
        lines = [
            "<b>Дайджест Telegram-постов</b>",
            f"Период выгрузки: {html.escape(created_at.strftime('%Y-%m-%d %H:%M UTC'))}",
            f"Новых постов: {len(posts)}",
        ]

        if summary.overview:
            lines.append("")
            lines.append(f"<b>Кратко:</b> {html.escape(summary.overview)}")

        if summary.topics:
            for topic in summary.topics:
                lines.append("")
                lines.append(f"<b>{html.escape(topic.title)}</b>")
                if topic.summary:
                    lines.append(html.escape(topic.summary))

                links = []
                for post_id in topic.post_ids:
                    post = post_map.get(post_id)
                    if not post:
                        continue
                    if post.original_link:
                        label = post.original_chat_title or post.original_chat_username or f"Пост {post_id}"
                        links.append(
                            f'• <a href="{html.escape(post.original_link, quote=True)}">{html.escape(label)}</a>'
                        )
                    else:
                        links.append(f"• Пост {post_id}: ссылка недоступна")

                if links:
                    lines.append("<b>Источники:</b>")
                    lines.extend(links)
        else:
            lines.append("")
            lines.append(html.escape(summary.raw_text))
            lines.append("")
            lines.append("<b>Источники:</b>")
            for post in posts:
                if post.original_link:
                    label = post.original_chat_title or post.original_chat_username or f"Пост {post.id}"
                    lines.append(
                        f'• <a href="{html.escape(post.original_link, quote=True)}">{html.escape(label)}</a>'
                    )
                else:
                    lines.append(f"• Пост {post.id}: ссылка недоступна")

        return "\n".join(lines)


def split_for_telegram(text: str, chunk_size: int = 3800) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    current = []
    current_length = 0

    for line in text.splitlines(keepends=True):
        if current_length + len(line) > chunk_size and current:
            chunks.append("".join(current).rstrip())
            current = [line]
            current_length = len(line)
        else:
            current.append(line)
            current_length += len(line)

    if current:
        chunks.append("".join(current).rstrip())

    return chunks
