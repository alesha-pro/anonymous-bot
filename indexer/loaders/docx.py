from pathlib import Path

from docx import Document

from indexer.loaders.base import BaseLoader, DocumentChunk


class DocxLoader(BaseLoader):
    def load(self, file_path: str) -> list[DocumentChunk]:
        name = Path(file_path).name
        doc = Document(file_path)

        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        if not text:
            return []

        return [DocumentChunk(text=text, metadata={"source": name})]
