from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents
from app.rag.hybrid_search import HybridRetriever


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"


# 1. Load documents
documents = load_documents(DOCUMENT_PATH)

# 2. Create chunks
chunks = chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
)

# 3. Create hybrid retriever
hybrid_retriever = HybridRetriever(chunks)

# 4. Query
query = "I forgot my password. How can I reset it?"

results = hybrid_retriever.retrieve(
    query=query,
    top_k=5,
    candidate_k=5
)

print("\n" + "=" * 70)
print("QUERY:")
print(query)

print("\n" + "=" * 70)
print(f"HYBRID RESULTS: {len(results)}")

for index, result in enumerate(results, start=1):

    print("\n" + "-" * 70)
    print(f"RESULT #{index}")

    print("\nHybrid Score:")
    print(result["hybrid_score"])

    print("\nMetadata:")
    print(result["metadata"])

    print("\nText:")
    print(result["text"])