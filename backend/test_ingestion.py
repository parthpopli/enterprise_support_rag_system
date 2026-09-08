from app.rag.ingestion import load_documents


DOCUMENT_PATH = r"..\data\documents\enterprise_support_sample_docs"

documents = load_documents(DOCUMENT_PATH)

print(f"\nTotal extracted sections: {len(documents)}")

for document in documents:
    print("\n" + "=" * 60)

    print("SOURCE:")
    print(document["metadata"])

    print("\nTEXT:")
    print(document["text"][:500])