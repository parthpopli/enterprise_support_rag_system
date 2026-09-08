import chromadb
from pathlib import Path


class VectorStore:

    def __init__(
        self,
        persist_directory=None,
        collection_name="enterprise_support"
    ):

        if persist_directory is None:

            project_root = (
                Path(__file__)
                .resolve()
                .parents[3]
            )

            persist_directory = (
                project_root
                / "vector_store"
            )

        self.persist_directory = str(
            persist_directory
        )

        self.client = (
            chromadb.PersistentClient(
                path=self.persist_directory
            )
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name
            )
        )

    def add_documents(
        self,
        documents
    ):

        if not documents:
            return

        ids = []
        texts = []
        embeddings = []
        metadatas = []

        for index, document in enumerate(
            documents
        ):

            source = document[
                "metadata"
            ].get(
                "source",
                "unknown"
            )

            chunk_index = document[
                "metadata"
            ].get(
                "chunk_index",
                index
            )

            ids.append(
                f"{source}_{chunk_index}"
            )

            texts.append(
                document["text"]
            )

            embeddings.append(
                document["embedding"]
            )

            metadatas.append(
                document["metadata"]
            )

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k
        )

        return results

    def delete_by_source(
        self,
        source: str
    ):

        self.collection.delete(
            where={
                "source": source
            }
        )

    def count(self):
        return self.collection.count()