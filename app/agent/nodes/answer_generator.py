
from app.agent.state import AgentState
from app.generation.answer_generator import AnswerGenerator


# Initialize the generator once
answer_generator = AnswerGenerator()


def answer_generator_node(state: AgentState) -> dict:

    query = state.get("query", "").strip()
    context = state.get("context", "").strip()

    if not query:
        return {
            "error": "Query cannot be empty."
        }

    if not context:
        return {
            "error": "Context cannot be empty."
        }

    try:
        answer = answer_generator.generate_from_context(
            query=query,
            context=context
        )

        return {
            "answer": answer,
            "error": ""
        }

    except Exception as error:
        return {
            "error": str(error)
        }
