"""Per-book processing profiles.

Each profile maps a filename to processing rules:
- title: human-readable book name (used as `source` in metadata)
- skip_pages: (PDF) set of page numbers to exclude
- skip_items: (EPUB) set of item names to exclude
- min_text_length: minimum text length to keep a segment
- strip_before: text marker — everything before this line is stripped
"""

import unicodedata
from dataclasses import dataclass, field


@dataclass
class BookProfile:
    title: str
    skip_pages: set[int] = field(default_factory=set)
    skip_items: set[str] = field(default_factory=set)
    min_text_length: int = 50
    strip_before: str | None = None


PROFILES: dict[str, BookProfile] = {
    "Базовый Текст.pdf": BookProfile(
        title="Анонимные Наркоманы",
        skip_pages={
            *range(1, 10),      # титульные листы, копирайт, содержание
            *range(262, 267),   # алфавитный указатель
        },
        min_text_length=50,
    ),
    "Это работает-Как и почему.epub": BookProfile(
        title="ЭРКИП",
        skip_items={"cover.xhtml", "content2.html"},  # обложка, реклама ЛитРес
        strip_before="Вступление",  # отрезать копирайт в начале content0
        min_text_length=50,
    ),
    "ЭТО РАБОТАЕТ_ КАК И ПОЧЕМУ (2).pdf": BookProfile(
        title="ЭРКИП",
        skip_pages={1},  # титульная страница
        min_text_length=50,
    ),
}


def get_profile(filename: str) -> BookProfile | None:
    normalized = unicodedata.normalize("NFC", filename)
    return PROFILES.get(normalized)
