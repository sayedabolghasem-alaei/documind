
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.pdf_loader import PDFLoader
from app.ingestion.sentence_chunker import SentenceChunker


PDF_PATH = "data/uploads/sample.pdf"


def main():

    loader = PDFLoader()
    chunker = SentenceChunker(
        chunk_size=5,
        chunk_overlap=1
    )

    # Extract PDF pages
    documents = loader.load(PDF_PATH)

    # Generate chunks
    chunks = chunker.chunk_documents(documents)

    print(f"\nTotal pages: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):

        print("\n" + "=" * 70)
        print(f"CHUNK {index}")
        print(f"Metadata: {chunk['metadata']}")
        print("-" * 70)
        print(chunk["text"])


if __name__ == "__main__":
    main()
