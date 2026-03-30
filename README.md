# Telegram Digest Bot

## Русский

Простой Telegram-бот для личного использования.

Что делает:

- принимает пересланные посты из `SOURCE_CHAT_ID`
- при необходимости ограничивает приём одним `SOURCE_THREAD_ID`
- сохраняет посты в SQLite
- по расписанию собирает дайджест через Perplexity API
- отправляет результат в `TARGET_CHAT_ID` и `TARGET_THREAD_ID`
- поддерживает ручной запуск командой `/digest_now`

Основные настройки в `.env`:

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

Важно:

- `SOURCE_THREAD_ID` можно оставить пустым, тогда бот принимает сообщения из всего исходного чата
- `DIGEST_SCHEDULE_TIMES` это список UTC-времён через запятую, например `09:30` или `08:00,20:00`

Локальный запуск:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src python -m tg_digest_bot
```

Запуск на Ubuntu VPS:

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv
sudo useradd --create-home --home-dir /home/tg-digest-bot --shell /usr/sbin/nologin tg-digest-bot
sudo mkdir -p /home/tg-digest-bot/tg-digest-bot
sudo chown -R tg-digest-bot:tg-digest-bot /home/tg-digest-bot
```

Если клонируете с GitHub:

```bash
sudo -u tg-digest-bot -H bash -lc '
cd /home/tg-digest-bot
git clone git@github.com:kosjak0ff/tg-digest-bot.git tg-digest-bot
cd tg-digest-bot
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
mkdir -p data
'
```

Потом:

```bash
sudo -u tg-digest-bot -H editor /home/tg-digest-bot/tg-digest-bot/.env
sudo cp systemd/tg-digest-bot.service /etc/systemd/system/tg-digest-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now tg-digest-bot.service
journalctl -u tg-digest-bot.service -f
```

Пути на сервере:

- проект: `/home/tg-digest-bot/tg-digest-bot`
- venv: `/home/tg-digest-bot/tg-digest-bot/.venv`
- `.env`: `/home/tg-digest-bot/tg-digest-bot/.env`
- база: `/home/tg-digest-bot/tg-digest-bot/data/tg_digest_bot.sqlite3`

## English

Minimal personal Telegram bot that stores forwarded posts in SQLite, builds summaries with Perplexity API, and sends digest messages into a configured Telegram topic/thread on a UTC schedule.

Quick start:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src python -m tg_digest_bot
```

Server paths:

- project: `/home/tg-digest-bot/tg-digest-bot`
- service file: [`systemd/tg-digest-bot.service`](/home/code/codex-projects/tg-digest-bot/systemd/tg-digest-bot.service)
- env example: [`.env.example`](/home/code/codex-projects/tg-digest-bot/.env.example)
