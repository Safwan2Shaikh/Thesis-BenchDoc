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


def test_bench_config_folders_are_discovered():
    from thesis.intelligence.retrieval.bench_topology_retriever import (
        get_bench_context,
        list_bench_configs,
    )

    configs = list_bench_configs()

    assert "ABT-C-0047D" in configs
    assert "ABT-C-003WE" in configs
    assert "RNG-C-0050F" in configs

    context = get_bench_context("ecu not reachable", bench="ABT-C-003WE")

    assert context["bench_id"] == "ABT-C-003WE"
    assert context["bench_info"]["devices"]["ecu_2"]["status"] == "expected_but_not_connected"


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


def test_diagnose_run_uses_selected_bench(monkeypatch):
    from thesis.workflows import diagnose_workflow
    from thesis.intelligence.orchestrator import chat_service

    captured = {}

    monkeypatch.setattr(chat_service, "get_bench_inventory", lambda b: {"psu": "Toellner", "lauterbach1": "Lauterbach"})
    monkeypatch.setattr(chat_service, "identify_devices", lambda q, i: {"bench_devices": ["PSU"], "query_devices": ["PSU"], "valid_devices": ["PSU"], "invalid_devices": []})

    def fake_retrieve_context(user_query, bench):
        captured["bench"] = bench
        return {"inventory": {}, "similar_issues": [], "knowledge_chunks": [], "bench_topology": {}, "trace32_advice": None}

    monkeypatch.setattr(chat_service, "retrieve_context", fake_retrieve_context)
    monkeypatch.setattr(chat_service, "run_diagnostic", lambda **kwargs: kwargs["bench"])

    out = diagnose_workflow.run("psu issue", selected_bench="RNG-C-0050F")

    assert out == "RNG-C-0050F"
    assert captured["bench"] == "RNG-C-0050F"


def test_diagnostic_execution_trace_includes_retrievers(monkeypatch):
    from thesis.intelligence.orchestrator import diagnostic_engine

    class FakeLLMClient:
        def ask(self, messages):
            return {
                "reply": "diagnostic-body",
                "tokens": 12,
            }

    monkeypatch.setattr(
        diagnostic_engine,
        "_get_llm_client",
        lambda: FakeLLMClient(),
    )

    result = diagnostic_engine.run_diagnostic(
        user_input="trace32 issue on ABT-C-00483",
        bench="ABT-C-00483",
        device_result={
            "bench_devices": ["Trace32", "PSU"],
            "query_devices": ["Trace32"],
            "valid_devices": ["Trace32"],
            "invalid_devices": [],
        },
        retrieval_context={
            "inventory": {"psu": "EA-PS"},
            "similar_issues": [],
            "knowledge_chunks": [],
            "bench_topology": {},
            "trace32_advice": None,
            "metadata": {
                "sources": {
                    "knowledge_base_dir": "data/knowledge_base",
                    "processed_dir": "data/processed",
                },
                "retrievers": {
                    "inventory": {
                        "status": "used",
                        "elapsed_ms": 1.2,
                        "count": 1,
                        "details": {},
                    }
                },
                "external_agents": {
                    "trace32": {
                        "routed": True,
                        "used": False,
                        "error": "not configured",
                    }
                },
                "total_elapsed_ms": 3.4,
            },
        },
    )

    assert "diagnostic-body" in result
    assert "DIAGNOSTIC EXECUTION TRACE" in result
    assert "knowledge_base_dir: data/knowledge_base" in result
    assert "inventory: used | count=1 | elapsed_ms=1.2" in result
    assert "trace32: routed=True, used=False" in result
    assert "retrieval_total_elapsed_ms: 3.4" in result
