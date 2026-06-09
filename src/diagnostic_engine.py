"""
diagnostic_engine.py

LLM diagnostic reasoning layer
"""

from llm_client import LLMClient

llm = LLMClient()


# ==========================================
# BUILD PROMPT
# ==========================================

def build_prompt(query, bench, device_result):

    bench_name = bench["bench"]

    bench_devices = ", ".join(device_result["bench_devices"])

    query_devices = ", ".join(device_result["query_devices"])

    valid_devices = ", ".join(device_result["valid_devices"])

    invalid_devices = ", ".join(device_result["invalid_devices"])

    prompt = f"""
You are a professional ECU testbench troubleshooting assistant.

The inventory system is the source of truth.

User Query:
{query}

Bench:
{bench_name}

Available Devices On Bench:
{bench_devices}

Devices Mentioned By User:
{query_devices}

Validated Devices:
{valid_devices}

Invalid Devices:
{invalid_devices}

Instructions:

1. If invalid devices exist:
- Explain clearly that the requested device is not configured on this bench.
- Mention possible reasons:
    - wrong bench specified
    - outdated inventory
    - external hardware manually connected

2. If valid devices exist:
- Explain what component is likely involved.
- Suggest practical troubleshooting checks.

3. Be concise and engineering-focused.

4. Do NOT hallucinate hardware.

Format:

Issue Analysis:
Possible Causes:
Suggested Checks:
"""

    return prompt



# ==========================================
# RUN DIAGNOSTIC
# ==========================================

def run_diagnostic(query, bench, device_result):

    prompt = build_prompt(
        query,
        bench,
        device_result
    )

    response = llm.ask([
        {
            "role": "user",
            "content": prompt
        }
    ])

    return response["reply"]