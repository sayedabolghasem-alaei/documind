
import os
import requests

from dotenv import load_dotenv
from app.agent.state import AgentState


class ContextGrader:

    def __init__(self):

        load_dotenv()

        api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")

        if not api_token or not account_id:
            raise ValueError("Cloudflare credentials are missing.")

        model = "@cf/zai-org/glm-4.7-flash"

        self.url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{account_id}/ai/run/{model}"
        )

        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def grade(self, query: str, context: str) -> bool:

        prompt = f"""
User Question:
{query}

Retrieved Context:
{context}

Task:
Determine whether the retrieved context contains useful
information that directly helps answer the user's question.

Rules:
- Return YES if the context contains relevant information.
- Return NO if the context is unrelated or insufficient.
- Do not answer the user's question.
- Return only YES or NO.
"""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a relevance evaluator for a RAG system. "
                        "Evaluate the semantic relevance of retrieved "
                        "context to the user's question."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": 16,
            "temperature": 0.0,
            "top_p": 0.9,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("success"):
            raise RuntimeError(
                f"Cloudflare API error: {result.get('errors')}"
            )

        choices = result.get("result", {}).get("choices", [])

        if not choices:
            raise RuntimeError("No choices returned by Cloudflare.")

        evaluation = (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
            .upper()
        )

        if evaluation.startswith("YES"):
            return True

        if evaluation.startswith("NO"):
            return False

        raise RuntimeError(
            f"Unexpected grader response: {evaluation}"
        )


context_grader = ContextGrader()


def context_grader_node(state: AgentState) -> dict:

    query = state.get("active_query") or state.get("query", "")
    vector_results = state.get("vector_results", [])
    graph_results = state.get("graph_results", {})

    context_parts = []

    for document in vector_results:
        text = document.get("text", "").strip()

        if text:
            context_parts.append(text)

    for entity in graph_results.get("entities", []):
        context_parts.append(str(entity))

    for relationship in graph_results.get("relationships", []):
        context_parts.append(str(relationship))

    context = "\n\n".join(context_parts)

    if not query.strip() or not context.strip():
        return {"is_relevant": False, "error": ""}

    try:
        is_relevant = context_grader.grade(
            query=query,
            context=context
        )

        return {
            "is_relevant": is_relevant,
            "error": ""
        }

    except Exception as error:
        return {
            "error": f"Context grading failed: {error}"
        }
