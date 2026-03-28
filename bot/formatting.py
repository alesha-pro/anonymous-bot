"""Convert Markdown from LLM output to Telegram-compatible HTML."""

import re
from html import escape


def md_to_telegram_html(text: str) -> str:
    # Escape HTML entities first (before adding our own tags)
    text = escape(text)

    # Code blocks (before other transformations)
    text = re.sub(r"```\w*\n?(.*?)```", r"<pre>\1</pre>", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Headers → bold
    text = re.sub(r"^#{1,6}\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)

    # Bold (must come before italic)
    text = re.sub(r"\*\*([^\s](?:.*?[^\s])?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__([^\s](?:.*?[^\s])?)__", r"<b>\1</b>", text)

    # Italic — require non-whitespace next to markers
    text = re.sub(r"\*([^\s*](?:.*?[^\s])?)\*", r"<i>\1</i>", text)
    text = re.sub(r"(?<!\w)_([^\s_](?:.*?[^\s])?)_(?!\w)", r"<i>\1</i>", text)

    # Strikethrough
    text = re.sub(r"~~([^\s](?:.*?[^\s])?)~~", r"<s>\1</s>", text)

    return text
