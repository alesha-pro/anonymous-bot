from qdrant_client import QdrantClient


def make_qdrant_client(host: str, port: int) -> QdrantClient:
    return QdrantClient(host=host, port=port)
