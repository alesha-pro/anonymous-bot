"""Index documents into Qdrant vector store.

Usage:
    python -m indexer path/to/documents/
    python -m indexer path/to/single_file.pdf
"""

import sys
from pathlib import Path

from indexer.config import settings
from indexer.loaders import get_loader, LOADERS
from indexer.chunker import chunk_text
from indexer.embeddings import EmbeddingClient
from indexer.store import VectorStore
from shared.qdrant import make_qdrant_client

BATCH_SIZE = 64


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m indexer <path/to/documents/>")
        sys.exit(1)

    doc_path = Path(sys.argv[1])

    if doc_path.is_dir():
        files = [
            f
            for f in sorted(doc_path.iterdir())
            if f.is_file() and f.suffix.lower() in LOADERS
        ]
    elif doc_path.is_file():
        files = [doc_path]
    else:
        print(f"Path not found: {doc_path}")
        sys.exit(1)

    if not files:
        print("No supported files found.")
        sys.exit(1)

    print(f"Found {len(files)} file(s) to index")

    embed_client = EmbeddingClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.effective_embed_base_url,
        model=settings.openrouter_embed_model,
    )

    qdrant = make_qdrant_client(settings.qdrant_host, settings.qdrant_port)

    # Determine vector size from a test embedding
    test_vec = embed_client.embed_single("test")
    store = VectorStore(qdrant, settings.qdrant_collection, len(test_vec))
    store.ensure_collection()

    for file in files:
        print(f"\nProcessing: {file.name}")

        try:
            loader = get_loader(str(file))
        except ValueError as e:
            print(f"  Skipping: {e}")
            continue

        doc_chunks = loader.load(str(file))
        print(f"  Extracted {len(doc_chunks)} segment(s)")

        all_chunks = []
        for dc in doc_chunks:
            all_chunks.extend(chunk_text(dc.text, dc.metadata))

        print(f"  Split into {len(all_chunks)} chunk(s)")

        indexed = 0
        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i : i + BATCH_SIZE]
            texts = [c.text for c in batch]
            metas = [c.metadata for c in batch]
            vectors = embed_client.embed(texts)
            store.upsert_chunks(texts, vectors, metas)
            indexed += len(batch)
            print(f"  Indexed {indexed}/{len(all_chunks)}")

    print("\nDone!")


if __name__ == "__main__":
    main()
