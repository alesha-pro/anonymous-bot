from dataclasses import dataclass, field

SEPARATORS = ["\n\n", "\n", ". ", ", ", " ", ""]


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)


def _split_by_separator(text: str, separator: str) -> list[str]:
    if not separator:
        return list(text)
    return text.split(separator)


def _recursive_split(
    text: str,
    separators: list[str],
    chunk_size: int,
) -> list[str]:
    """Recursively split text, trying separators from most to least preferred."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    sep = separators[0]
    remaining_seps = separators[1:] if len(separators) > 1 else separators

    parts = _split_by_separator(text, sep)

    result: list[str] = []
    current = ""

    for part in parts:
        piece = part if not current else (current + sep + part)

        if len(piece) <= chunk_size:
            current = piece
        else:
            if current:
                result.append(current)
            # This part alone is too big — split deeper
            if len(part) > chunk_size:
                sub_chunks = _recursive_split(part, remaining_seps, chunk_size)
                result.extend(sub_chunks)
                current = ""
            else:
                current = part

    if current and current.strip():
        result.append(current)

    return result


def chunk_text(
    text: str,
    metadata: dict,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[Chunk]:
    """Split text using recursive character splitter with overlap."""
    if not text.strip():
        return []

    if len(text) <= chunk_size:
        return [Chunk(text=text.strip(), metadata={**metadata, "chunk_index": 0})]

    raw_chunks = _recursive_split(text, SEPARATORS, chunk_size)

    # Merge overlap: prepend tail of previous chunk to current
    chunks: list[Chunk] = []
    for idx, raw in enumerate(raw_chunks):
        if idx > 0 and overlap > 0:
            prev = raw_chunks[idx - 1]
            tail = prev[-overlap:] if len(prev) > overlap else prev
            raw = tail + raw

        chunks.append(
            Chunk(
                text=raw.strip(),
                metadata={**metadata, "chunk_index": idx},
            )
        )

    return chunks
