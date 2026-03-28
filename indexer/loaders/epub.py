from pathlib import Path

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, Tag

from indexer.books import get_profile
from indexer.loaders.base import BaseLoader, DocumentChunk


class EpubLoader(BaseLoader):
    def load(self, file_path: str) -> list[DocumentChunk]:
        filename = Path(file_path).name
        profile = get_profile(filename)

        source = profile.title if profile else filename
        skip_items = profile.skip_items if profile else set()
        min_length = profile.min_text_length if profile else 0
        strip_before = profile.strip_before if profile else None

        chunks: list[DocumentChunk] = []
        book = epub.read_epub(file_path, options={"ignore_ncx": True})
        marker_found = strip_before is None

        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            if item.get_name() in skip_items:
                continue

            html = item.get_content().decode("utf-8", errors="replace")
            soup = BeautifulSoup(html, "html.parser")

            # Only apply strip_before until we find the marker
            current_strip = strip_before if not marker_found else None
            sections = self._split_by_headings(soup, current_strip)
            if sections:
                marker_found = True

            for title, text in sections:
                if not text or len(text) < min_length:
                    continue

                chunks.append(
                    DocumentChunk(
                        text=text,
                        metadata={"source": source, "chapter": title},
                    )
                )

        return chunks

    def _split_by_headings(
        self, soup: BeautifulSoup, strip_before: str | None
    ) -> list[tuple[str, str]]:
        """Split HTML into sections by h1/h2/h3 headings."""
        body = soup.find("body") or soup
        headings = body.find_all(["h1", "h2", "h3"])

        if not headings:
            text = body.get_text(separator="\n").strip()
            title = soup.find(["h1", "h2", "h3", "h4"])
            return [(title.get_text(strip=True) if title else "", text)]

        sections: list[tuple[str, str]] = []
        found_marker = strip_before is None

        for i, heading in enumerate(headings):
            title = heading.get_text(strip=True)

            # Skip everything before strip_before marker
            if not found_marker:
                if strip_before and strip_before in title:
                    found_marker = True
                else:
                    continue

            # Collect text from this heading until the next heading
            parts = [title]
            node = heading.next_sibling
            next_heading = headings[i + 1] if i + 1 < len(headings) else None

            while node:
                if node == next_heading:
                    break
                if isinstance(node, Tag):
                    parts.append(node.get_text(separator="\n"))
                elif isinstance(node, str) and node.strip():
                    parts.append(node.strip())
                node = node.next_sibling

            text = "\n".join(p for p in parts if p.strip()).strip()
            sections.append((title, text))

        return sections
