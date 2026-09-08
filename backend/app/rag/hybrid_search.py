import json
from pathlib import Path

from app.rag.bm25 import BM25Retriever
from app.rag.retriever import Retriever


class HybridRetriever:

    def __init__(
        self,
        chunks_file: str = None
    ):

        # -------------------------------------------------
        # Find chunks.json
        # -------------------------------------------------

        if chunks_file is None:

            project_root = (
                Path(__file__)
                .resolve()
                .parents[3]
            )

            chunks_file = (
                project_root
                / "data"
                / "processed"
                / "chunks.json"
            )

        self.chunks_file = Path(chunks_file)

        # -------------------------------------------------
        # Load processed chunks
        # -------------------------------------------------

        if not self.chunks_file.exists():

            raise FileNotFoundError(
                f"chunks.json not found at: "
                f"{self.chunks_file}\n"
                f"Run scripts/ingest_documents.py first."
            )

        with open(
            self.chunks_file,
            "r",
            encoding="utf-8"
        ) as file:

            documents = json.load(file)

        if not documents:

            raise ValueError(
                "chunks.json is empty."
            )

        self.documents = documents

        # -------------------------------------------------
        # Initialize retrievers
        # -------------------------------------------------

        self.vector_retriever = Retriever()

        self.bm25_retriever = BM25Retriever(
            documents
        )


    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 5
    ) -> list[dict]:

        # -------------------------------------------------
        # Vector search
        # -------------------------------------------------

        vector_results = (
            self.vector_retriever.retrieve(
                query=query,
                top_k=candidate_k
            )
        )


        # -------------------------------------------------
        # BM25 search
        # -------------------------------------------------

        bm25_results = (
            self.bm25_retriever.retrieve(
                query=query,
                top_k=candidate_k
            )
        )


        # -------------------------------------------------
        # Reciprocal Rank Fusion
        # -------------------------------------------------

        fused_scores = {}

        k = 60


        # Vector results

        for rank, result in enumerate(
            vector_results,
            start=1
        ):

            document_id = (
                result["metadata"]["source"],
                result["metadata"]["chunk_index"]
            )

            fused_scores.setdefault(
                document_id,
                {
                    "score": 0.0,
                    "result": result
                }
            )

            fused_scores[
                document_id
            ]["score"] += 1 / (k + rank)


        # BM25 results

        for rank, result in enumerate(
            bm25_results,
            start=1
        ):

            document_id = (
                result["metadata"]["source"],
                result["metadata"]["chunk_index"]
            )

            fused_scores.setdefault(
                document_id,
                {
                    "score": 0.0,
                    "result": result
                }
            )

            fused_scores[
                document_id
            ]["score"] += 1 / (k + rank)


        # -------------------------------------------------
        # Sort fused results
        # -------------------------------------------------

        ranked_results = sorted(
            fused_scores.values(),
            key=lambda item: item["score"],
            reverse=True
        )


        # -------------------------------------------------
        # Return top results
        # -------------------------------------------------

        final_results = []

        for item in ranked_results[:top_k]:

            result = item["result"].copy()

            result["hybrid_score"] = (
                item["score"]
            )

            final_results.append(result)


        return final_results