"""Load documents -> chunk -> embed -> upsert into Qdrant."""
import pathlib
import uuid

from pypdf import PdfReader
from qdrant_client.models import PointStruct

import config
import store

SUPPORTED = {".md", ".txt", ".pdf"}


def load_text(path: pathlib.Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk(text: str) -> list[str]:
    """Fixed-size character chunks with overlap.

    Deliberately simple. For smarter strategies (recursive, semantic,
    structure-aware) see https://aquila.network/learn/rag-chunking-strategies
    """
    text = " ".join(text.split())
    step = max(1, config.CHUNK_SIZE - config.CHUNK_OVERLAP)
    chunks = [text[i : i + config.CHUNK_SIZE] for i in range(0, len(text), step)]
    return [c for c in chunks if c.strip()]


def ingest_path(path: str) -> int:
    """Ingest a single file or every supported file under a directory.

    Returns the number of chunks stored.
    """
    root = pathlib.Path(path)
    if root.is_file():
        files = [root]
    else:
        files = sorted(f for f in root.rglob("*") if f.suffix.lower() in SUPPORTED)

    points: list[PointStruct] = []
    for f in files:
        for piece in chunk(load_text(f)):
            vector = store.embed(piece)
            store.ensure_collection(len(vector))
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"text": piece, "source": f.name},
                )
            )

    if points:
        store.upsert(points)
    return len(points)
