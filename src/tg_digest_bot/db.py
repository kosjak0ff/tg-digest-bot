from __future__ import annotations

from pathlib import Path

import aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_chat_id INTEGER NOT NULL,
    source_message_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    content_hash TEXT NOT NULL UNIQUE,
    original_link TEXT,
    original_chat_title TEXT,
    original_chat_username TEXT,
    original_message_id INTEGER,
    original_message_date TEXT,
    raw_json TEXT NOT NULL,
    received_at TEXT NOT NULL,
    digested_at TEXT,
    digest_id INTEGER,
    UNIQUE(source_chat_id, source_message_id)
);

CREATE TABLE IF NOT EXISTS digests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    posts_count INTEGER NOT NULL,
    summary_text TEXT NOT NULL
);
"""


async def init_db(database_path: Path) -> aiosqlite.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = await aiosqlite.connect(database_path)
    connection.row_factory = aiosqlite.Row
    await connection.executescript(SCHEMA)
    await connection.commit()
    return connection
