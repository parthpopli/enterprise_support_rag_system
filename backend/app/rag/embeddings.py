from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Handles conversion of text into numerical embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a single piece of text into an embedding vector.
        """

        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )

        return embedding.tolist()

    def embed_documents(
        self,
        documents: list[dict]
    ) -> list[dict]:
        """
        Generate embeddings for multiple document chunks.
        """

        texts = [
            document["text"]
            for document in documents
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )

        embedded_documents = []

        for document, embedding in zip(
            documents,
            embeddings
        ):
            embedded_documents.append(
                {
                    "text": document["text"],
                    "metadata": document["metadata"],
                    "embedding": embedding.tolist()
                }
            )

        return embedded_documents