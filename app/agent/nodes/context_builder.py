
from app.agent.state import AgentState
from app.generation.hybrid_context_builder import HybridContextBuilder


context_builder = HybridContextBuilder()


def context_builder_node(state: AgentState) -> dict:

    vector_results = state.get("vector_results", [])
    graph_results = state.get("graph_results", {})

    try:
        context = context_builder.build(
            vector_results=vector_results,
            graph_results=graph_results
        )

        return {
            "context": context,
            "error": ""
        }

    except Exception as error:
        return {
            "error": str(error)
        }
