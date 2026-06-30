from typing import Optional

from thesis.bench.controllers.pdu_controller import PDUController
from thesis.bench.controllers.topology import BenchTopology



def run_check(
    exe_path: Optional[str] = None,
    config_file: Optional[str] = None,
    graph_file: Optional[str] = None,
):
    topology = BenchTopology(graph_file)
    mapping = topology.get_pdu_mapping()

    result = {
        "status": "OK",
        "mapping": mapping,
        "connected": False,
    }

    if not exe_path or not config_file:
        result["status"] = "WARNING"
        result["warning"] = "PDU executable/config not provided; returned mapping only"
        return result

    try:
        controller = PDUController(exe_path=exe_path, config_file=config_file)
        states_output = controller.read_states()
        result["connected"] = True
        result["states_raw"] = states_output
        return result
    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)
        return result


def main():
    print(run_check())


if __name__ == "__main__":
    main()
