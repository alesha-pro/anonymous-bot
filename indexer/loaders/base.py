from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    """Raw extracted text with metadata, before chunking."""

    text: str
    metadata: dict = field(default_factory=dict)


class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> list[DocumentChunk]:
        """Extract text segments from a file with per-segment metadata."""
        ...
