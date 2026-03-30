from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from tg_digest_bot.models import DigestSummary, DigestTopic, StoredPost


logger = logging.getLogger(__name__)


class PerplexityClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai"
        self.timeout = httpx.Timeout(90.0, connect=10.0)

    async def summarize_posts(self, posts: list[StoredPost]) -> DigestSummary:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You summarize only the provided Telegram posts. "
                        "Return valid JSON only. "
                        "Language: Russian. "
                        "Do not add facts not present in the input. "
                        "Schema: "
                        '{"overview":"string","topics":[{"title":"string","summary":"string","post_ids":[1,2]}]}'
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(posts),
                },
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        ) as client:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = self._parse_response(content)
        return parsed

    def _build_prompt(self, posts: list[StoredPost]) -> str:
        lines = [
            "Create a short digest grouped by topics.",
            "Each topic must reference input post ids.",
            "Input posts:",
        ]
        for post in posts:
            lines.append(
                "\n".join(
                    [
                        f"POST_ID: {post.id}",
                        f"RECEIVED_AT_UTC: {post.received_at.isoformat()}",
                        f"ORIGINAL_LINK: {post.original_link or 'null'}",
                        f"TEXT: {post.text}",
                    ]
                )
            )
        return "\n\n".join(lines)

    def _parse_response(self, content: str) -> DigestSummary:
        raw_text = content.strip()
        json_text = raw_text
        if "```" in raw_text:
            chunks = raw_text.split("```")
            for chunk in chunks:
                stripped = chunk.strip()
                if stripped.startswith("{") or stripped.startswith("json"):
                    json_text = stripped.removeprefix("json").strip()
                    break

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            logger.warning("Perplexity returned non-JSON response, fallback to plain summary.")
            return DigestSummary(overview=raw_text, topics=[], raw_text=raw_text)

        topics = []
        for item in data.get("topics", []):
            post_ids = [int(value) for value in item.get("post_ids", []) if isinstance(value, int) or str(value).isdigit()]
            topics.append(
                DigestTopic(
                    title=str(item.get("title", "Без темы")).strip() or "Без темы",
                    summary=str(item.get("summary", "")).strip(),
                    post_ids=post_ids,
                )
            )

        overview = str(data.get("overview", "")).strip()
        return DigestSummary(overview=overview, topics=topics, raw_text=raw_text)
