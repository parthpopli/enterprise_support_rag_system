from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents
from app.rag.embeddings import EmbeddingModel


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"


# 1. Load documents
documents = load_documents(DOCUMENT_PATH)

# 2. Create chunks
chunks = chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
)

# 3. Create embedding model
embedding_model = EmbeddingModel()

# 4. Generate embeddings
embedded_documents = embedding_model.embed_documents(chunks)


print(f"\nDocuments: {len(documents)}")
print(f"Chunks: {len(chunks)}")
print(f"Embedded chunks: {len(embedded_documents)}")

print("\nFirst embedding:")
print(embedded_documents[0]["embedding"][:10])

print("\nEmbedding dimensions:")
print(len(embedded_documents[0]["embedding"]))

print("\nMetadata:")
print(embedded_documents[0]["metadata"])