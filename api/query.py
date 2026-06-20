"""Retrieve relevant chunks from Qdrant and generate a grounded answer."""
import config
import store

PROMPT = """You are a helpful assistant. Answer the question using ONLY the context \
below. If the context does not contain the answer, say you don't know — do not make \
things up. Cite the sources you used by their [name].

Context:
{context}

Question: {question}

Answer:"""


def ask(question: str) -> dict:
    query_vector = store.embed(question)
    hits = store.search(query_vector, config.TOP_K)

    context = "\n\n".join(
        f"[{h.payload['source']}] {h.payload['text']}" for h in hits
    )
    answer = store.generate(PROMPT.format(context=context, question=question))
    sources = sorted({h.payload["source"] for h in hits})
    return {"answer": answer.strip(), "sources": sources}
