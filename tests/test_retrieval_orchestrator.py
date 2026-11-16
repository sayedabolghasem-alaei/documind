from app.agent.orchestration.retrieval_orchestrator import (
    RetrievalOrchestrator
)


def test_retrieval_orchestrator():

    orchestrator = RetrievalOrchestrator()

    test_queries = [
        "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟",
        "ارتباط بین محصول A و محصول B چیست؟",
        "همسایه‌های محصول A کدام‌اند؟"
    ]

    for query in test_queries:

        print("\n" + "=" * 70)
        print("QUERY:", query)

        result = orchestrator.retrieve(
            query=query,
            top_k=3
        )

        print("\nStrategy:")
        print(result["strategy"])

        print("\nRetrieval Status:")
        print(result["retrieval_status"])

        print("\nRetrieval Errors:")
        print(result["retrieval_errors"])

        print("\nDocument Results:")
        print(len(result["vector_results"]))

        print("\nGraph Entities:")
        print(
            len(result["graph_results"]["entities"])
        )

        print("\nGraph Relationships:")
        print(
            len(result["graph_results"]["relationships"])
        )

        print("\nGeneral Error:")
        print(result["error"])

    print("\nOrchestration test completed.")


if __name__ == "__main__":
    test_retrieval_orchestrator()