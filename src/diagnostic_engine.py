"""
diagnostic_engine.py

LLM diagnostic reasoning layer
with retrieval support.
"""

from llm_client import LLMClient

llm = LLMClient()


# ==================================================
# BUILD RETRIEVAL CONTEXT
# ==================================================

def build_retrieval_context(retrieval_context):

    context_text = ""

    # =============================================
    # INVENTORY
    # =============================================

    inventory = retrieval_context.get(
        "inventory"
    )

    if inventory:

        context_text += """

==========================
BENCH INVENTORY
==========================

"""

        context_text += str(inventory)

        context_text += "\n\n"

    # =============================================
    # HISTORICAL ISSUES
    # =============================================

    issues = retrieval_context.get(
        "similar_issues",
        []
    )

    if issues:

        context_text += """

==========================
KNOWN HISTORICAL ISSUES
==========================

"""

        for issue in issues:

            context_text += f"""

Issue:
{issue.get('issue', '')}

Root Cause:
{issue.get('root_cause', '')}

Solution:
{issue.get('solution', '')}

Symptoms:
{issue.get('symptoms', '')}

-----------------------------------

"""

    # =============================================
    # KNOWLEDGE CHUNKS
    # =============================================

    chunks = retrieval_context.get(
        "knowledge_chunks",
        []
    )

    if chunks:

        context_text += """

==========================
KNOWLEDGE BASE
==========================

"""

        for chunk in chunks:

            context_text += f"""

File:
{chunk.get('file_name', '')}

Category:
{chunk.get('category', '')}

Content:
{chunk.get('content', '')}

-----------------------------------

"""

    # =============================================
    # BENCH TOPOLOGY
    # =============================================

    topology = retrieval_context.get(
        "bench_topology"
    )

    if topology:

        context_text += """

==========================
BENCH TOPOLOGY
==========================

"""

        # -------------------------
        # Bench Definition
        # -------------------------

        context_text += "Bench Information:\n\n"

        context_text += str(
            topology.get(
                "bench_info",
                {}
            )
        )

        context_text += "\n\n"

        # -------------------------
        # Connections
        # -------------------------

        connections = topology.get(
            "connections",
            []
        )

        if connections:

            context_text += (
                "Relevant Connections:\n\n"
            )

            for edge in connections:

                context_text += (
                    f"{edge.get('source')} "
                    f"--{edge.get('relation')}--> "
                    f"{edge.get('target')}\n"
                )

            context_text += "\n"

        # -------------------------
        # Troubleshooting Rules
        # -------------------------

        rules = topology.get(
            "rules",
            []
        )

        if rules:

            context_text += (
                "Relevant Troubleshooting Rules:\n\n"
            )

            for rule in rules:

                condition = rule.get(
                    "condition",
                    ""
                )

                context_text += (
                    f"Condition: "
                    f"{condition}\n"
                )

                check_order = rule.get(
                    "check_order",
                    []
                )

                if check_order:

                    context_text += (
                        "Check Order:\n"
                    )

                    for step in check_order:

                        context_text += (
                            f" - {step}\n"
                        )

                context_text += "\n"

    return context_text


# ==================================================
# BUILD PROMPT
# ==================================================

def build_prompt(
    query,
    bench,
    device_result,
    retrieval_context
):

    retrieval_text = build_retrieval_context(
        retrieval_context
    )

    prompt = f"""
You are a professional ECU testbench troubleshooting assistant.

The inventory system and bench topology are the source of truth.

================================================
USER QUERY
================================================

{query}

================================================
BENCH
================================================

{bench}

================================================
DEVICE IDENTIFICATION
================================================

Available Devices On Bench:

{device_result.get('bench_devices', [])}

Devices Mentioned By User:

{device_result.get('query_devices', [])}

Validated Devices:

{device_result.get('valid_devices', [])}

Invalid Devices:

{device_result.get('invalid_devices', [])}

================================================
RETRIEVED KNOWLEDGE
================================================

{retrieval_text}

================================================
INSTRUCTIONS
================================================

Use ALL available information:

1. Inventory Information
2. Historical Issues
3. Knowledge Base Files
4. Bench Topology
5. Device Relationships
6. Power Connections
7. Communication Paths
8. Troubleshooting Rules

When bench topology is available:

- Use connection paths as evidence.
- Use troubleshooting rules as guidance.
- Consider power dependencies.
- Consider CAN dependencies.
- Consider Ethernet dependencies.
- Consider debugger connections.

If invalid devices exist:

- Clearly explain that the device is not
  configured on the bench.

- Mention possible reasons:
  * wrong bench selected
  * outdated inventory
  * manually connected hardware

If historical issues match:

- mention them as supporting evidence

If knowledge base files match:

- use them as troubleshooting evidence

Do not invent hardware.
Do not invent connections.
Do not invent log messages.

Provide practical engineering advice.

================================================
RESPONSE FORMAT
================================================

Issue Analysis:

Likely Root Cause:

Supporting Evidence:

Relevant Historical Issues:

Recommended Checks:

Confidence:
"""

    return prompt


# ==================================================
# RUN DIAGNOSTIC
# ==================================================

def run_diagnostic(
    user_input,
    bench,
    device_result,
    retrieval_context
):

    prompt = build_prompt(
        query=user_input,
        bench=bench,
        device_result=device_result,
        retrieval_context=retrieval_context
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an ECU testbench troubleshooting "
                "assistant."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = llm.ask(messages)

    return response["reply"]