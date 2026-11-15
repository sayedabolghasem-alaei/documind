
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

        # Normalize Arabic and Persian characters
        character_map = str.maketrans({
            "ي": "ی",
            "ى": "ی",
            "ك": "ک",
            "ۀ": "ه",
            "ة": "ه",
            "أ": "ا",
            "إ": "ا",
            "ٱ": "ا"
        })

        text = text.translate(character_map)

        # Remove Arabic diacritics and tatweel
        text = re.sub(
            r"[\u064B-\u065F\u0670\u0640]",
            "",
            text
        )

        # Normalize zero-width characters
        text = text.replace("\u200c", " ")
        text = text.replace("\u200d", " ")

        # Extract Persian, English and numeric tokens
        tokens = re.findall(
            r"[^\W_]+",
            text.lower(),
            flags=re.UNICODE
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
