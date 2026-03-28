from typing import Any

from openai import AsyncOpenAI
from qdrant_client import QdrantClient

from bot.tools.base import BaseTool


class AsyncEmbeddingClient:
    """Async embedding client for the bot runtime."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def aembed_single(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            input=[text],
            model=self._model,
        )
        return response.data[0].embedding


class SearchDocumentsTool(BaseTool):
    """RAG search over NA literature in Qdrant."""

    @property
    def name(self) -> str:
        return "search_documents"

    @property
    def description(self) -> str:
        return (
            "Поиск по библиотеке литературы АН. Используй этот инструмент, "
            "когда пользователь спрашивает о шагах, традициях, чтениях АН "
            "или о чём-то, что может быть в книгах АН. "
            "Возвращает релевантные отрывки с указанием источников."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос",
                },
            },
            "required": ["query"],
        }

    def __init__(
        self,
        qdrant: QdrantClient,
        collection: str,
        embed_client: AsyncEmbeddingClient,
    ):
        self._qdrant = qdrant
        self._collection = collection
        self._embed = embed_client

    async def execute(self, **kwargs: Any) -> str:
        query: str = kwargs["query"]

        vector = await self._embed.aembed_single(query)

        results = self._qdrant.query_points(
            collection_name=self._collection,
            query=vector,
            limit=5,
            with_payload=True,
        )

        if not results.points:
            return "Релевантных документов не найдено."

        formatted = []
        for point in results.points:
            payload = point.payload or {}
            source = payload.get("source", "Неизвестно")
            page = payload.get("page", "")
            chapter = payload.get("chapter", "")
            text = payload.get("text", "")

            citation = f"[{source}"
            if page:
                citation += f", стр. {page}"
            if chapter:
                citation += f", {chapter}"
            citation += "]"

            formatted.append(f"{text}\n— {citation}")

        return "\n\n---\n\n".join(formatted)
