from pathlib import Path
import yaml
from thesis.infra.paths import knowledge_base_dir


class BenchTopology:
    def __init__(self, graph_file: str = None):
        if graph_file is None:
            graph_file = str(
                knowledge_base_dir()
                / "Bench_Config"
                / "ABT-C-0047D"
                / "graph_trail.yaml"
            )
        self.graph_file = Path(graph_file)
        self.graph = self._load_graph()

    def _load_graph(self):
        with open(self.graph_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get_pdu_mapping(self) -> dict:
        mapping = {}

        for edge in self.graph.get("edges", []):

            source = edge.get("source", "")
            relation = edge.get("relation", "")
            target = edge.get("target", "")

            if relation != "powers":
                continue

            if not source.startswith("pdu.port_"):
                continue

            socket_num = int(source.split("_")[-1])

            mapping[target.lower()] = socket_num

        return mapping