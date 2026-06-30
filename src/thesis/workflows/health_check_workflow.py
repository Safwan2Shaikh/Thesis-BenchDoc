from thesis.bench.controllers.pdu_controller import PDUController
from thesis.bench.controllers.pdu_service import PDUService
from thesis.bench.controllers.topology import BenchTopology
from thesis.bench.orchestrator.bench_orchestrator import BenchOrchestrator


def build_pdu_service(graph_file: str, exe_path: str, config_file: str) -> PDUService:
    topology = BenchTopology(graph_file)
    mapping = topology.get_pdu_mapping()
    controller = PDUController(exe_path=exe_path, config_file=config_file)
    return PDUService(controller, mapping)


def run_health_check(device: str = "all", **kwargs):
    orchestrator = BenchOrchestrator()
    if device == "all":
        return orchestrator.run_all_checks(**kwargs)
    return {device: orchestrator.run_device(device, **kwargs)}
