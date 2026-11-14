from app.embedding.embedding_model import EmbeddingModel
from app.retrieval.vector_store import VectorStore


class Retriever:

    def __init__(
        self,
        collection_name: str = "documents"
    ):

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore(
            collection_name=collection_name
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        # Step 1: Convert query into an embedding
        query_embedding = self.embedding_model.encode(
            [query]
        )[0]

        # Step 2: Search in ChromaDB
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k
        )

        # Step 3: Prepare search results
        retrieved_documents = []

        for index in range(len(results["ids"][0])):

            retrieved_documents.append({
                "id": results["ids"][0][index],
                "text": results["documents"][0][index],
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index]
            })

        return retrieved_documents