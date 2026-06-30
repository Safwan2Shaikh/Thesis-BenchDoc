import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_path_resolution_prefers_existing_dirs():
    from thesis.infra.paths import knowledge_base_dir, processed_dir

    assert knowledge_base_dir().exists()
    assert processed_dir().exists()


def test_build_pdu_service_from_graph(tmp_path):
    from thesis.workflows.health_check_workflow import build_pdu_service

    graph = tmp_path / "graph.yaml"
    graph.write_text(
        "edges:\n"
        "  - source: pdu.port_8\n"
        "    relation: powers\n"
        "    target: lauterbach\n",
        encoding="utf-8",
    )

    service = build_pdu_service(
        graph_file=str(graph),
        exe_path="dummy.exe",
        config_file="dummy.yaml",
    )

    assert service.mapping["lauterbach"] == 8
