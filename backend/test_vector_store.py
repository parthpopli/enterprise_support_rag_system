from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"


# --------------------------------------------------
# 1. Load documents
# --------------------------------------------------

documents = load_documents(DOCUMENT_PATH)

print(f"\nDocuments loaded: {len(documents)}")


# --------------------------------------------------
# 2. Chunk documents
# --------------------------------------------------

chunks = chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
)

print(f"Chunks created: {len(chunks)}")


# --------------------------------------------------
# 3. Generate embeddings
# --------------------------------------------------

embedding_model = EmbeddingModel()

embedded_documents = embedding_model.embed_documents(chunks)

print(f"Embeddings generated: {len(embedded_documents)}")


# --------------------------------------------------
# 4. Create ChromaDB vector store
# --------------------------------------------------

vector_store = VectorStore()


# --------------------------------------------------
# 5. Store embeddings + text + metadata
# --------------------------------------------------

vector_store.add_documents(embedded_documents)

print("\nDocuments successfully stored in ChromaDB!")


# --------------------------------------------------
# 6. Verify stored data
# --------------------------------------------------

count = vector_store.count()

print(f"Total chunks stored in ChromaDB: {count}")