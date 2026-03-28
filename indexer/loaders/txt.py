from pathlib import Path

from indexer.loaders.base import BaseLoader, DocumentChunk


class TxtLoader(BaseLoader):
    def load(self, file_path: str) -> list[DocumentChunk]:
        name = Path(file_path).name
        text = Path(file_path).read_text(encoding="utf-8").strip()

        if not text:
            return []

        return [DocumentChunk(text=text, metadata={"source": name})]
