
from pathlib import Path


class TXTLoader:

    def load(self, file_path: str) -> list[dict]:

        documents = []

        txt_path = Path(file_path)

        if not txt_path.exists():
            raise FileNotFoundError(
                f"TXT file not found: {file_path}"
            )

        if txt_path.suffix.lower() != ".txt":
            raise ValueError(
                "Only TXT files are supported."
            )

        text = txt_path.read_text(
            encoding="utf-8"
        ).strip()

        if text:
            documents.append({
                "text": text,
                "metadata": {
                    "source": txt_path.name,
                    "page": None,
                    "file_type": "txt"
                }
            })

        return documents
