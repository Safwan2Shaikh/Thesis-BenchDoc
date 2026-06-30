import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_core_modular_imports():
    from thesis.app.cli import main as cli_main
    from thesis.workflows.diagnose_workflow import run as diagnose_run
    from thesis.workflows.health_check_workflow import build_pdu_service
    from thesis.intelligence.retrieval.master_retriever import retrieve_context

    assert callable(cli_main)
    assert callable(diagnose_run)
    assert callable(build_pdu_service)
    assert callable(retrieve_context)
