
import os
import json
import requests

from dotenv import load_dotenv


class RelationshipExtractor:

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

    def _build_prompt(self, text: str, entities: list) -> str:

        return f"""
Extract relationships between the provided entities
from the given text.

TEXT:
{text}

ENTITIES:
{json.dumps(entities, ensure_ascii=False)}

Return ONLY valid JSON in this format:

{{
    "relationships": [
        {{
            "source": "Entity A",
            "target": "Entity B",
            "relation": "RELATION_TYPE",
            "description": "Short explanation"
        }}
    ]
}}

Rules:
1. Use only the provided entities.
2. Extract only relationships supported by the text.
3. Do not invent relationships.
4. Use short uppercase relation names.
5. Avoid duplicate relationships.
6. If no relationship exists, return an empty list.
"""

    def _parse_response(self, content: str) -> list:

        content = content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[1]

            if content.endswith("```"):
                content = content[:-3]

        try:
            data = json.loads(content.strip())

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid relationship JSON: {error}"
            )

        relationships = data.get("relationships")

        if not isinstance(relationships, list):
            raise ValueError(
                "Invalid relationships format."
            )

        valid_relationships = []
        seen = set()

        for item in relationships:

            if not isinstance(item, dict):
                continue

            source = item.get("source")
            target = item.get("target")
            relation = item.get("relation")
            description = item.get("description", "")

            if not all([
                isinstance(source, str),
                isinstance(target, str),
                isinstance(relation, str)
            ]):
                continue

            if not source.strip() or not target.strip():
                continue

            if not relation.strip():
                continue

            key = (
                source.casefold(),
                target.casefold(),
                relation.upper()
            )

            if key in seen:
                continue

            seen.add(key)

            valid_relationships.append({
                "source": source.strip(),
                "target": target.strip(),
                "relation": relation.strip().upper(),
                "description": (
                    description.strip()
                    if isinstance(description, str)
                    else ""
                )
            })

        return valid_relationships

    def extract(self, text: str, entities: list) -> list:

        if not text.strip():
            raise ValueError("Text cannot be empty.")

        if not entities:
            return []

        prompt = self._build_prompt(
            text=text,
            entities=entities
        )

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a knowledge graph relationship "
                        "extraction assistant. Extract only "
                        "relationships explicitly supported "
                        "by the provided text."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": 1024,
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

        message = choices[0].get("message", {})
        content = message.get("content")

        if not content:
            raise RuntimeError(
                "Cloudflare returned an empty response."
            )

        return self._parse_response(content)
