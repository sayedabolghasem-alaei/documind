
from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState

from app.agent.nodes.query_analyzer import query_analyzer
from app.agent.nodes.retrieval import retrieval_node
from app.agent.nodes.context_grader import context_grader_node
from app.agent.nodes.context_builder import context_builder_node
from app.agent.nodes.answer_generator import answer_generator_node
from app.agent.nodes.query_rewriter import query_rewriter_node
from app.agent.nodes.no_context import no_context_node

from app.agent.edges import (
    route_after_analysis,
    route_after_grading,
    route_after_rewriting,
    route_after_context_building
)


def build_agent():

    # Initialize StateGraph
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("context_grader", context_grader_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("answer_generator", answer_generator_node)
    workflow.add_node("query_rewriter", query_rewriter_node)
    workflow.add_node("no_context", no_context_node)

    # Starting point
    workflow.add_edge(START, "query_analyzer")

    # Query Analyzer routing
    workflow.add_conditional_edges(
        "query_analyzer",
        route_after_analysis,
        {
            "retrieve": "retrieval",
            "no_context": "no_context"
        }
    )

    # Retrieval pipeline
    workflow.add_edge("retrieval", "context_grader")

    # Context Grader routing
    workflow.add_conditional_edges(
        "context_grader",
        route_after_grading,
        {
            "build_context": "context_builder",
            "rewrite_query": "query_rewriter",
            "no_context": "no_context"
        }
    )

    # Query Rewriter routing
    workflow.add_conditional_edges(
        "query_rewriter",
        route_after_rewriting,
        {
            "retrieve": "retrieval",
            "no_context": "no_context"
        }
    )

    # Context Builder routing
    workflow.add_conditional_edges(
        "context_builder",
        route_after_context_building,
        {
            "generate_answer": "answer_generator",
            "no_context": "no_context"
        }
    )

    # Final nodes
    workflow.add_edge("answer_generator", END)
    workflow.add_edge("no_context", END)

    # Compile graph
    return workflow.compile()


# Compiled Agent
agent = build_agent()
