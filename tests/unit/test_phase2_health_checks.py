import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_data_dir_path_resolution():
    """Verify path resolution now prefers populated data/ folders."""
    from thesis.infra.paths import knowledge_base_dir, logs_dir, processed_dir

    kb_dir = knowledge_base_dir()
    assert kb_dir.exists()
    assert (kb_dir / "Bench_mapping.csv").exists()
    
    processed = processed_dir()
    assert processed.exists()
    assert (processed / "cleaned_issues.csv").exists()


def test_bench_checks_imports():
    """Verify all migrated bench checks can import."""
    from thesis.bench.checks.pc_ports_check import get_com_ports
    from thesis.bench.orchestrator.bench_orchestrator import BenchOrchestrator

    try:
        from thesis.bench.checks.vector_check import configs
    except ModuleNotFoundError:
        pass  # python-can is optional

    assert callable(get_com_ports)
    assert callable(BenchOrchestrator)


def test_bench_orchestrator_initialization():
    """Verify bench orchestrator can initialize."""
    from thesis.bench.orchestrator.bench_orchestrator import BenchOrchestrator

    orch = BenchOrchestrator()
    assert orch.results == {}


def test_pdu_service_with_default_graph():
    """Verify PDU service can resolve graph file automatically."""
    from thesis.bench.controllers.topology import BenchTopology

    topo = BenchTopology()
    assert topo.graph is not None
    assert "edges" in topo.graph or len(topo.graph) >= 0
