import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thesis.workflows.diagnose_workflow import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run LLM diagnosis")
    parser.add_argument("query", nargs="*", help="Diagnostic query text")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive diagnosis session",
    )
    return parser


def interactive_loop() -> None:
    print("\\n========================================")
    print(" Thesis Unified Bench Assistant")
    print("========================================")
    while True:
        user_input = input("\\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        print("\\nAssistant:\\n")
        print(run(user_input))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.interactive or not args.query:
        interactive_loop()
        return

    prompt = " ".join(args.query).strip()
    print(run(prompt))


if __name__ == "__main__":
    main()
