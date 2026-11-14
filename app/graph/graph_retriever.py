
import networkx as nx

from app.graph.graph_storage import GraphStorage


class GraphRetriever:

    def __init__(self):

        self.storage = GraphStorage()
        self.graph = None

        self.load_graph()

    def load_graph(self) -> None:

        if not self.storage.exists():
            self.graph = nx.DiGraph()
            return

        self.graph = self.storage.load()

    def find_entity(self, entity_name: str) -> list:

        if not entity_name or not entity_name.strip():
            return []

        query = entity_name.strip().casefold()

        matches = []

        for node, attributes in self.graph.nodes(data=True):

            name = str(node)

            if query in name.casefold():

                matches.append({
                    "name": name,
                    "type": attributes.get("entity_type"),
                    "description": attributes.get("description", "")
                })

        return matches

    def get_relationships(
        self,
        entity_name: str,
        direction: str = "both"
    ) -> list:

        if not entity_name or not entity_name.strip():
            return []

        entity = entity_name.strip()

        if not self.graph.has_node(entity):
            return []

        relationships = []

        # Outgoing relationships
        if direction in ("out", "both"):

            for _, target, attributes in self.graph.out_edges(
                entity,
                data=True
            ):

                relationships.append({
                    "source": entity,
                    "target": target,
                    "relation": attributes.get("relation"),
                    "description": attributes.get("description", "")
                })

        # Incoming relationships
        if direction in ("in", "both"):

            for source, _, attributes in self.graph.in_edges(
                entity,
                data=True
            ):

                relationships.append({
                    "source": source,
                    "target": entity,
                    "relation": attributes.get("relation"),
                    "description": attributes.get("description", "")
                })

        return relationships

    def search(
        self,
        entity_name: str,
        direction: str = "both"
    ) -> dict:

        entities = self.find_entity(entity_name)

        relationships = []

        for entity in entities:

            relationships.extend(
                self.get_relationships(
                    entity_name=entity["name"],
                    direction=direction
                )
            )

        return {
            "query": entity_name,
            "entities": entities,
            "relationships": relationships
        }

    def get_neighbors(self, entity_name: str) -> list:

        if not self.graph.has_node(entity_name):
            return []

        neighbors = set(self.graph.successors(entity_name))
        neighbors.update(self.graph.predecessors(entity_name))

        return list(neighbors)
