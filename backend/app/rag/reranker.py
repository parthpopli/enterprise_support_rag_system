from sentence_transformers import CrossEncoder


class Reranker:
    """
    Reranks retrieved documents based on
    query-document relevance.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 3
    ) -> list[dict]:

        if not documents:
            return []

        # Create query-document pairs.
        pairs = [
            (query, document["text"])
            for document in documents
        ]

        # Generate relevance scores.
        scores = self.model.predict(pairs)

        # Attach reranker score to every document.
        reranked_documents = []

        for document, score in zip(documents, scores):

            result = document.copy()

            result["reranker_score"] = float(score)

            reranked_documents.append(result)

        # Higher reranker score = more relevant.
        reranked_documents.sort(
            key=lambda item: item["reranker_score"],
            reverse=True
        )

        # Keep only the best documents.
        return reranked_documents[:top_k]