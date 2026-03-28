"""Anonymous usage statistics. No personal data is ever stored."""

import json
import logging
from datetime import date, datetime, timezone

import aiosqlite

logger = logging.getLogger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    event TEXT NOT NULL,
    meta TEXT
)
"""


class Stats:
    def __init__(self, db_path: str = "stats.db"):
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None
        # Track unique chats per day (in-memory only, never persisted)
        self._daily_chats: set[int] = set()
        self._current_date: date | None = None

    async def init(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.execute(CREATE_TABLE)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def _emit(self, event: str, meta: dict | None = None) -> None:
        if not self._db:
            return
        ts = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(meta, ensure_ascii=False) if meta else None
        await self._db.execute(
            "INSERT INTO events (ts, event, meta) VALUES (?, ?, ?)",
            (ts, event, meta_json),
        )
        await self._db.commit()

    def _check_day_rollover(self) -> None:
        today = date.today()
        if self._current_date != today:
            self._daily_chats.clear()
            self._current_date = today

    async def on_message(
        self, chat_id: int, question_len: int, response_len: int
    ) -> None:
        self._check_day_rollover()

        # Track new unique chat for today (only the fact, not the ID)
        if chat_id not in self._daily_chats:
            self._daily_chats.add(chat_id)
            await self._emit("new_daily_chat")

        hour = datetime.now(timezone.utc).hour
        await self._emit(
            "message",
            {"hour": hour, "question_len": question_len, "response_len": response_len},
        )

    async def on_command(self, command: str) -> None:
        await self._emit("command", {"name": command})

    async def on_search(self, results_count: int) -> None:
        await self._emit("search", {"results_count": results_count})
