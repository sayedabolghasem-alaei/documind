
import os
import requests

from dotenv import load_dotenv
from app.agent.state import AgentState


class QueryRewriter:

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

    def rewrite(self, query: str, context: str = "") -> str:

        prompt = f"""
Original Question:
{query}

Previous Retrieved Context:
{context}

Task:
Rewrite the original question to improve document retrieval.

Rules:
- Preserve the original meaning and intent.
- Make the question clearer and more specific.
- Use relevant keywords when appropriate.
- Do not answer the question.
- Return only the rewritten question.
- Write in the same language as the original question.
"""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a query rewriting assistant. "
                        "Your task is to improve search queries "
                        "without changing their original meaning."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": 256,
            "temperature": 0.1,
            "top_p": 0.9,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }

        try:
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

            rewritten_query = (
                choices[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

            if not rewritten_query:
                raise RuntimeError("Rewritten query is empty.")

            return rewritten_query

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                f"Query rewriting request failed: {error}"
            )


query_rewriter = QueryRewriter()


def query_rewriter_node(state: AgentState) -> dict:

    query = state.get("active_query", "").strip()
    context = state.get("context", "")

    if not query:
        return {
            "error": "Active query cannot be empty."
        }

    try:
        rewritten_query = query_rewriter.rewrite(
            query=query,
            context=context
        )

        return {
            "active_query": rewritten_query,
            "context": "",
            "vector_results": [],
            "graph_results": {},
            "is_relevant": False,
            "error": ""
        }

    except Exception as error:
        return {
            "error": str(error)
        }
