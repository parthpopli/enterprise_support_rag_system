from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


class Retriever:
    """
    Retrieves relevant document chunks for a user query.
    """

    def __init__(self):
        # Load the same embedding model used during ingestion.
        self.embedding_model = EmbeddingModel()

        # Connect to our ChromaDB vector store.
        self.vector_store = VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> list[dict]:
        """
        Convert the user query into an embedding
        and retrieve the most relevant chunks.
        """

        # 1. Convert user query into a vector.
        query_embedding = self.embedding_model.embed_text(
            query
        )

        # 2. Search ChromaDB using the query vector.
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        # 3. Convert ChromaDB response into a simpler format.
        retrieved_documents = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            retrieved_documents.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance
                }
            )

        return retrieved_documents