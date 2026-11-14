import chromadb


class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(
            path="./data/chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        ids: list[str],
        texts: list[str],
        embeddings,
        metadatas: list[dict] | None = None
    ):
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding,
        n_results: int = 3
    ):
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )

        return results