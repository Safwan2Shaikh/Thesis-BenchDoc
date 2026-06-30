"""
diagnostic_engine.py

LLM diagnostic reasoning layer
with retrieval support.
"""

from thesis.intelligence.llm.client import LLMClient

_llm = None


def _get_llm_client():
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm


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

        context_text += (
            str(topology)
        )

        context_text += "\n\n"

    # =============================================
    # TRACE32 AGENT
    # =============================================

    trace32 = retrieval_context.get(
        "trace32_advice"
    )

    if trace32:

        context_text += """

==========================
TRACE32 EXPERT AGENT
==========================

"""

        context_text += trace32

        context_text += "\n\n"

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
6. Power Dependencies
7. CAN Dependencies
8. Ethernet Dependencies
9. Trace32 Expert Advice

IMPORTANT:

If Trace32 advice exists,
treat it as expert knowledge.

For Trace32 / Lauterbach issues:

- prioritize Trace32 recommendations
- use topology information
- use debugging paths
- use troubleshooting rules

Do not invent hardware.
Do not invent connections.
Do not invent commands.
Do not invent logs.

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
                "You are an ECU testbench troubleshooting assistant."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = _get_llm_client().ask(messages)

    return response["reply"]