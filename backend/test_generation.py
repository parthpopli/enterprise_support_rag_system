from app.rag.hybrid_search import HybridRetriever
from app.rag.reranker import Reranker
from app.rag.generator import Generator


# ---------------------------------------------------------
# 1. Initialize hybrid retriever
# ---------------------------------------------------------

print("=" * 70)
print("ENTERPRISE SUPPORT RAG - QUERY")
print("=" * 70)

print("\nInitializing hybrid retriever...")

hybrid_retriever = HybridRetriever()

print("Hybrid retriever ready.")


# ---------------------------------------------------------
# 2. User query
# ---------------------------------------------------------

query = (
    "I forgot my password. "
    "How can I reset it?"
)

print(f"\nQuery: {query}")


# ---------------------------------------------------------
# 3. Hybrid retrieval
# ---------------------------------------------------------

print("\nRunning hybrid retrieval...")

hybrid_results = hybrid_retriever.retrieve(
    query=query,
    top_k=5,
    candidate_k=5
)

print(
    f"Hybrid candidates: "
    f"{len(hybrid_results)}"
)


# ---------------------------------------------------------
# 4. Reranking
# ---------------------------------------------------------

print("\nRunning reranker...")

reranker = Reranker()

final_documents = reranker.rerank(
    query=query,
    documents=hybrid_results,
    top_k=3
)

print(
    f"Final context chunks: "
    f"{len(final_documents)}"
)


# ---------------------------------------------------------
# 5. Generate answer
# ---------------------------------------------------------

print("\nGenerating answer...")

generator = Generator()

answer = generator.generate(
    query=query,
    documents=final_documents
)


# ---------------------------------------------------------
# 6. Display answer
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL ANSWER")
print("=" * 70)

print(answer)


# ---------------------------------------------------------
# 7. Display sources
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("SOURCES")
print("=" * 70)

for document in final_documents:

    source = document["metadata"].get(
        "source",
        "Unknown"
    )

    page = document["metadata"].get(
        "page",
        "Unknown"
    )

    chunk_index = document["metadata"].get(
        "chunk_index",
        "Unknown"
    )

    reranker_score = document.get(
        "reranker_score",
        "Unknown"
    )

    print(
        f"- {source} | "
        f"Page: {page} | "
        f"Chunk: {chunk_index} | "
        f"Reranker Score: {reranker_score}"
    )