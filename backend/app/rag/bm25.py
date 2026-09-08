from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    Performs keyword-based retrieval using BM25.
    """

    def __init__(self, documents: list[dict]):
        self.documents = documents

        # Extract text from every document chunk.
        texts = [document["text"] for document in documents]

        # Tokenize each document.
        tokenized_documents = [
            self.tokenize(text)
            for text in texts
        ]

        # Build the BM25 index.
        self.bm25 = BM25Okapi(tokenized_documents)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """
        Convert text into lowercase tokens.
        """
        return text.lower().split()

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> list[dict]:
        """
        Retrieve the top-k chunks based on BM25 keyword matching.
        """

        # Tokenize the user's query.
        tokenized_query = self.tokenize(query)

        # Calculate BM25 score for every document.
        scores = self.bm25.get_scores(tokenized_query)

        # Sort document indexes by score, highest first.
        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        # Keep only top-k results.
        ranked_indexes = ranked_indexes[:top_k]

        results = []

        for index in ranked_indexes:
            document = self.documents[index]

            results.append(
                {
                    "text": document["text"],
                    "metadata": document["metadata"],
                    "score": float(scores[index])
                }
            )

        return results