from __future__ import annotations

import unittest
from types import SimpleNamespace

from tg_digest_bot.services.thread_matching import get_thread_candidates, matches_thread


class ThreadMatchingTests(unittest.TestCase):
    def test_matches_without_thread_restriction(self) -> None:
        message = SimpleNamespace(message_thread_id=None)

        self.assertTrue(matches_thread(message, None))

    def test_matches_direct_message_thread_id(self) -> None:
        message = SimpleNamespace(message_thread_id=23)

        self.assertTrue(matches_thread(message, 23))

    def test_matches_reply_to_top_message_id(self) -> None:
        message = SimpleNamespace(message_thread_id=None, reply_to_top_message_id=23)

        self.assertTrue(matches_thread(message, 23))

    def test_matches_reply_chain_when_thread_id_missing(self) -> None:
        reply = SimpleNamespace(message_id=23, message_thread_id=None, reply_to_top_message_id=None)
        message = SimpleNamespace(
            message_thread_id=None,
            reply_to_top_message_id=None,
            reply_to_message=reply,
        )

        self.assertTrue(matches_thread(message, 23))

    def test_collects_all_integer_candidates(self) -> None:
        reply = SimpleNamespace(message_id=21, message_thread_id=22, reply_to_top_message_id=23)
        message = SimpleNamespace(
            message_thread_id=20,
            reply_to_top_message_id=24,
            reply_to_message=reply,
        )

        self.assertEqual(get_thread_candidates(message), {20, 21, 22, 23, 24})


if __name__ == "__main__":
    unittest.main()
