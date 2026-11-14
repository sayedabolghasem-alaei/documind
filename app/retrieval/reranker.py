from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3"
    ):

        self.model = CrossEncoder(
            model_name,
            max_length=512
        )

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 3
    ) -> list[dict]:

        # Validate input
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if not documents:
            return []

        # Create query-document pairs
        pairs = [
            [query, document["text"]]
            for document in documents
        ]

        # Calculate relevance scores
        scores = self.model.predict(
            pairs,
            show_progress_bar=False
        )

        # Attach reranking scores
        reranked_documents = []

        for document, score in zip(documents, scores):

            result = document.copy()

            result["rerank_score"] = float(score)

            reranked_documents.append(result)

        # Sort documents by relevance score
        reranked_documents.sort(
            key=lambda document: document["rerank_score"],
            reverse=True
        )

        return reranked_documents[:top_k]