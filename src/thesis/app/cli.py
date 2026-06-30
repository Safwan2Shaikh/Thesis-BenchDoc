from thesis.workflows.diagnose_workflow import run as run_diagnose


def main() -> None:
    print("\n========================================")
    print(" Thesis Unified Bench Assistant")
    print("========================================")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        try:
            result = run_diagnose(user_input)
            print(f"\nAssistant:\n\n{result}")
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
