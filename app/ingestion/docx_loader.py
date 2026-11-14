from pathlib import Path
from docx import Document


class DOCXLoader:

    def load(self, file_path: str) -> list[dict]:

        documents = []

        docx_path = Path(file_path)

        # Check if file exists
        if not docx_path.exists():
            raise FileNotFoundError(
                f"DOCX file not found: {file_path}"
            )

        # Check file extension
        if docx_path.suffix.lower() != ".docx":
            raise ValueError(
                "Only DOCX files are supported."
            )

        # Open Word document
        word_document = Document(docx_path)

        # Extract non-empty paragraphs
        paragraphs = [
            paragraph.text.strip()
            for paragraph in word_document.paragraphs
            if paragraph.text.strip()
        ]

        # Combine paragraphs
        text = "\n\n".join(paragraphs)

        if text:
            documents.append({
                "text": text,
                "metadata": {
                    "source": docx_path.name,
                    "page": None,
                    "file_type": "docx"
                }
            })

        return documents