from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents
from app.rag.bm25 import BM25Retriever


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"


# 1. Load documents
documents = load_documents(DOCUMENT_PATH)

# 2. Create chunks
chunks = chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
)

# 3. Create BM25 retriever
bm25 = BM25Retriever(chunks)

# 4. Query
query = "I forgot my password. How can I reset it?"

results = bm25.retrieve(
    query=query,
    top_k=5
)

print("\n" + "=" * 70)
print("QUERY:")
print(query)

print("\n" + "=" * 70)
print(f"BM25 RESULTS: {len(results)}")

for index, result in enumerate(results, start=1):

    print("\n" + "-" * 70)
    print(f"RESULT #{index}")

    print("\nBM25 Score:")
    print(result["score"])

    print("\nMetadata:")
    print(result["metadata"])

    print("\nText:")
    print(result["text"])