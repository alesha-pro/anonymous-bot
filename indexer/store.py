import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class VectorStore:
    def __init__(self, client: QdrantClient, collection: str, vector_size: int):
        self._client = client
        self._collection = collection
        self._vector_size = vector_size

    def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = [c.name for c in self._client.get_collections().collections]
        if self._collection not in collections:
            self._client.create_collection(
                self._collection,
                vectors_config=VectorParams(
                    size=self._vector_size,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created collection '{self._collection}' (dim={self._vector_size})")
        else:
            print(f"Collection '{self._collection}' already exists")

    def upsert_chunks(
        self,
        texts: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """Upsert a batch of chunks with their vectors and metadata."""
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text, **meta},
            )
            for text, vector, meta in zip(texts, vectors, metadatas)
        ]
        self._client.upsert(self._collection, points=points, wait=True)
