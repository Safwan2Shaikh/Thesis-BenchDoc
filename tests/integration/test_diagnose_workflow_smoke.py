import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_diagnose_workflow_with_patched_dependencies(monkeypatch):
    from thesis.intelligence.orchestrator import chat_service
    from thesis.workflows.diagnose_workflow import run

    monkeypatch.setattr(
        chat_service,
        "identify_bench",
        lambda q: {"bench_name": "ABT-C-00483", "ip": "10.10.10.10"},
    )
    monkeypatch.setattr(
        chat_service,
        "get_bench_inventory",
        lambda b: {"psu": "EA-PS", "vector1": "VN5650", "pdu": "PDU", "relay": "Relay", "lauterbach1": "Trace32"},
    )
    monkeypatch.setattr(
        chat_service,
        "identify_devices",
        lambda q, i: {
            "bench_devices": ["PSU", "Vector", "PDU", "Relay", "Trace32"],
            "query_devices": ["Vector"],
            "valid_devices": ["Vector"],
            "invalid_devices": [],
        },
    )
    monkeypatch.setattr(
        chat_service,
        "retrieve_context",
        lambda user_query, bench: {"inventory": {}, "similar_issues": [], "knowledge_chunks": [], "bench_topology": {}, "trace32_advice": None},
    )
    monkeypatch.setattr(
        chat_service,
        "run_diagnostic",
        lambda **kwargs: "mock diagnosis response",
    )

    result = run("vector not responding on ABT-C-00483")
    assert "mock diagnosis response" in result
