from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents
from app.rag.hybrid_search import HybridRetriever
from app.rag.reranker import Reranker


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"


# --------------------------------------------------
# 1. Load documents
# --------------------------------------------------

documents = load_documents(DOCUMENT_PATH)

print(f"\nDocuments loaded: {len(documents)}")


# --------------------------------------------------
# 2. Create chunks
# --------------------------------------------------

chunks = chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
)

print(f"Chunks created: {len(chunks)}")


# --------------------------------------------------
# 3. Hybrid retrieval
# --------------------------------------------------

hybrid_retriever = HybridRetriever(chunks)

query = "I forgot my password. How can I reset it?"

hybrid_results = hybrid_retriever.retrieve(
    query=query,
    top_k=5,
    candidate_k=5
)

print("\n" + "=" * 70)
print("HYBRID RESULTS")
print("=" * 70)

for index, result in enumerate(hybrid_results, start=1):

    print(f"\nRESULT #{index}")
    print("Hybrid Score:", result["hybrid_score"])
    print("Source:", result["metadata"]["source"])
    print("Chunk:", result["metadata"]["chunk_index"])


# --------------------------------------------------
# 4. Reranking
# --------------------------------------------------

reranker = Reranker()

reranked_results = reranker.rerank(
    query=query,
    documents=hybrid_results,
    top_k=3
)


# --------------------------------------------------
# 5. Display final results
# --------------------------------------------------

print("\n" + "=" * 70)
print("FINAL RERANKED RESULTS")
print("=" * 70)

for index, result in enumerate(reranked_results, start=1):

    print("\n" + "-" * 70)

    print(f"FINAL RESULT #{index}")

    print("\nReranker Score:")
    print(result["reranker_score"])

    print("\nSource:")
    print(result["metadata"]["source"])

    print("\nChunk:")
    print(result["metadata"]["chunk_index"])

    print("\nText:")
    print(result["text"])