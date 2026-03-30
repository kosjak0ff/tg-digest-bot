# Telegram Digest Bot

Minimal MVP Telegram bot for personal use. The bot receives forwarded posts in a dedicated source chat or source topic, stores them in SQLite, and sends digest summaries to a specific Telegram group topic on a configurable UTC schedule.

## Features

- Receives messages only from one configured source chat and optional source topic/thread.
- Stores post text, timestamps, Telegram metadata, and original post links when available.
- Skips duplicate messages.
- Builds digest summaries with Perplexity API.
- Sends digest messages to a specific Telegram topic/thread.
- Supports manual digest trigger with `/digest_now`.
- Runs as a plain Python service on Ubuntu VPS.

## Stack

- Python 3.12
- aiogram
- SQLite
- APScheduler
- Perplexity API
- systemd
- python-dotenv

## Project layout

```text
.
├── .env.example
├── README.md
├── requirements.txt
├── systemd/
│   └── tg-digest-bot.service
├── data/
│   └── .gitkeep
└── src/
    └── tg_digest_bot/
        ├── __init__.py
        ├── __main__.py
        ├── bot.py
        ├── config.py
        ├── db.py
        ├── logging_setup.py
        ├── models.py
        ├── handlers/
        │   ├── __init__.py
        │   ├── commands.py
        │   └── forwarded_posts.py
        ├── repositories/
        │   ├── __init__.py
        │   └── posts.py
        └── services/
            ├── __init__.py
            ├── dedup.py
            ├── digest_builder.py
            ├── perplexity.py
            ├── scheduler.py
            ├── storage.py
            └── telegram_links.py
```

## How MVP works

1. You manually forward posts from other Telegram channels into `SOURCE_CHAT_ID`.
2. If `SOURCE_THREAD_ID` is set, the bot listens only inside that specific source topic/thread.
3. Incoming messages are normalized and stored in SQLite.
4. On times configured in `DIGEST_SCHEDULE_TIMES` the scheduler gathers all not-yet-digested posts.
5. The bot sends them to Perplexity and asks for a short Russian digest grouped by topics.
6. The resulting digest is posted into `TARGET_CHAT_ID` and `TARGET_THREAD_ID`.
7. You can manually trigger digest generation with `/digest_now` inside the source chat/topic.

## Environment variables

Copy `.env.example` to `.env` and set your values:

```env
BOT_TOKEN=...
PERPLEXITY_API_KEY=...
SOURCE_CHAT_ID=-100...
SOURCE_THREAD_ID=
TARGET_CHAT_ID=-100...
TARGET_THREAD_ID=1
TIMEZONE=UTC
DIGEST_SCHEDULE_TIMES=08:00,20:00
DATABASE_PATH=data/tg_digest_bot.sqlite3
PERPLEXITY_MODEL=sonar
LOG_LEVEL=INFO
```

`SOURCE_THREAD_ID` is optional:

- leave it empty to accept messages from the whole source chat
- set it to a topic/thread id to accept messages only from that topic

`DIGEST_SCHEDULE_TIMES` is a simple comma-separated list of UTC times:

- `08:00,20:00` for morning and evening digests
- `09:30` for one digest per day
- `06:00,12:00,18:00` for three digests per day

## Local run

Create a virtual environment and install dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Run the bot:

```bash
PYTHONPATH=src python -m tg_digest_bot
```

## Ubuntu VPS deployment

### 1. System packages

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv
```

### 2. Prepare app directory

```bash
cd /opt
sudo mkdir -p tg-digest-bot
sudo chown "$USER":"$USER" tg-digest-bot
cd tg-digest-bot
```

Copy project files into the directory, then:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
mkdir -p data
```

### 3. Configure environment

Edit `.env` and set real values:

- `BOT_TOKEN`
- `PERPLEXITY_API_KEY`
- `SOURCE_CHAT_ID`
- `SOURCE_THREAD_ID` if you want to limit the source to one topic
- `TARGET_CHAT_ID`
- `TARGET_THREAD_ID`
- `TIMEZONE=UTC`
- `DIGEST_SCHEDULE_TIMES=08:00,20:00`

### 4. Install systemd unit

Edit paths in [`systemd/tg-digest-bot.service`](/home/code/codex-projects/tg-digest-bot/systemd/tg-digest-bot.service), then copy it:

```bash
sudo cp systemd/tg-digest-bot.service /etc/systemd/system/tg-digest-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now tg-digest-bot.service
```

### 5. Check logs

```bash
sudo systemctl status tg-digest-bot.service
journalctl -u tg-digest-bot.service -f
```

## Notes and limitations

- Original post links are saved only when Telegram metadata exposes enough information to build them.
- The digest is based only on posts that were not yet included in a previous digest.
- The scheduler uses `TIMEZONE=UTC` by default.
- This MVP is single-user and single-source-chat by design.

## Useful checks

Run a quick import check:

```bash
PYTHONPATH=src python -m compileall src
```
