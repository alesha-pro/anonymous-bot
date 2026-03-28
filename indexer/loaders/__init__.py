from pathlib import Path

from indexer.loaders.base import BaseLoader
from indexer.loaders.pdf import PdfLoader
from indexer.loaders.epub import EpubLoader
from indexer.loaders.txt import TxtLoader
from indexer.loaders.docx import DocxLoader

LOADERS: dict[str, type[BaseLoader]] = {
    ".pdf": PdfLoader,
    ".epub": EpubLoader,
    ".txt": TxtLoader,
    ".docx": DocxLoader,
}


def get_loader(file_path: str) -> BaseLoader:
    ext = Path(file_path).suffix.lower()
    loader_cls = LOADERS.get(ext)
    if not loader_cls:
        supported = ", ".join(LOADERS.keys())
        raise ValueError(f"Unsupported format: {ext}. Supported: {supported}")
    return loader_cls()
