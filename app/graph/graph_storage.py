
import json
from pathlib import Path

import networkx as nx


class GraphStorage:

    def __init__(self, storage_path: str = "data/graph/knowledge_graph.json"):

        self.storage_path = Path(storage_path)

        # Ensure storage directory exists
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, graph: nx.DiGraph) -> None:

        if not isinstance(graph, nx.DiGraph):
            raise TypeError(
                "Expected a NetworkX directed graph."
            )

        graph_data = nx.node_link_data(
            graph,
            edges="edges"
        )

        with self.storage_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                graph_data,
                file,
                ensure_ascii=False,
                indent=4
            )

    def load(self) -> nx.DiGraph:

        if not self.storage_path.exists():
            raise FileNotFoundError(
                f"Graph file not found: {self.storage_path}"
            )

        with self.storage_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            graph_data = json.load(file)

        graph = nx.node_link_graph(
            graph_data,
            directed=True,
            edges="edges"
        )

        return graph

    def exists(self) -> bool:

        return self.storage_path.exists()

    def delete(self) -> bool:

        if not self.storage_path.exists():
            return False

        self.storage_path.unlink()

        return True
