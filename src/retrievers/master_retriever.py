"""
master_retriever.py

Central retrieval orchestrator.
"""

from time import perf_counter

from thesis.infra.paths import (
    knowledge_base_dir,
    processed_dir
)

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


def _classify_trace32_error(error):
    message = str(error)
    lower_message = message.lower()

    if "http 500" in lower_message or "server_error" in lower_message or "error code: 500" in lower_message:
        return {
            "error_type": "service_unavailable",
            "retryable": True,
            "message": "Trace32 specialist agent service returned HTTP 500/server_error.",
            "fallback": "Main diagnosis continued without Trace32 specialist advice. Retry the Trace32 agent later.",
        }

    if "not configured" in lower_message:
        return {
            "error_type": "configuration_missing",
            "retryable": False,
            "message": message,
            "fallback": "Main diagnosis continued without Trace32 specialist advice. Configure TRACE32_AGENT_TOKEN and TRACE32_AGENT_ID to enable it.",
        }

    return {
        "error_type": "request_failed",
        "retryable": True,
        "message": message,
        "fallback": "Main diagnosis continued without Trace32 specialist advice.",
    }


def retrieve_context(
    user_query,
    bench=None,
    include_external_agents=True,
    include_general_chunks=True
):

    started_at = perf_counter()

    context = {
        "inventory": None,
        "similar_issues": [],
        "knowledge_chunks": [],
        "bench_topology": None,
        "trace32_advice": None,
        "metadata": {
            "bench": bench,
            "query": user_query,
            "scope": "bench" if bench else "general",
            "sources": {
                "knowledge_base_dir": str(knowledge_base_dir()),
                "processed_dir": str(processed_dir())
            },
            "retrievers": {},
            "external_agents": {
                "trace32": {
                    "routed": False,
                    "used": False,
                    "error": None,
                    "enabled": include_external_agents
                }
            },
            "total_elapsed_ms": 0
        }
    }

    def record_retriever(
        name,
        status,
        elapsed_ms,
        count=0,
        error=None,
        details=None
    ):
        context["metadata"]["retrievers"][name] = {
            "status": status,
            "elapsed_ms": round(elapsed_ms, 2),
            "count": count,
            "error": error,
            "details": details or {}
        }

    # ======================================
    # INVENTORY
    # ======================================

    try:

        retriever_started = perf_counter()

        context["inventory"] = (
            get_bench_inventory(
                bench
            )
            if bench else None
        )

        record_retriever(
            "inventory",
            "used" if context["inventory"] else "empty",
            (perf_counter() - retriever_started) * 1000,
            count=len(context["inventory"] or {})
        )

    except Exception as e:

        record_retriever(
            "inventory",
            "error",
            (perf_counter() - retriever_started) * 1000,
            error=str(e)
        )

        print(
            f"Inventory retrieval failed: {e}"
        )

    # ======================================
    # HISTORICAL ISSUES
    # ======================================

    try:

        retriever_started = perf_counter()

        context["similar_issues"] = (
            find_similar_issues(
                user_query,
                bench=bench
            )
        )

        record_retriever(
            "historical_issues",
            "used" if context["similar_issues"] else "empty",
            (perf_counter() - retriever_started) * 1000,
            count=len(context["similar_issues"]),
            details={
                "top_scores": [
                    round(issue.get("score", 0), 2)
                    for issue in context["similar_issues"]
                ]
            }
        )

    except Exception as e:

        record_retriever(
            "historical_issues",
            "error",
            (perf_counter() - retriever_started) * 1000,
            error=str(e)
        )

        print(
            f"Issue retrieval failed: {e}"
        )

    # ======================================
    # KNOWLEDGE CHUNKS
    # ======================================

    try:

        retriever_started = perf_counter()

        context["knowledge_chunks"] = (
            retrieve_chunks(
                user_query
            )
            if include_general_chunks else []
        )

        record_retriever(
            "knowledge_chunks",
            "used" if context["knowledge_chunks"] else "disabled" if not include_general_chunks else "empty",
            (perf_counter() - retriever_started) * 1000,
            count=len(context["knowledge_chunks"]),
            details={
                "files": [
                    chunk.get("file_name", "")
                    for chunk in context["knowledge_chunks"]
                ]
            }
        )

    except Exception as e:

        record_retriever(
            "knowledge_chunks",
            "error",
            (perf_counter() - retriever_started) * 1000,
            error=str(e)
        )

        print(
            f"Chunk retrieval failed: {e}"
        )

    # ======================================
    # BENCH TOPOLOGY
    # ======================================

    try:

        retriever_started = perf_counter()

        context["bench_topology"] = (
            get_bench_context(
                user_query,
                bench=bench
            )
        )

        topology = context["bench_topology"] or {}

        record_retriever(
            "bench_topology",
            "used" if topology else "empty",
            (perf_counter() - retriever_started) * 1000,
            count=len(topology.get("connections", [])) + len(topology.get("rules", [])),
            details={
                "connections": len(topology.get("connections", [])),
                "rules": len(topology.get("rules", [])),
                "bench_id": topology.get("bench_id"),
                "config_folder": topology.get("config_folder"),
                "searched_benches": topology.get("metadata", {}).get("searched_benches", [])
            }
        )

    except Exception as e:

        record_retriever(
            "bench_topology",
            "error",
            (perf_counter() - retriever_started) * 1000,
            error=str(e)
        )

        print(
            f"Bench topology retrieval failed: {e}"
        )

    # ======================================
    # TRACE32 AGENT
    # ======================================

    try:

        agent_started = None

        if include_external_agents and needs_trace32_agent(
            user_query
        ):

            context["metadata"]["external_agents"]["trace32"]["routed"] = True
            agent_started = perf_counter()

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

            context["metadata"]["external_agents"]["trace32"].update(
                {
                    "used": True,
                    "elapsed_ms": round((perf_counter() - agent_started) * 1000, 2)
                }
            )

    except Exception as e:

        failure = _classify_trace32_error(e)

        update = {
            "used": False,
            "error": failure["message"],
            "error_type": failure["error_type"],
            "retryable": failure["retryable"],
            "fallback": failure["fallback"],
        }

        if agent_started is not None:
            update["elapsed_ms"] = round((perf_counter() - agent_started) * 1000, 2)

        context["metadata"]["external_agents"]["trace32"].update(update)

        print(
            f"Trace32 agent failed: {failure['message']} {failure['fallback']}"
        )

    context["metadata"]["total_elapsed_ms"] = round(
        (perf_counter() - started_at) * 1000,
        2
    )

    return context