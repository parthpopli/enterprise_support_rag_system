from app.rag.retriever import Retriever


# Create retriever
retriever = Retriever()


# Test query
query = "I forgot my password. How can I reset it?"


# Retrieve the top 5 relevant chunks
results = retriever.retrieve(
    query=query,
    top_k=5
)


print("\n" + "=" * 70)
print("QUERY:")
print(query)


print("\n" + "=" * 70)
print(f"RETRIEVED RESULTS: {len(results)}")


for index, result in enumerate(results, start=1):

    print("\n" + "-" * 70)

    print(f"RESULT #{index}")

    print("\nDistance:")
    print(result["distance"])

    print("\nMetadata:")
    print(result["metadata"])

    print("\nText:")
    print(result["text"])