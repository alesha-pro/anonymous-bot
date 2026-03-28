import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.agent.loop import Agent
from bot.formatting import md_to_telegram_html

logger = logging.getLogger(__name__)
router = Router(name="commands")


def setup_handlers(agent: Agent) -> Router:
    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        await message.answer(
            "Привет! Я помощник по литературе Анонимных Наркоманов.\n\n"
            "Задавай мне вопросы о программе АН — шагах, традициях, "
            "чтениях или общих вопросах выздоровления.\n\n"
            "Команды:\n"
            "/new — начать новый разговор\n"
            "/clear — очистить историю чата"
        )

    @router.message(Command("new", "clear"))
    async def cmd_clear(message: Message) -> None:
        agent._history.clear(message.chat.id)
        await message.answer("История чата очищена. Начинаем с чистого листа!")

    @router.message()
    async def handle_message(message: Message) -> None:
        if not message.text:
            return

        logger.info(
            "Message from chat_id=%s: %s",
            message.chat.id,
            message.text[:100],
        )

        reply = await agent.respond(message.chat.id, message.text)
        html = md_to_telegram_html(reply)

        # Telegram has a 4096 char limit per message
        for i in range(0, len(html), 4096):
            await message.answer(html[i : i + 4096], parse_mode="HTML")

    return router
