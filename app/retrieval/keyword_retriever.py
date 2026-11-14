
import re

from rank_bm25 import BM25Okapi
from app.retrieval.vector_store import VectorStore


class KeywordRetriever:

    def __init__(self, collection_name: str = "documents"):

        self.vector_store = VectorStore(
            collection_name=collection_name
        )

        # Load all stored documents from ChromaDB
        stored_data = self.vector_store.collection.get(
            include=["documents", "metadatas"]
        )

        self.documents = []

        for index, document_text in enumerate(
            stored_data["documents"]
        ):
            self.documents.append({
                "id": stored_data["ids"][index],
                "text": document_text,
                "metadata": stored_data["metadatas"][index]
            })

        # Tokenize documents
        self.tokenized_documents = [
            self._tokenize(document["text"])
            for document in self.documents
        ]

        # Initialize BM25
        self.bm25 = (
            BM25Okapi(self.tokenized_documents)
            if self.tokenized_documents
            else None
        )

    def _tokenize(self, text: str) -> list[str]:

        # Normalize Persian and Arabic characters
        text = text.replace("ي", "ی")
        text = text.replace("ك", "ک")
        text = text.replace("ۀ", "ه")
        text = text.replace("ة", "ه")

        # Extract Persian, English and numeric tokens
        tokens = re.findall(
            r"[آ-یA-Za-z0-9]+",
            text.lower()
        )

        return tokens

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self.bm25 is None:
            return []

        tokenized_query = self._tokenize(query)

        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices:

            score = float(scores[index])

            if score <= 0:
                continue

            result = self.documents[index].copy()
            result["score"] = score

            results.append(result)

            if len(results) == top_k:
                break

        return results
