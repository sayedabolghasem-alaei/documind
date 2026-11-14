
import sys
from pathlib import Path
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.entity_extractor import EntityExtractor
from app.graph.relationship_extractor import RelationshipExtractor


def main():

    sample_text = """
    شرکت آلفا محصولی به نام DocuMind توسعه داده است.
    این محصول از فناوری RAG و پایگاه داده ChromaDB
    برای جست‌وجو در اسناد استفاده می‌کند.
    """

    # Step 1: Extract entities
    entity_extractor = EntityExtractor()

    entities = entity_extractor.extract(sample_text)

    print("Extracted Entities:")
    print("=" * 50)

    print(
        json.dumps(
            entities,
            ensure_ascii=False,
            indent=4
        )
    )

    # Step 2: Extract relationships
    relationship_extractor = RelationshipExtractor()

    relationships = relationship_extractor.extract(
        text=sample_text,
        entities=entities
    )

    print("\nExtracted Relationships:")
    print("=" * 50)

    print(
        json.dumps(
            relationships,
            ensure_ascii=False,
            indent=4
        )
    )

    print("\nTotal Relationships:", len(relationships))


if __name__ == "__main__":
    main()
