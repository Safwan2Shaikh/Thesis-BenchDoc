"""
master_retriever.py
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


def retrieve_context(
    user_query,
    bench
):

    context = {
        "inventory": None,
        "similar_issues": [],
        "knowledge_chunks": []
    }

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

    return context