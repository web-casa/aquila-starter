"""Load documents -> chunk -> embed -> upsert into Qdrant."""
import pathlib
import uuid

from pypdf import PdfReader
from qdrant_client.models import PointStruct

import config
import store

SUPPORTED = {".md", ".txt", ".pdf"}
DATA_ROOT = pathlib.Path("data").resolve()
_NS = uuid.uuid5(uuid.NAMESPACE_DNS, "aquila-starter")


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


def _resolve(subpath: str) -> pathlib.Path:
    """Resolve a request path strictly inside the data directory (no traversal)."""
    target = (DATA_ROOT / subpath).resolve()
    if target != DATA_ROOT and DATA_ROOT not in target.parents:
        raise ValueError("path must be inside the data directory")
    return target


def ingest_path(subpath: str = "") -> int:
    """Ingest a file or every supported file under a path *within* ./data.

    Re-ingesting a file replaces its previous chunks (deterministic IDs +
    delete-by-source), so the collection doesn't grow with duplicates.
    Returns the number of chunks stored.
    """
    target = _resolve(subpath)
    if target.is_file():
        files = [target] if target.suffix.lower() in SUPPORTED else []
    elif target.is_dir():
        files = sorted(f for f in target.rglob("*") if f.suffix.lower() in SUPPORTED)
    else:
        files = []

    total = 0
    for f in files:
        pieces = chunk(load_text(f))
        if not pieces:
            continue
        points = []
        for i, piece in enumerate(pieces):
            vector = store.embed(piece)
            store.ensure_collection(len(vector))
            points.append(
                PointStruct(
                    id=str(uuid.uuid5(_NS, f"{f.name}:{i}")),
                    vector=vector,
                    payload={"text": piece, "source": f.name},
                )
            )
        store.delete_source(f.name)  # drop any previous chunks for this file
        store.upsert(points)
        total += len(points)
    return total
