
from app.agent.state import AgentState


def query_analyzer(state: AgentState) -> dict:

    query = state.get("query", "").strip()

    if not query:
        return {
            "error": "Query cannot be empty."
        }

    return {
        "active_query": query,
        "retrieval_attempts": 0,
        "error": ""
    }
