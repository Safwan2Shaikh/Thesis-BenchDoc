"""
chat_agent.py
"""

from thesis.intelligence.retrieval.bench_retriever import identify_bench

from thesis.intelligence.retrieval.inventory_retriever import (
    get_bench_inventory
)

from thesis.intelligence.orchestrator.device_identifier import (
    identify_devices
)

from thesis.intelligence.orchestrator.diagnostic_engine import (
    run_diagnostic
)

from thesis.intelligence.retrieval.master_retriever import (
    retrieve_context
)

from thesis.intelligence.retrieval.bench_topology_retriever import (
    has_bench_config,
    get_bench_context
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
    "devices connected",

    "available hardware",
    "show hardware",

    "what hardware",

    "bench configuration",
    "bench setup"
]


def _devices_from_topology(bench_name):
    if not bench_name or not has_bench_config(bench_name):
        return {}

    topology = get_bench_context("", bench=bench_name)
    devices = topology.get("bench_info", {}).get("devices", {})

    return {
        name: details.get("type", "configured")
        if isinstance(details, dict)
        else str(details)
        for name, details in devices.items()
    }


def _build_device_result(user_input, bench_inventory, bench_name):
    if bench_inventory:
        return identify_devices(
            user_input,
            bench_inventory
        )

    topology_devices = _devices_from_topology(bench_name)

    return {
        "bench_devices": list(topology_devices.keys()),
        "query_devices": [],
        "valid_devices": [],
        "invalid_devices": []
    }


def _retrieve_context_for_chat(
    user_input,
    bench_name,
    include_external_agents,
    include_general_chunks
):
    try:
        return retrieve_context(
            user_query=user_input,
            bench=bench_name,
            include_external_agents=include_external_agents,
            include_general_chunks=include_general_chunks
        )
    except TypeError as exc:
        if "unexpected keyword argument" not in str(exc):
            raise

        return retrieve_context(
            user_query=user_input,
            bench=bench_name
        )


def chat(
    user_input,
    selected_bench=None,
    general_session=False,
    include_external_agents=True,
    include_general_chunks=True
):

    # ============================================
    # BENCH IDENTIFICATION
    # ============================================

    if selected_bench:
        bench_result = {
            "bench_name": selected_bench,
            "ip": None
        }
    else:
        bench_result = identify_bench(
            user_input
        )

    if not bench_result and not general_session:

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

    bench_name = (
        bench_result["bench_name"]
        if bench_result
        else None
    )

    # ============================================
    # INVENTORY
    # ============================================

    bench_inventory = None

    if bench_name:
        bench_inventory = (
            get_bench_inventory(
                bench_name
            )
        )

    if bench_name and not bench_inventory and not has_bench_config(bench_name):

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
            f"Bench: {bench_name or 'General session'}",
            ""
        ]

        devices = bench_inventory or _devices_from_topology(bench_name)

        for key, value in devices.items():

            if not value:
                continue

            if str(value).strip():

                response.append(
                    f"{key}: {value}"
                )

        return "\n".join(response)

    # ============================================
    # DEVICE IDENTIFICATION
    # ============================================

    device_result = _build_device_result(
        user_input,
        bench_inventory,
        bench_name
    )

    # ============================================
    # RETRIEVAL
    # ============================================

    retrieval_context = (
        _retrieve_context_for_chat(
            user_input=user_input,
            bench_name=bench_name,
            include_external_agents=include_external_agents,
            include_general_chunks=include_general_chunks
        )
    )

    # ============================================
    # LLM
    # ============================================

    return run_diagnostic(
        user_input=user_input,
        bench=bench_name or "General session",
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