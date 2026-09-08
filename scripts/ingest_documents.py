import json
import sys
from pathlib import Path

# Add backend/ to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))

from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


DOCUMENT_PATH = (
    PROJECT_ROOT
    / "data"
    / "documents"
    / "enterprise_support_sample_docs"
)

PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
CHUNKS_FILE = PROCESSED_PATH / "chunks.json"


def main():

    print("=" * 70)
    print("ENTERPRISE SUPPORT RAG - DOCUMENT INGESTION")
    print("=" * 70)

    # -------------------------------------------------
    # 1. Load documents
    # -------------------------------------------------

    print("\n[1/5] Loading documents...")

    documents = load_documents(
        str(DOCUMENT_PATH)
    )

    print(f"Documents loaded: {len(documents)}")

    if not documents:
        print("No documents found.")
        return

    # -------------------------------------------------
    # 2. Create chunks
    # -------------------------------------------------

    print("\n[2/5] Creating chunks...")

    chunks = chunk_documents(
        documents,
        chunk_size=500,
        chunk_overlap=100
    )

    print(f"Chunks created: {len(chunks)}")

    # -------------------------------------------------
    # 3. Save chunks
    # -------------------------------------------------

    print("\n[3/5] Saving chunks to chunks.json...")

    PROCESSED_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CHUNKS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Chunks saved to: {CHUNKS_FILE}")

    # -------------------------------------------------
    # 4. Generate embeddings
    # -------------------------------------------------

    print("\n[4/5] Generating embeddings...")

    embedding_model = EmbeddingModel()

    embedded_documents = (
        embedding_model.embed_documents(chunks)
    )

    print(
        f"Embeddings generated: "
        f"{len(embedded_documents)}"
    )

    # -------------------------------------------------
    # 5. Store in ChromaDB
    # -------------------------------------------------

    print("\n[5/5] Storing embeddings in ChromaDB...")

    vector_store = VectorStore()

    vector_store.add_documents(
        embedded_documents
    )

    print(
        "Documents successfully stored in ChromaDB!"
    )

    print(
        f"Total chunks in ChromaDB: "
        f"{vector_store.count()}"
    )

    print("\n" + "=" * 70)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()