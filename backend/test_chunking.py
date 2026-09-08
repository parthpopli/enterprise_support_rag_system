from app.rag.ingestion import load_documents
from app.rag.chunking import chunk_documents


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"


documents = load_documents(DOCUMENT_PATH)

chunks = chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100
)


print(f"\nDocuments: {len(documents)}")
print(f"Chunks: {len(chunks)}")


for chunk in chunks[:5]:

    print("\n" + "=" * 60)

    print("METADATA:")
    print(chunk["metadata"])

    print("\nCHUNK:")
    print(chunk["text"])