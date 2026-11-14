
import networkx as nx


class KnowledgeGraph:

    def __init__(self):

        # Create a directed graph
        self.graph = nx.DiGraph()

    def add_entities(self, entities: list) -> None:

        for entity in entities:

            name = entity.get("name")
            entity_type = entity.get("type")
            description = entity.get("description", "")

            if not name or not entity_type:
                continue

            self.graph.add_node(
                name,
                entity_type=entity_type,
                description=description
            )

    def add_relationships(self, relationships: list) -> None:

        for relationship in relationships:

            source = relationship.get("source")
            target = relationship.get("target")
            relation = relationship.get("relation")
            description = relationship.get("description", "")

            if not all([source, target, relation]):
                continue

            # Only connect existing nodes
            if not self.graph.has_node(source):
                continue

            if not self.graph.has_node(target):
                continue

            self.graph.add_edge(
                source,
                target,
                relation=relation,
                description=description
            )

    def build(
        self,
        entities: list,
        relationships: list
    ) -> nx.DiGraph:

        self.graph.clear()

        self.add_entities(entities)
        self.add_relationships(relationships)

        return self.graph

    def get_entities(self) -> list:

        entities = []

        for node, attributes in self.graph.nodes(data=True):

            entities.append({
                "name": node,
                "type": attributes.get("entity_type"),
                "description": attributes.get("description", "")
            })

        return entities

    def get_relationships(self) -> list:

        relationships = []

        for source, target, attributes in self.graph.edges(data=True):

            relationships.append({
                "source": source,
                "target": target,
                "relation": attributes.get("relation"),
                "description": attributes.get("description", "")
            })

        return relationships

    def get_statistics(self) -> dict:

        return {
            "total_entities": self.graph.number_of_nodes(),
            "total_relationships": self.graph.number_of_edges(),
            "is_directed": self.graph.is_directed(),
            "is_empty": self.graph.number_of_nodes() == 0
        }
