from __future__ import annotations

import unittest
from types import SimpleNamespace

from tg_digest_bot.services.telegram_links import (
    extract_original_link_from_text,
    extract_original_post_context,
)


class TelegramLinksTests(unittest.TestCase):
    def test_extracts_original_link_from_text_line(self) -> None:
        text = "Some text\nOriginal: https://t.me/NewBitFuture/2108\nMore text"

        self.assertEqual(
            extract_original_link_from_text(text),
            "https://t.me/NewBitFuture/2108",
        )

    def test_populates_context_from_explicit_original_link(self) -> None:
        message = SimpleNamespace(
            text="Original: https://t.me/NewBitFuture/2108",
            caption=None,
            forward_origin=None,
            forward_from_chat=None,
            forward_from_message_id=None,
            forward_date=None,
        )

        context = extract_original_post_context(message)

        self.assertEqual(context["original_link"], "https://t.me/NewBitFuture/2108")
        self.assertEqual(context["original_chat_username"], "NewBitFuture")
        self.assertEqual(context["original_message_id"], 2108)


if __name__ == "__main__":
    unittest.main()
