# Aquila Starter

**Private, self-hosted AI search you own** — a one-command RAG stack that runs
entirely on your own machine. No data leaves the box, no API keys, no per-search bill.

[Ollama](https://ollama.com) (local LLM + embeddings) · [Qdrant](https://qdrant.tech)
(vector database) · [FastAPI](https://fastapi.tiangolo.com) (ingest + ask). Apache-2.0.

> This is the runnable version of the guides at **[aquila.network](https://aquila.network)**.
> It's a *starter* — minimal and readable on purpose, meant to be forked and built on.

## Quickstart

Requires Docker. One command brings up Ollama, Qdrant, and the API, and pulls the
models on first run (the chat model is a few GB, so the first start takes a while):

```bash
git clone https://github.com/web-casa/aquila-starter.git
cd aquila-starter
docker compose up --build
```

Drop some documents (`.md`, `.txt`, `.pdf`) into `./data/`, then index and ask:

```bash
# index everything under ./data
curl -X POST localhost:8000/ingest -H 'content-type: application/json' -d '{"path":"data"}'

# or upload a single file
curl -X POST localhost:8000/ingest/upload -F file=@./examples/aquila-overview.md

# ask a question — answered only from your documents, with sources
curl -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question":"What is Aquila Starter?"}'
```

```json
{ "answer": "Aquila Starter is a one-command, fully local RAG stack ...",
  "sources": ["aquila-overview.md"] }
```

Interactive API docs: <http://localhost:8000/docs> · health: `GET /health`.

## How it works

```
documents → chunk → embed (Ollama) → store (Qdrant)
                                          │
question → embed (Ollama) → search (Qdrant) → context → generate (Ollama) → answer + sources
```

Standard retrieval-augmented generation: your docs are chunked, embedded with a local
model, and stored as vectors in Qdrant. At query time we embed the question, pull the
most relevant chunks, and ask the local LLM to answer **only** from that context.

## Configuration

Copy `.env.example` to `.env` and tweak (defaults work out of the box):

| Var | Default | What |
|---|---|---|
| `CHAT_MODEL` | `llama3.1` | Ollama model for answers |
| `EMBED_MODEL` | `nomic-embed-text` | Ollama model for embeddings |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `1000` / `150` | chunking (characters) |
| `TOP_K` | `5` | chunks retrieved per question |

## Going further (the guides)

Each piece here is covered in depth on aquila.network — start there when you outgrow
the defaults:

- **Concepts & full walkthrough** → [Self-Hosted RAG: the complete guide](https://aquila.network/learn/self-hosted-rag-complete-guide)
- **Deploy on a VPS** → [Build a private RAG on a VPS](https://aquila.network/learn/build-private-rag-on-a-vps)
- **Chat with your documents** → [Chat with your documents, self-hosted](https://aquila.network/learn/chat-with-your-documents-self-hosted)
- **Better chunking** → [RAG chunking strategies](https://aquila.network/learn/rag-chunking-strategies)
- **Pick an embedding model** → [Best local embedding models](https://aquila.network/learn/best-local-embedding-models)
- **Why Qdrant / how to swap it** → [Best self-hosted vector databases](https://aquila.network/compare/best-self-hosted-vector-databases)

Want to swap Qdrant for pgvector or Chroma, add a reranker, or evaluate quality?
Those are on the roadmap and each maps to a guide above.

## Roadmap

- [x] **v0.1** — compose stack, ingest (md/txt/pdf), ask with sources
- [ ] **v0.2** — minimal web UI for ask-with-citations
- [ ] **v0.3** — hybrid search; swap-in pgvector / Chroma
- [ ] **v0.4** — reranker (bge-reranker) + a small eval script

## License

Apache-2.0 — see [LICENSE](./LICENSE). Built by the Aquila Team.
**Own your search.**
