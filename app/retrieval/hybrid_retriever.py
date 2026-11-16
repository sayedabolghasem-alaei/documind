
import hashlib

from app.retrieval.retriever import Retriever
from app.retrieval.keyword_retriever import KeywordRetriever
from app.retrieval.reranker import Reranker


class HybridRetriever:

    def __init__(self, collection_name: str = "documents"):

        self.vector_retriever = Retriever(
            collection_name=collection_name
        )

        self.keyword_retriever = KeywordRetriever(
            collection_name=collection_name
        )

        self.reranker = Reranker()

    @staticmethod
    def _content_key(text: str) -> str:
        """Create a stable key from normalized document content."""

        normalized_text = " ".join(text.split()).casefold()

        return hashlib.sha256(
            normalized_text.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _merge_metadata(existing: dict, incoming: dict) -> dict:
        """Merge source-related metadata without losing provenance."""

        merged = dict(existing)

        merge_fields = {
            "source",
            "sources",
            "page",
            "pages",
            "file_type",
            "file_types",
            "chunk_index",
            "chunk_indices"
        }

        for key in merge_fields:

            values = []

            for metadata in (existing, incoming):

                value = metadata.get(key)

                if value is None:
                    continue

                if isinstance(value, list):
                    items = value
                else:
                    items = str(value).split(",")

                values.extend(
                    str(item).strip()
                    for item in items
                    if str(item).strip()
                )

            unique_values = list(dict.fromkeys(values))

            if unique_values:
                merged[key] = ", ".join(unique_values)

        return merged

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query = query.strip()

        # Step 1: Retrieve candidate documents
        candidate_k = top_k * 5

        vector_results = self.vector_retriever.retrieve(
            query=query,
            top_k=candidate_k
        )

        keyword_results = self.keyword_retriever.retrieve(
            query=query,
            top_k=candidate_k
        )

        # Step 2: Apply content-aware Reciprocal Rank Fusion
        rrf_k = 60
        fused_results = {}

        result_lists = [
            ("vector", vector_results),
            ("keyword", keyword_results)
        ]

        for source, results in result_lists:

            for rank, document in enumerate(results, start=1):

                content_key = self._content_key(
                    document["text"]
                )

                if content_key not in fused_results:

                    fused_results[content_key] = {
                        "id": document["id"],
                        "duplicate_ids": [],
                        "text": document["text"],
                        "metadata": dict(document["metadata"]),
                        "rrf_score": 0.0,
                        "retrieval_sources": [],
                        "ranks": {}
                    }

                fused_document = fused_results[content_key]

                # Preserve IDs of duplicate chunks
                if (
                    document["id"] != fused_document["id"]
                    and document["id"] not in fused_document["duplicate_ids"]
                ):
                    fused_document["duplicate_ids"].append(
                        document["id"]
                    )

                # Merge metadata from duplicate chunks
                fused_document["metadata"] = self._merge_metadata(
                    fused_document["metadata"],
                    document["metadata"]
                )

                # Count each retrieval source only once
                if source not in fused_document["retrieval_sources"]:

                    fused_document["rrf_score"] += (
                        1 / (rrf_k + rank)
                    )

                    fused_document["retrieval_sources"].append(
                        source
                    )

                    fused_document["ranks"][source] = rank

        # Step 3: Sort fused candidates
        ranked_candidates = sorted(
            fused_results.values(),
            key=lambda document: document["rrf_score"],
            reverse=True
        )

        # Step 4: Apply Reranking
        return self.reranker.rerank(
            query=query,
            documents=ranked_candidates,
            top_k=top_k
        )
    