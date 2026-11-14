import sys
from pathlib import Path
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.entity_extractor import EntityExtractor


def main():

    extractor = EntityExtractor()

    sample_text = """
    شرکت آلفا محصولی به نام DocuMind توسعه داده است.
    این محصول از فناوری RAG و پایگاه داده ChromaDB
    برای جست‌وجو در اسناد استفاده می‌کند.
    """

    print("Extracting entities...\n")

    entities = extractor.extract(sample_text)

    print("Extracted Entities:")
    print("=" * 50)

    print(
        json.dumps(
            entities,
            ensure_ascii=False,
            indent=4
        )
    )

    print("\nTotal Entities:", len(entities))


if __name__ == "__main__":
    main()