"""
Unified health check orchestrator.
"""

from typing import Any, Dict


class BenchOrchestrator:
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}

    # Compatibility methods preserved for existing tests/callers
    def run_pc_ports_check(self) -> Dict[str, Any]:
        return self.run_device("pc_ports")

    def run_vector_check(self) -> Dict[str, Any]:
        return self.run_device("vector")

    def run_psu_check(self, serial_port: str = "COM3") -> Dict[str, Any]:
        return self.run_device("psu", serial_port=serial_port)

    def run_pmb_check(self, serial_port: str = "COM3") -> Dict[str, Any]:
        return self.run_device("pmb", serial_port=serial_port)

    def run_pdu_check(self, pdu_exe=None, pdu_cfg=None, graph_file=None) -> Dict[str, Any]:
        return self.run_device("pdu", pdu_exe=pdu_exe, pdu_cfg=pdu_cfg, graph_file=graph_file)

    def run_device(self, device: str, **kwargs) -> Dict[str, Any]:
        key = device.strip().lower()

        if key in {"pc", "pc_ports", "ports", "com"}:
            from thesis.bench.checks.pc_ports_check import run_check as run_pc_ports_check

            result = run_pc_ports_check()
            self.results["pc_ports"] = result
            return result

        if key == "vector":
            from thesis.bench.checks.vector_check import detect_vector_devices

            result = detect_vector_devices()
            self.results["vector"] = result
            return result

        if key == "psu":
            from thesis.bench.checks.psu_check import run_check as run_psu_check

            result = run_psu_check(serial_port=kwargs.get("serial_port", "COM3"))
            self.results["psu"] = result
            return result

        if key == "pmb":
            from thesis.bench.checks.pmb_check import run_check as run_pmb_check

            result = run_pmb_check(serial_port=kwargs.get("serial_port", "COM3"))
            self.results["pmb"] = result
            return result

        if key == "pdu":
            from thesis.bench.checks.pdu_check import run_check as run_pdu_check

            result = run_pdu_check(
                exe_path=kwargs.get("pdu_exe"),
                config_file=kwargs.get("pdu_cfg"),
                graph_file=kwargs.get("graph_file"),
            )
            self.results["pdu"] = result
            return result

        raise ValueError(f"Unsupported device check: {device}")

    def run_all_checks(self, **kwargs) -> Dict[str, Dict[str, Any]]:
        for device in ["pc_ports", "vector", "psu", "pmb", "pdu"]:
            self.run_device(device, **kwargs)
        return self.results

    def get_summary(self) -> str:
        lines = ["=== Bench Health Summary ==="]
        for name, result in self.results.items():
            lines.append(f"{name}: {result.get('status', 'UNKNOWN')}")
        return "\n".join(lines)
