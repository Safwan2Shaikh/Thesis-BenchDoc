"""
chat_agent.py

Constraint-aware diagnostic chat agent
"""

from inventory_retriever import get_bench_info
from device_identifier import identify_devices
from diagnostic_engine import run_diagnostic


# ==========================================
# MAIN CHAT ROUTER
# ==========================================

def chat(user_input):

    # ==========================================
    # STEP 1 — BENCH DETECTION
    # ==========================================

    bench = get_bench_info(user_input)

    if not bench:

        return """
❌ No valid bench detected.

Please specify a bench name.

Examples:
- ABT-C-003WE
- 3WE
- 483
"""

    # ==========================================
    # STEP 2 — DEVICE IDENTIFICATION
    # ==========================================

    device_result = identify_devices(
        user_input,
        bench
    )

    # ==========================================
    # STEP 3 — LLM DIAGNOSTIC
    # ==========================================

    response = run_diagnostic(
        user_input,
        bench,
        device_result
    )

    return response


# ==========================================
# MAIN LOOP
# ==========================================

def main():

    print("🤖 Constraint-Aware ECU Diagnostic Agent\n")

    while True:

        user = input("You: ")

        if user.lower() == "exit":
            break

        print("\nAgent:\n")

        result = chat(user)

        print(result)

        print("\n==================================================")


if __name__ == "__main__":
    main()