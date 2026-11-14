
import os
import json
import requests

from dotenv import load_dotenv


class EntityExtractor:

    def __init__(self):

        load_dotenv()

        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")

        if not self.api_token or not self.account_id:
            raise ValueError(
                "Cloudflare credentials are missing."
            )

        self.model = "@cf/zai-org/glm-4.7-flash"

        self.url = (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _build_prompt(self, text: str) -> str:

        return f"""
Extract named entities from the following text.

Entity types:
- PERSON
- ORGANIZATION
- PRODUCT
- LOCATION
- TECHNOLOGY
- CONCEPT

Rules:
1. Extract only entities explicitly mentioned in the text.
2. Do not invent entities.
3. Keep entity names in their original language.
4. Avoid extracting ordinary words as entities.
5. Return valid JSON only.
6. If no entities exist, return an empty list.

Required JSON format:

{{
    "entities": [
        {{
            "name": "Entity name",
            "type": "ENTITY_TYPE",
            "description": "Short description based only on the text"
        }}
    ]
}}

TEXT:
{text}
"""

    def _parse_response(self, content: str) -> list:

        content = content.strip()

        # Remove Markdown code fences if present
        if content.startswith("```"):
            lines = content.splitlines()

            if lines[-1].strip() == "```":
                lines = lines[1:-1]

            content = "\n".join(lines)

            if content.startswith("json"):
                content = content[4:].strip()

        try:
            data = json.loads(content)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON returned by the model: {error}"
            )

        entities = data.get("entities", [])

        if not isinstance(entities, list):
            raise ValueError(
                "Invalid entities format returned by the model."
            )

        valid_entities = []
        seen_entities = set()

        allowed_types = {
            "PERSON",
            "ORGANIZATION",
            "PRODUCT",
            "LOCATION",
            "TECHNOLOGY",
            "CONCEPT"
        }

        for entity in entities:

            if not isinstance(entity, dict):
                continue

            name = entity.get("name")
            entity_type = entity.get("type")
            description = entity.get("description", "")

            if not isinstance(name, str) or not name.strip():
                continue

            if entity_type not in allowed_types:
                continue

            unique_key = (
                name.strip().casefold(),
                entity_type
            )

            if unique_key in seen_entities:
                continue

            seen_entities.add(unique_key)

            valid_entities.append({
                "name": name.strip(),
                "type": entity_type,
                "description": (
                    description.strip()
                    if isinstance(description, str)
                    else ""
                )
            })

        return valid_entities

    def extract(self, text: str) -> list:

        if not text or not text.strip():
            return []

        prompt = self._build_prompt(text)

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an information extraction system. "
                        "Extract only explicitly stated information. "
                        "Always return valid JSON."
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
                "Entity extraction request timed out."
            )

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                f"Entity extraction request failed: {error}"
            )

        try:
            result = response.json()

        except ValueError:
            raise RuntimeError(
                "Cloudflare returned invalid JSON."
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

        content = (
            choices[0]
            .get("message", {})
            .get("content")
        )

        if not content:
            raise RuntimeError(
                "Cloudflare returned empty content."
            )

        return self._parse_response(content)
