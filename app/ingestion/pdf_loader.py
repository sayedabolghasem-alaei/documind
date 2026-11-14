
import fitz
from pathlib import Path


class PDFLoader:

    def load(self, file_path: str) -> list[dict]:

        documents = []

        pdf_path = Path(file_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        with fitz.open(pdf_path) as pdf:

            for page_number, page in enumerate(pdf, start=1):

                # Extract text using block information
                blocks = page.get_text("blocks")

                page_blocks = []

                for block in blocks:

                    x0, y0, x1, y1, text = block[:5]

                    text = text.strip()

                    if not text:
                        continue

                    page_blocks.append({
                        "text": text,
                        "x": x0,
                        "y": y0
                    })

                # Sort blocks from top to bottom
                # Preserve the internal text order of each block
                page_blocks.sort(
                    key=lambda block: (
                        round(block["y"], 1),
                        block["x"]
                    )
                )

                page_text = "\n".join(
                    block["text"]
                    for block in page_blocks
                ).strip()

                if not page_text:
                    continue

                documents.append({
                    "text": page_text,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_number,
                        "file_type": "pdf"
                    }
                })

        return documents
