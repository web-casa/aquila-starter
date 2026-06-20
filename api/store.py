"""Thin helpers over Ollama (embeddings + generation) and Qdrant (vector store)."""
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, VectorParams

import config

_qdrant = QdrantClient(url=config.QDRANT_URL)


def embed(text: str) -> list[float]:
    """Embed a single string with the local Ollama embedding model."""
    r = httpx.post(
        f"{config.OLLAMA_URL}/api/embeddings",
        json={"model": config.EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def generate(prompt: str) -> str:
    """Generate a completion with the local Ollama chat model."""
    r = httpx.post(
        f"{config.OLLAMA_URL}/api/generate",
        json={"model": config.CHAT_MODEL, "prompt": prompt, "stream": False},
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["response"]


def ensure_collection(dim: int) -> None:
    """Create the Qdrant collection on first use (size inferred from the model)."""
    if not _qdrant.collection_exists(config.COLLECTION):
        _qdrant.create_collection(
            config.COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def upsert(points) -> None:
    _qdrant.upsert(config.COLLECTION, points=points)


def delete_source(name: str) -> None:
    """Remove all chunks previously stored for a given source file."""
    if _qdrant.collection_exists(config.COLLECTION):
        _qdrant.delete(
            config.COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=name))]
            ),
        )


def search(vector: list[float], k: int):
    return _qdrant.search(
        config.COLLECTION, query_vector=vector, limit=k, with_payload=True
    )


def client() -> QdrantClient:
    return _qdrant
