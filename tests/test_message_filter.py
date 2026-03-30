from __future__ import annotations

import unittest
from types import SimpleNamespace

from tg_digest_bot.services.message_filter import should_store_source_message


class MessageFilterTests(unittest.TestCase):
    def test_accepts_regular_text_message(self) -> None:
        message = SimpleNamespace(text="hello world", caption=None)

        self.assertTrue(should_store_source_message(message))

    def test_accepts_caption_when_text_missing(self) -> None:
        message = SimpleNamespace(text=None, caption="caption text")

        self.assertTrue(should_store_source_message(message))

    def test_rejects_commands(self) -> None:
        message = SimpleNamespace(text="/digest_now", caption=None)

        self.assertFalse(should_store_source_message(message))

    def test_rejects_empty_content(self) -> None:
        message = SimpleNamespace(text="   ", caption=None)

        self.assertFalse(should_store_source_message(message))


if __name__ == "__main__":
    unittest.main()
