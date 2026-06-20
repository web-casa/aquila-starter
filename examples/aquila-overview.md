# Aquila Starter — overview

Aquila Starter is a one-command, fully local RAG (retrieval-augmented generation)
stack. It runs Ollama for the language model and embeddings, Qdrant as the vector
database, and a small FastAPI service that ingests your documents and answers
questions about them.

Nothing leaves your machine: there are no external API keys and no per-search fees.
You drop documents into a folder, the service chunks and embeds them into Qdrant, and
when you ask a question it retrieves the most relevant chunks and has the local model
answer using only that context — citing its sources.

It is intentionally minimal: a starting point you fork and extend, not a finished
product. The full concepts and tutorials live at aquila.network.
