import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_retrievers_read_new_knowledge_base():
    from thesis.intelligence.retrieval.inventory_retriever import get_bench_inventory
    from thesis.intelligence.retrieval.bench_retriever import identify_bench

    bench = identify_bench("ABT-C-00483")
    assert bench is not None

    inventory = get_bench_inventory(bench["bench_name"])
    assert inventory is not None


def test_diagnose_run_with_monkeypatch(monkeypatch):
    from thesis.workflows import diagnose_workflow
    from thesis.intelligence.orchestrator import chat_service

    monkeypatch.setattr(
        chat_service,
        "identify_bench",
        lambda q: {"bench_name": "ABT-C-00483", "ip": "10.10.10.10"},
    )
    monkeypatch.setattr(chat_service, "get_bench_inventory", lambda b: {"psu": "EA-PS", "vector1": "VN5650", "pdu": "PDU"})
    monkeypatch.setattr(chat_service, "identify_devices", lambda q, i: {"bench_devices": ["PSU"], "query_devices": ["PSU"], "valid_devices": ["PSU"], "invalid_devices": []})
    monkeypatch.setattr(chat_service, "retrieve_context", lambda user_query, bench: {"inventory": {}, "similar_issues": [], "knowledge_chunks": [], "bench_topology": {}, "trace32_advice": None})
    monkeypatch.setattr(chat_service, "run_diagnostic", lambda **kwargs: "ok-diagnosis")

    out = diagnose_workflow.run("psu issue on ABT-C-00483")
    assert out == "ok-diagnosis"
