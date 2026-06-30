import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_data_folder_migration():
    """Verify all data folders are populated in new location."""
    data_root = Path(__file__).resolve().parents[2] / "data"
    
    assert (data_root / "knowledge_base" / "Bench_mapping.csv").exists()
    assert (data_root / "knowledge_base" / "TB_Inventory.csv").exists()
    assert (data_root / "knowledge_base" / "Bench_Config").exists()
    assert (data_root / "processed" / "cleaned_issues.csv").exists()
    assert (data_root / "logs" / "raw").exists()


def test_bench_retrieval_with_new_paths(monkeypatch):
    """Verify retrievers work with new data paths."""
    from thesis.intelligence.retrieval.bench_retriever import identify_bench
    from thesis.intelligence.retrieval.inventory_retriever import get_bench_inventory

    assert callable(identify_bench)
    assert callable(get_bench_inventory)


def test_orchestrator_health_check_workflow():
    """Verify orchestrator can run health checks."""
    from thesis.bench.orchestrator.bench_orchestrator import BenchOrchestrator

    orch = BenchOrchestrator()
    orch.run_pc_ports_check()
    assert "pc_ports" in orch.results
    assert "status" in orch.results["pc_ports"]


def test_unified_workflow_intact():
    """Verify unified diagnose workflow still works after migration."""
    from thesis.workflows.diagnose_workflow import run

    assert callable(run)
