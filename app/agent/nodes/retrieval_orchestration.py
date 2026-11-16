from app.agent.state import AgentState
from app.agent.orchestration.retrieval_orchestrator import (
    RetrievalOrchestrator
)


# Initialize orchestrator once
retrieval_orchestrator = RetrievalOrchestrator()


def retrieval_orchestration_node(
    state: AgentState
) -> dict:

    query = state.get("active_query", "").strip()

    if not query:
        return {
            "error": "Active query cannot be empty."
        }

    try:

        results = retrieval_orchestrator.retrieve(
            query=query,
            top_k=3
        )

        return {
            "vector_results": results["vector_results"],
            "graph_results": results["graph_results"],
            "retrieval_strategy": results["strategy"],
            "retrieval_status": results["retrieval_status"],
            "retrieval_errors": results["retrieval_errors"],
            "retrieval_attempts": (
                state.get("retrieval_attempts", 0) + 1
            ),
            "error": results["error"]
        }

    except Exception as error:

        return {
            "error": f"Retrieval orchestration failed: {error}"
        }