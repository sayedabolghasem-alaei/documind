
from app.agent.state import AgentState


MAX_RETRIEVAL_ATTEMPTS = 2


def route_after_analysis(state: AgentState) -> str:
    if state.get("error"):
        return "no_context"

    return "retrieve"


def route_after_grading(state: AgentState) -> str:

    if state.get("error"):
        return "no_context"

    if state.get("is_relevant", False):
        return "build_context"

    attempts = state.get("retrieval_attempts", 0)

    if attempts < MAX_RETRIEVAL_ATTEMPTS:
        return "rewrite_query"

    return "no_context"


def route_after_rewriting(state: AgentState) -> str:
    if state.get("error"):
        return "no_context"

    return "retrieve"


def route_after_context_building(state: AgentState) -> str:
    if state.get("error"):
        return "no_context"

    if not state.get("context", "").strip():
        return "no_context"

    return "generate_answer"
