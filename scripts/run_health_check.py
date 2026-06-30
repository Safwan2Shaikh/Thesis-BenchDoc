import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thesis.workflows.health_check_workflow import run_health_check


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bench health checks")
    parser.add_argument(
        "--device",
        choices=["all", "pdu", "pmb", "psu", "vector", "pc_ports"],
        default="all",
        help="Run a specific device check or all checks",
    )
    parser.add_argument("--serial-port", default="COM3", help="Serial port for PSU/PMB checks")
    parser.add_argument("--pdu-exe", default=None, help="PDU executable path")
    parser.add_argument("--pdu-cfg", default=None, help="PDU config yaml path")
    parser.add_argument("--graph-file", default=None, help="Bench graph yaml path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    result = run_health_check(
        device=args.device,
        serial_port=args.serial_port,
        pdu_exe=args.pdu_exe,
        pdu_cfg=args.pdu_cfg,
        graph_file=args.graph_file,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
