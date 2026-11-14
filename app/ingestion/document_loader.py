from pathlib import Path

from app.ingestion.pdf_loader import PDFLoader
from app.ingestion.txt_loader import TXTLoader
from app.ingestion.docx_loader import DOCXLoader


class DocumentLoader:

    def __init__(self):

        self.loaders = {
            ".pdf": PDFLoader(),
            ".txt": TXTLoader(),
            ".docx": DOCXLoader()
        }

    def load(self, file_path: str) -> list[dict]:

        file_extension = Path(file_path).suffix.lower()

        loader = self.loaders.get(file_extension)

        if loader is None:
            raise ValueError(
                f"Unsupported file format: {file_extension}"
            )

        return loader.load(file_path)