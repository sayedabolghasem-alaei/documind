
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

    Extraction rules:

    1. Extract only entities explicitly mentioned in the text.
    2. Never invent entities.
    3. Keep entity names in their original language.
    4. Avoid extracting ordinary or generic words.
    5. Never expand or modify an entity name.
    6. Never append surrounding words to an entity name.
    7. Do not create entities by repeatedly extending another entity.
    8. Each entity must be an independent and meaningful entity.
    9. Do not extract the same entity more than once.
    10. Return at most 8 entities.
    11. Prioritize the most important entities.
    12. Never repeat an entity.
    13. Keep descriptions short and based only on the provided text.
    14. If no entities exist, return an empty entities array.

    Output requirements:

    - Return valid JSON only.
    - Do not include explanations.
    - Do not use Markdown code fences.
    - Do not include text before or after the JSON.
    - Use only the entity types listed above.

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

    If no entities are found, return:

    {{"entities": []}}

    TEXT:
    {text}
"""


    def _split_text(
        self,
        text: str,
        chunk_size: int = 3000,
        overlap: int = 200
    ) -> list:

        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - overlap

        return chunks


    def _parse_response(self, content: str) -> list:

        if not content or not content.strip():
            raise RuntimeError("Model returned empty content.")

        content = content.strip()

        # Remove Markdown code fences
        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        try:
            data = json.loads(content)

        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Invalid JSON returned by the model: {error}. "
                f"Response preview: {content[:500]}"
            ) from error

        if isinstance(data, dict):
            entities = data.get("entities", [])
        elif isinstance(data, list):
            entities = data
        else:
            raise RuntimeError("Unexpected JSON response format.")

        if not isinstance(entities, list):
            raise RuntimeError("'entities' must be a list.")

        valid_types = {
            "PERSON",
            "ORGANIZATION",
            "LOCATION",
            "PRODUCT",
            "EVENT",
            "DATE",
            "OTHER"
        }

        unique_entities = []
        seen = set()

        for entity in entities:

            if not isinstance(entity, dict):
                continue

            name = entity.get("name")
            entity_type = entity.get("type")
            description = entity.get("description", "")

            if not isinstance(name, str) or not name.strip():
                continue

            if not isinstance(entity_type, str):
                continue

            entity_type = entity_type.upper().strip()

            if entity_type not in valid_types:
                continue

            name = name.strip()
            key = (name.casefold(), entity_type)

            if key in seen:
                continue

            seen.add(key)

            unique_entities.append({
                "name": name,
                "type": entity_type,
                "description": (
                    description.strip()
                    if isinstance(description, str)
                    else ""
                )
            })

        return unique_entities



    def extract(self, text: str) -> list:

        if not text or not text.strip():
            return []

        chunks = self._split_text(
            text,
            chunk_size=4000,
            overlap=200
        )

        all_entities = []

        for index, chunk in enumerate(chunks, start=1):

            if not chunk.strip():
                continue

            prompt = self._build_prompt(chunk)

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

            result = None

            for attempt in range(3):

                try:
                    response = requests.post(
                        self.url,
                        headers=self.headers,
                        json=payload,
                        timeout=(15, 90)
                    )

                    response.raise_for_status()
                    result = response.json()
                    break

                except requests.exceptions.RequestException as error:

                    if attempt == 2:
                        raise RuntimeError(
                            f"Entity extraction failed on chunk "
                            f"{index}/{len(chunks)}: {error}"
                        ) from error

                    import time
                    time.sleep(2 * (attempt + 1))

                except ValueError as error:

                    raise RuntimeError(
                        "Cloudflare returned invalid JSON."
                    ) from error

            if not result or not result.get("success"):
                raise RuntimeError(
                    f"Cloudflare API error on chunk {index}: "
                    f"{result.get('errors') if result else 'Empty response'}"
                )

            choices = result.get("result", {}).get("choices", [])

            if not choices:
                raise RuntimeError(
                    f"No choices returned for chunk {index}."
                )

            content = (
                choices[0]
                .get("message", {})
                .get("content")
            )

            if not content:
                raise RuntimeError(
                    f"Empty response content for chunk {index}."
                )

            print("\n========== ENTITY EXTRACTION DEBUG ==========")
            print(f"Chunk: {index}/{len(chunks)}")
            print(f"Response content: {repr(content)}")
            print("==============================================\n")

            entities = self._parse_response(content)
            all_entities.extend(entities)

        unique_entities = []
        seen_entities = set()

        for entity in all_entities:

            key = (
                entity["name"].casefold(),
                entity["type"]
            )

            if key not in seen_entities:
                seen_entities.add(key)
                unique_entities.append(entity)

        return unique_entities
