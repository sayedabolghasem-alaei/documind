from concurrent.futures import ThreadPoolExecutor

from app.agent.router.query_router import QueryRouter
from app.retrieval.hybrid_graph_retriever import HybridGraphRetriever


class RetrievalOrchestrator:

    def __init__(self, collection_name: str = "documents"):

        self.router = QueryRouter()

        self.retriever = HybridGraphRetriever(
            collection_name=collection_name
        )

    def _safe_document_retrieval(
        self,
        query: str,
        top_k: int
    ) -> tuple:

        try:
            results = self.retriever.retrieve_documents(
                query=query,
                top_k=top_k
            )

            return results, ""

        except Exception as error:
            return [], str(error)

    def _safe_graph_retrieval(
        self,
        query: str
    ) -> tuple:

        try:
            results = self.retriever.retrieve_graph(
                query=query
            )

            return results, ""

        except Exception as error:

            return {
                "query": query,
                "matched_entities": [],
                "entities": [],
                "relationships": []
            }, str(error)

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> dict:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query = query.strip()

        # Step 1: Select retrieval strategy
        strategy = self.router.route(query)

        vector_results = []

        graph_results = {
            "query": query,
            "matched_entities": [],
            "entities": [],
            "relationships": []
        }

        retrieval_status = {
            "documents": "skipped",
            "graph": "skipped"
        }

        retrieval_errors = {}

        # Step 2: Documents-only retrieval
        if strategy == "documents":

            documents, error = self._safe_document_retrieval(
                query=query,
                top_k=top_k
            )

            vector_results = documents

            if error:
                retrieval_status["documents"] = "failed"
                retrieval_errors["documents"] = error
            else:
                retrieval_status["documents"] = "success"

        # Step 3: Graph-only retrieval
        elif strategy == "graph":

            graph, error = self._safe_graph_retrieval(
                query=query
            )

            graph_results = graph

            if error:
                retrieval_status["graph"] = "failed"
                retrieval_errors["graph"] = error
            else:
                retrieval_status["graph"] = "success"

        # Step 4: Hybrid parallel retrieval
        elif strategy == "hybrid":

            with ThreadPoolExecutor(max_workers=2) as executor:

                document_future = executor.submit(
                    self._safe_document_retrieval,
                    query,
                    top_k
                )

                graph_future = executor.submit(
                    self._safe_graph_retrieval,
                    query
                )

                documents, document_error = document_future.result()

                graph, graph_error = graph_future.result()

            vector_results = documents
            graph_results = graph

            if document_error:
                retrieval_status["documents"] = "failed"
                retrieval_errors["documents"] = document_error
            else:
                retrieval_status["documents"] = "success"

            if graph_error:
                retrieval_status["graph"] = "failed"
                retrieval_errors["graph"] = graph_error
            else:
                retrieval_status["graph"] = "success"

        else:
            raise ValueError(
                f"Unsupported retrieval strategy: {strategy}"
            )

        # Step 5: Check whether all selected branches failed
        active_statuses = [
            status
            for status in retrieval_status.values()
            if status != "skipped"
        ]

        all_failed = (
            bool(active_statuses)
            and all(
                status == "failed"
                for status in active_statuses
            )
        )

        error_message = ""

        if all_failed:
            error_message = (
                "All selected retrieval strategies failed."
            )

        # Step 6: Return orchestration result
        return {
            "query": query,
            "strategy": strategy,
            "vector_results": vector_results,
            "graph_results": graph_results,
            "retrieval_status": retrieval_status,
            "retrieval_errors": retrieval_errors,
            "error": error_message
        }