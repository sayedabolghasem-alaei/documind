
from app.agent.state import AgentState
from app.retrieval.hybrid_graph_retriever import HybridGraphRetriever


# Initialize retriever once
retriever = HybridGraphRetriever()


def retrieval_node(state: AgentState) -> dict:

    query = state.get("active_query", "").strip()

    if not query:
        return {
            "error": "Active query cannot be empty."
        }

    try:
        results = retriever.retrieve(
            query=query,
            top_k=3
        )

        return {
            "vector_results": results["vector_results"],
            "graph_results": results["graph_results"],
            "retrieval_attempts": state.get("retrieval_attempts", 0) + 1,
            "error": ""
        }

    except Exception as error:
        return {
            "error": str(error)
        }
