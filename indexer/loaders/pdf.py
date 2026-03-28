from pathlib import Path

import pymupdf

from indexer.books import get_profile
from indexer.loaders.base import BaseLoader, DocumentChunk


class PdfLoader(BaseLoader):
    def load(self, file_path: str) -> list[DocumentChunk]:
        filename = Path(file_path).name
        profile = get_profile(filename)

        source = profile.title if profile else filename
        skip_pages = profile.skip_pages if profile else set()
        min_length = profile.min_text_length if profile else 0

        chunks: list[DocumentChunk] = []

        doc = pymupdf.open(file_path)
        for page_num, page in enumerate(doc, start=1):
            if page_num in skip_pages:
                continue

            text = page.get_text().strip()

            if not text or len(text) < min_length:
                continue

            chunks.append(
                DocumentChunk(
                    text=text,
                    metadata={"source": source, "page": page_num},
                )
            )
        doc.close()
        return chunks
