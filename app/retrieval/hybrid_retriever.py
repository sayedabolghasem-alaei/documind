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

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:

        # Validate input
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        # Retrieve more candidates than final top_k
        candidate_k = top_k * 5

        vector_results = self.vector_retriever.retrieve(
            query=query,
            top_k=candidate_k
        )

        keyword_results = self.keyword_retriever.retrieve(
            query=query,
            top_k=candidate_k
        )

        # Reciprocal Rank Fusion
        rrf_k = 60
        fused_results = {}

        result_lists = [
            ("vector", vector_results),
            ("keyword", keyword_results)
        ]

        for source, results in result_lists:

            for rank, document in enumerate(results, start=1):

                document_id = document["id"]

                if document_id not in fused_results:

                    fused_results[document_id] = {
                        "id": document_id,
                        "text": document["text"],
                        "metadata": document["metadata"],
                        "rrf_score": 0.0,
                        "retrieval_sources": [],
                        "ranks": {}
                    }

                # Calculate RRF score
                fused_results[document_id]["rrf_score"] += (
                    1 / (rrf_k + rank)
                )

                # Track retrieval source
                fused_results[document_id]["retrieval_sources"].append(
                    source
                )

                # Track individual rank
                fused_results[document_id]["ranks"][source] = rank

        # Sort candidates by RRF score
        ranked_candidates = sorted(
            fused_results.values(),
            key=lambda document: document["rrf_score"],
            reverse=True
        )

        # Apply Reranking
        final_results = self.reranker.rerank(
            query=query,
            documents=ranked_candidates,
            top_k=top_k
        )

        return final_results