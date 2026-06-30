"""
master_retriever.py

Central retrieval orchestrator.
"""

from thesis.intelligence.retrieval.inventory_retriever import (
    get_bench_inventory
)

from thesis.intelligence.retrieval.fuzzy_retriever import (
    find_similar_issues
)

from thesis.intelligence.retrieval.chunk_md_retriever import (
    retrieve_chunks
)

from thesis.intelligence.retrieval.bench_topology_retriever import (
    get_bench_context
)

from thesis.intelligence.agents.agent_router import (
    needs_trace32_agent
)

from thesis.intelligence.agents.trace32_agent import (
    Trace32Agent
)


def retrieve_context(
    user_query,
    bench
):

    context = {
        "inventory": None,
        "similar_issues": [],
        "knowledge_chunks": [],
        "bench_topology": None,
        "trace32_advice": None
    }

    # ======================================
    # INVENTORY
    # ======================================

    try:

        context["inventory"] = (
            get_bench_inventory(
                bench
            )
        )

    except Exception as e:

        print(
            f"Inventory retrieval failed: {e}"
        )

    # ======================================
    # HISTORICAL ISSUES
    # ======================================

    try:

        context["similar_issues"] = (
            find_similar_issues(
                user_query
            )
        )

    except Exception as e:

        print(
            f"Issue retrieval failed: {e}"
        )

    # ======================================
    # KNOWLEDGE CHUNKS
    # ======================================

    try:

        context["knowledge_chunks"] = (
            retrieve_chunks(
                user_query
            )
        )

    except Exception as e:

        print(
            f"Chunk retrieval failed: {e}"
        )

    # ======================================
    # BENCH TOPOLOGY
    # ======================================

    try:

        context["bench_topology"] = (
            get_bench_context(
                user_query
            )
        )

    except Exception as e:

        print(
            f"Bench topology retrieval failed: {e}"
        )

    # ======================================
    # TRACE32 AGENT
    # ======================================

    try:

        if needs_trace32_agent(
            user_query
        ):

            topology = context.get(
                "bench_topology"
            )

            inventory = context.get(
                "inventory"
            )

            trace32_prompt = f"""
Bench:
{bench}

Inventory:
{inventory}

Bench Topology:
{topology}

User Issue:
{user_query}

Provide:

1. Trace32-specific root cause analysis
2. Debugger-related troubleshooting
3. Recommended checks
4. Useful PRACTICE/CMM commands
5. Engineering recommendations

Focus only on Lauterbach / Trace32 expertise.
"""

            agent = Trace32Agent()

            context["trace32_advice"] = (
                agent.ask(
                    trace32_prompt
                )
            )

    except Exception as e:

        print(
            f"Trace32 agent failed: {e}"
        )

    return context