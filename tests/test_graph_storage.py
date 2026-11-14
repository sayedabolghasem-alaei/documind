
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.entity_extractor import EntityExtractor
from app.graph.relationship_extractor import RelationshipExtractor
from app.graph.knowledge_graph import KnowledgeGraph
from app.graph.graph_storage import GraphStorage


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

    # Step 4: Initialize graph storage
    storage = GraphStorage()

    # Step 5: Save graph
    storage.save(graph)

    print("Graph saved successfully!")
    print("File exists:", storage.exists())
    print("File path:", storage.storage_path)

    # Step 6: Load graph
    loaded_graph = storage.load()

    print("\nLoaded Graph Statistics:")
    print("=" * 50)

    print(
        json.dumps(
            {
                "total_entities": loaded_graph.number_of_nodes(),
                "total_relationships": loaded_graph.number_of_edges(),
                "is_directed": loaded_graph.is_directed()
            },
            indent=4
        )
    )

    # Step 7: Display loaded relationships
    print("\nLoaded Relationships:")
    print("=" * 50)

    for source, target, attributes in loaded_graph.edges(data=True):

        print(
            f"{source} --{attributes['relation']}--> {target}"
        )


if __name__ == "__main__":
    main()
