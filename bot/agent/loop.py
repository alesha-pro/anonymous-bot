import json
import logging

from openai import AsyncOpenAI

from bot.agent.history import ChatHistory
from bot.agent.prompts import SYSTEM_PROMPT
from bot.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 5


class Agent:
    def __init__(
        self,
        llm: AsyncOpenAI,
        model: str,
        tools: ToolRegistry,
        history: ChatHistory,
    ):
        self._llm = llm
        self._model = model
        self._tools = tools
        self._history = history

    async def respond(self, chat_id: int, user_message: str) -> str:
        self._history.add(chat_id, "user", user_message)

        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self._history.get(chat_id),
        ]

        tool_schemas = self._tools.all_schemas() or None

        for _ in range(MAX_ITERATIONS):
            kwargs: dict = {
                "model": self._model,
                "messages": messages,
            }
            if tool_schemas:
                kwargs["tools"] = tool_schemas

            response = await self._llm.chat.completions.create(**kwargs)
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                messages.append(choice.message.model_dump())

                for tool_call in choice.message.tool_calls:
                    tool = self._tools.get(tool_call.function.name)
                    if tool is None:
                        result = f"Error: unknown tool '{tool_call.function.name}'"
                        logger.warning(result)
                    else:
                        try:
                            tool_kwargs = json.loads(tool_call.function.arguments)
                            result = await tool.execute(**tool_kwargs)
                        except Exception as e:
                            result = f"Error executing tool: {e}"
                            logger.exception("Tool execution failed")

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
                continue

            assistant_text = choice.message.content or ""
            self._history.add(chat_id, "assistant", assistant_text)
            return assistant_text

        fallback = "Извините, произошла ошибка при обработке вашего запроса."
        self._history.add(chat_id, "assistant", fallback)
        return fallback
