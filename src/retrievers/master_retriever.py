"""
master_retriever.py

Central retrieval orchestrator.
"""

from retrievers.inventory_retriever import (
    get_bench_inventory
)

from retrievers.fuzzy_retriever import (
    find_similar_issues
)

from retrievers.chunk_md_retriever import (
    retrieve_chunks
)

from retrievers.bench_topology_retriever import (
    get_bench_context
)


def retrieve_context(
    user_query,
    bench
):

    context = {
        "inventory": None,
        "similar_issues": [],
        "knowledge_chunks": [],
        "bench_topology": None
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

    return context