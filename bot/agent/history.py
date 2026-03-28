from collections import defaultdict


class ChatHistory:
    """In-memory sliding window message history. No persistence — privacy first."""

    def __init__(self, max_messages: int = 20):
        self._max = max_messages
        self._store: dict[int, list[dict]] = defaultdict(list)

    def add(self, chat_id: int, role: str, content: str) -> None:
        self._store[chat_id].append({"role": role, "content": content})
        if len(self._store[chat_id]) > self._max:
            self._store[chat_id] = self._store[chat_id][-self._max :]

    def get(self, chat_id: int) -> list[dict]:
        return list(self._store[chat_id])

    def clear(self, chat_id: int) -> None:
        self._store[chat_id] = []
