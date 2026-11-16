
import os
import requests

from dotenv import load_dotenv

from app.retrieval.hybrid_graph_retriever import HybridGraphRetriever
from app.generation.hybrid_context_builder import HybridContextBuilder


class AnswerGenerator:

    def __init__(self):

        load_dotenv()

        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")

        if not self.api_token or not self.account_id:
            raise ValueError("Cloudflare credentials are missing.")

        self.model = "@cf/zai-org/glm-4.7-flash"

        self.url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Hybrid Graph RAG components
        self.hybrid_retriever = HybridGraphRetriever()
        self.context_builder = HybridContextBuilder()

    
    def generate_from_context(self, query: str, context: str) -> str:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if not context or not context.strip():
            raise ValueError("Context cannot be empty.")

        prompt = f"""
User Question:
{query}

Retrieved Context:
{context}

Instructions:
- Answer the user's question in Persian.
- Use only the information provided in the retrieved context.
- Use both document content and knowledge graph information when relevant.
- Do not invent facts, entities, or relationships.
- If the context does not contain enough information,
  clearly explain that the information is unavailable.
- Keep the answer clear, accurate, and relevant.
"""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Persian Hybrid Graph RAG assistant. "
                        "Answer only using the provided context. "
                        "Do not invent facts or sources. "
                        "Treat knowledge graph relationships as structured "
                        "context and do not add relationships that are not provided. "
                        "If the context does not contain the answer, "
                        "say that the information is unavailable."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": 512,
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

        except requests.exceptions.Timeout:
            raise TimeoutError(
                "Cloudflare API request timed out."
            )

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                f"Cloudflare API request failed: {error}"
            )

        try:
            result = response.json()

        except ValueError:
            raise RuntimeError(
                "Cloudflare returned an invalid JSON response."
            )

        if not result.get("success"):
            raise RuntimeError(
                f"Cloudflare API error: {result.get('errors')}"
            )

        choices = result.get("result", {}).get("choices", [])

        if not choices:
            raise RuntimeError(
                "No choices returned by Cloudflare."
            )

        answer = choices[0].get("message", {}).get("content")

        if not answer:
            raise RuntimeError(
                "Cloudflare returned an empty answer."
            )

        return answer.strip()


    def generate(self, query: str, top_k: int = 3) -> dict:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # Step 1: Retrieve vector and graph results
        retrieval_results = self.hybrid_retriever.retrieve(
            query=query,
            top_k=top_k
        )

        vector_results = retrieval_results["vector_results"]
        graph_results = retrieval_results["graph_results"]

        # Step 2: Check whether any relevant information was found
        if (
            not vector_results
            and not graph_results.get("entities")
            and not graph_results.get("relationships")
        ):
            return {
                "answer": "اطلاعات مرتبطی در اسناد یا گراف پیدا نشد.",
                "retrieved_documents": []
            }

        # Step 3: Build combined context
        context = self.context_builder.build(
            vector_results=vector_results,
            graph_results=graph_results
        )

        # Step 4: Build the LLM prompt
        prompt = f"""
User Question:
{query}

Retrieved Context:
{context}

Instructions:
- Answer the user's question in Persian.
- Use only the information provided in the retrieved context.
- Use both document content and knowledge graph information when relevant.
- Do not invent facts, entities, or relationships.
- If the context does not contain enough information,
  clearly explain that the information is unavailable.
- Keep the answer clear, accurate, and relevant.
"""

        # Step 5: Prepare Cloudflare request
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Persian Hybrid Graph RAG assistant. "
                        "Answer only using the provided context. "
                        "Do not invent facts or sources. "
                        "Treat knowledge graph relationships as structured "
                        "context and do not add relationships that are not provided. "
                        "If the context does not contain the answer, "
                        "say that the information is unavailable."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": 512,
            "temperature": 0.1,
            "top_p": 0.9,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }

        # Step 6: Send request to Cloudflare
        try:

            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

        except requests.exceptions.Timeout:

            raise TimeoutError(
                "Cloudflare API request timed out."
            )

        except requests.exceptions.RequestException as error:

            raise RuntimeError(
                f"Cloudflare API request failed: {error}"
            )

        # Step 7: Parse response
        try:

            result = response.json()

        except ValueError:

            raise RuntimeError(
                "Cloudflare returned an invalid JSON response."
            )

        if not result.get("success"):

            raise RuntimeError(
                f"Cloudflare API error: {result.get('errors')}"
            )

        # Step 8: Extract generated answer
        choices = result.get("result", {}).get("choices", [])

        if not choices:

            raise RuntimeError(
                "No choices returned by Cloudflare."
            )

        message = choices[0].get("message", {})
        answer = message.get("content")

        if not answer:

            raise RuntimeError(
                "Cloudflare returned an empty answer."
            )

        # Step 9: Return answer and retrieved documents
        return {
            "answer": answer.strip(),
            "retrieved_documents": vector_results
        }
