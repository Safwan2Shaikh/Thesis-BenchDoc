"""
chat_agent.py
"""

from retrievers.bench_retriever import identify_bench

from retrievers.inventory_retriever import (
    get_bench_inventory
)

from device_identifier import (
    identify_devices
)

from diagnostic_engine import (
    run_diagnostic
)

from retrievers.master_retriever import (
    retrieve_context
)


DEVICE_LIST_INTENTS = [

    "available devices",
    "devices available",
    "show devices",
    "list devices",
    "list all device",

    "what devices",
    "which devices",

    "connected devices",
    "devices connected"

    "available hardware",
    "show hardware",

    "what hardware",

    "bench configuration",
    "bench setup"
]


def chat(user_input):

    # ============================================
    # BENCH IDENTIFICATION
    # ============================================

    bench_result = identify_bench(
        user_input
    )

    if not bench_result:

        return """
WARNING - Bench could not be identified.

Please specify:

• Full Bench Name

Example:
ABT-C-00483

OR

• Bench IP Address

Example:
10.10.10.15

Short names such as:

483
3WE

are not supported.
"""

    bench_name = bench_result[
        "bench_name"
    ]

    # ============================================
    # INVENTORY
    # ============================================

    bench_inventory = (
        get_bench_inventory(
            bench_name
        )
    )

    if not bench_inventory:

        return f"""
WARNING - Bench found:

{bench_name}

But no inventory exists.
"""

    # ============================================
    # SPECIAL DEVICE LIST INTENT
    # ============================================

    query_lower = user_input.lower()

    if any(
        phrase in query_lower
        for phrase in DEVICE_LIST_INTENTS
    ):

        response = [
            f"Bench: {bench_name}",
            ""
        ]

        for key, value in (
            bench_inventory.items()
        ):

            if not value:
                continue

            if value.strip():

                response.append(
                    f"{key}: {value}"
                )

        return "\n".join(response)

    # ============================================
    # DEVICE IDENTIFICATION
    # ============================================

    device_result = identify_devices(
        user_input,
        bench_inventory
    )

    # ============================================
    # RETRIEVAL
    # ============================================

    retrieval_context = (
        retrieve_context(
            user_query=user_input,
            bench=bench_name
        )
    )

    # ============================================
    # LLM
    # ============================================

    return run_diagnostic(
        user_input=user_input,
        bench=bench_name,
        device_result=device_result,
        retrieval_context=retrieval_context
    )


def main():

    print(
        "\n========================================"
    )

    print(
        " Radar ECU Diagnostic Assistant"
    )

    print(
        "========================================"
    )

    while True:

        user_input = input(
            "\nYou: "
        ).strip()

        if not user_input:
            continue

        if user_input.lower() in [
            "exit",
            "quit",
            "q"
        ]:
            break

        try:

            result = chat(
                user_input
            )

            print(
                f"\nAssistant:\n\n{result}"
            )

        except Exception as e:

            print(
                f"Error: {e}"
            )


if __name__ == "__main__":
    main()