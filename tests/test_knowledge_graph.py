
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.entity_extractor import EntityExtractor
from app.graph.relationship_extractor import RelationshipExtractor
from app.graph.knowledge_graph import KnowledgeGraph


def main():

    sample_text = """
    شرکت آلفا محصولی به نام DocuMind توسعه داده است.
    این محصول از فناوری RAG و پایگاه داده ChromaDB
    برای جست‌وجو در اسناد استفاده می‌کند.
    """

    # Step 1: Extract entities
    entity_extractor = EntityExtractor()
    entities = entity_extractor.extract(sample_text)

    # Step 2: Extract relationships
    relationship_extractor = RelationshipExtractor()

    relationships = relationship_extractor.extract(
        text=sample_text,
        entities=entities
    )

    # Step 3: Build knowledge graph
    knowledge_graph = KnowledgeGraph()

    graph = knowledge_graph.build(
        entities=entities,
        relationships=relationships
    )

    # Step 4: Display entities
    print("\nKnowledge Graph Entities:")
    print("=" * 50)

    print(
        json.dumps(
            knowledge_graph.get_entities(),
            ensure_ascii=False,
            indent=4
        )
    )

    # Step 5: Display relationships
    print("\nKnowledge Graph Relationships:")
    print("=" * 50)

    print(
        json.dumps(
            knowledge_graph.get_relationships(),
            ensure_ascii=False,
            indent=4
        )
    )

    # Step 6: Display statistics
    print("\nGraph Statistics:")
    print("=" * 50)

    print(
        json.dumps(
            knowledge_graph.get_statistics(),
            ensure_ascii=False,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
