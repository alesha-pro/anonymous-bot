"""NA Bot entry point.

Usage:
    python -m bot
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from openai import AsyncOpenAI

from bot.config import Settings
from bot.agent.history import ChatHistory
from bot.agent.loop import Agent
from bot.handlers.commands import setup_handlers
from bot.tools.registry import ToolRegistry
from bot.tools.search import AsyncEmbeddingClient, SearchDocumentsTool
from shared.qdrant import make_qdrant_client


async def main() -> None:
    settings = Settings()

    # LLM client (OpenRouter)
    llm = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )

    # Embedding client (async, for search tool)
    embed_client = AsyncEmbeddingClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.effective_embed_base_url,
        model=settings.openrouter_embed_model,
    )

    # Qdrant
    qdrant = make_qdrant_client(settings.qdrant_host, settings.qdrant_port)

    # Tools
    tools = ToolRegistry()
    tools.register(
        SearchDocumentsTool(qdrant, settings.qdrant_collection, embed_client)
    )

    # Agent
    history = ChatHistory(max_messages=settings.history_max_messages)
    agent = Agent(llm=llm, model=settings.openrouter_model, tools=tools, history=history)

    # Telegram bot
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(),
    )
    dp = Dispatcher()
    dp.include_router(setup_handlers(agent))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info("Starting NA Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
