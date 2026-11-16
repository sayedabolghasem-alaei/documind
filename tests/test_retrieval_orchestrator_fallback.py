
from app.agent.orchestration.retrieval_orchestrator import RetrievalOrchestrator
from app.agent.router.query_router import QueryRouter


class FakeRetriever:

    def __init__(self, fail_documents=False, fail_graph=False):
        self.fail_documents = fail_documents
        self.fail_graph = fail_graph

    def retrieve_documents(self, query, top_k):
        if self.fail_documents:
            raise RuntimeError("Document retrieval failed.")

        return [
            {
                "text": "Sample document result",
                "metadata": {"source": "test.pdf"}
            }
        ]

    def retrieve_graph(self, query):
        if self.fail_graph:
            raise RuntimeError("Graph retrieval failed.")

        return {
            "query": query,
            "matched_entities": [],
            "entities": [],
            "relationships": []
        }


def create_test_orchestrator(retriever):
    orchestrator = RetrievalOrchestrator.__new__(
        RetrievalOrchestrator
    )
    orchestrator.router = QueryRouter()
    orchestrator.retriever = retriever
    return orchestrator


def test_partial_failure():

    orchestrator = create_test_orchestrator(
        FakeRetriever(fail_graph=True)
    )

    result = orchestrator.retrieve(
        query="ارتباط بین محصول A و محصول B چیست؟",
        top_k=3
    )

    assert result["strategy"] == "hybrid"
    assert result["retrieval_status"]["documents"] == "success"
    assert result["retrieval_status"]["graph"] == "failed"
    assert len(result["vector_results"]) == 1
    assert result["error"] == ""

    print("Partial failure test passed.")


def test_all_retrievers_failure():

    orchestrator = create_test_orchestrator(
        FakeRetriever(
            fail_documents=True,
            fail_graph=True
        )
    )

    result = orchestrator.retrieve(
        query="ارتباط بین محصول A و محصول B چیست؟",
        top_k=3
    )

    assert result["retrieval_status"]["documents"] == "failed"
    assert result["retrieval_status"]["graph"] == "failed"
    assert result["error"] == (
        "All selected retrieval strategies failed."
    )

    print("All retrievers failure test passed.")


if __name__ == "__main__":
    test_partial_failure()
    test_all_retrievers_failure()

    print("\nAll fallback tests passed.")
