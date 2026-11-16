from typing import TypedDict


class AgentState(TypedDict, total=False):

    # User input
    query: str

    # Query processing
    active_query: str
    retrieval_attempts: int

    # Retrieval strategy
    retrieval_strategy: str

    # Retrieval results
    vector_results: list[dict]
    graph_results: dict

    # Retrieval monitoring
    retrieval_status: dict
    retrieval_errors: dict

    # Context evaluation
    context: str
    is_relevant: bool

    # Final response
    answer: str
    error: str