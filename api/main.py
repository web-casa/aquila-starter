"""Aquila Starter API — private, self-hosted AI search you own.

Endpoints:
  GET  /health          — is Ollama + Qdrant reachable?
  POST /ingest          — index files already under ./data  (JSON: {"path": "data"})
  POST /ingest/upload   — upload a file (multipart) and index it
  POST /ask             — ask a question  (JSON: {"question": "..."})
"""
import pathlib
import shutil

import httpx
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

import config
import ingest
import query
import store

app = FastAPI(
    title="Aquila Starter",
    description="Private, self-hosted AI search you own — Ollama + Qdrant + FastAPI.",
    version="0.1.0",
)

DATA_DIR = pathlib.Path("data")


class IngestRequest(BaseModel):
    # Path relative to ./data; empty = the whole data directory.
    path: str = ""


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    status = {}
    try:
        httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=5).raise_for_status()
        status["ollama"] = True
    except Exception:
        status["ollama"] = False
    try:
        store.client().get_collections()
        status["qdrant"] = True
    except Exception:
        status["qdrant"] = False
    return {"status": "ok" if all(status.values()) else "degraded", **status}


@app.post("/ingest")
def ingest_endpoint(body: IngestRequest) -> dict:
    return {"path": body.path, "ingested_chunks": ingest.ingest_path(body.path)}


# Sync def → FastAPI runs it in a threadpool, so the blocking embed/ingest work
# never stalls the event loop (health/ask stay responsive during an upload).
@app.post("/ingest/upload")
def ingest_upload(file: UploadFile) -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    dest = DATA_DIR / pathlib.Path(file.filename).name
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return {"file": dest.name, "ingested_chunks": ingest.ingest_path(dest.name)}


@app.post("/ask")
def ask_endpoint(body: AskRequest) -> dict:
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    return query.ask(body.question)
