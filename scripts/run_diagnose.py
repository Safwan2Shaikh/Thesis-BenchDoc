import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thesis.workflows.diagnose_workflow import run
from thesis.intelligence.retrieval.bench_retriever import list_benches
from thesis.intelligence.retrieval.bench_topology_retriever import list_bench_configs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run LLM diagnosis")
    parser.add_argument("query", nargs="*", help="Diagnostic query text")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive diagnosis session",
    )
    parser.add_argument(
        "--bench",
        help="Run diagnosis scoped to a selected bench name, for example ABT-C-003WE",
    )
    parser.add_argument(
        "--general",
        action="store_true",
        help="Run diagnosis as a general session without forcing a bench scope",
    )
    return parser


def select_session_scope() -> tuple[str | None, bool]:
    configured_benches = set(list_bench_configs().keys())
    benches = list_benches()

    for bench in configured_benches:
        if not any(item["bench_name"].upper() == bench.upper() for item in benches):
            benches.append({"bench_name": bench, "ip": ""})

    benches = sorted(benches, key=lambda item: item["bench_name"])

    print("\nSelect session scope:")
    print("0. General session")

    for index, bench in enumerate(benches, start=1):
        marker = "configured" if bench["bench_name"] in configured_benches else "inventory"
        ip = str(bench.get("ip", "") or "").strip()
        suffix = f" | {ip}" if ip and ip.lower() != "nan" else ""
        print(f"{index}. {bench['bench_name']} ({marker}){suffix}")

    while True:
        selection = input("\nBench selection: ").strip()
        if selection == "0":
            return None, True

        if selection.isdigit():
            index = int(selection)
            if 1 <= index <= len(benches):
                return benches[index - 1]["bench_name"], False

        match = next(
            (
                bench
                for bench in benches
                if bench["bench_name"].lower() == selection.lower()
            ),
            None,
        )
        if match:
            return match["bench_name"], False

        print("Please choose a listed number, full bench name, or 0 for general.")


def interactive_loop(selected_bench: str | None = None, general_session: bool = False) -> None:
    print("\\n========================================")
    print(" Thesis Unified Bench Assistant")
    print("========================================")

    if not selected_bench and not general_session:
        selected_bench, general_session = select_session_scope()

    print(f"\nSession: {selected_bench or 'General session'}")

    while True:
        user_input = input("\\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        print("\\nAssistant:\\n")
        print(
            run(
                user_input,
                selected_bench=selected_bench,
                general_session=general_session,
            )
        )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.interactive or not args.query:
        interactive_loop(
            selected_bench=args.bench,
            general_session=args.general,
        )
        return

    prompt = " ".join(args.query).strip()
    print(
        run(
            prompt,
            selected_bench=args.bench,
            general_session=args.general,
        )
    )


if __name__ == "__main__":
    main()
