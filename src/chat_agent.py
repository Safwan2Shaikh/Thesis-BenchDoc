"""
chat_agent.py

Smart multi-source AI agent
"""

from fuzzy_retriever import find_similar_issues
from inventory_retriever import get_bench_info
from device_rules import get_device_suggestions
from llm_client import LLMClient

llm = LLMClient()
total_tokens_used = 0


def detect_intent(query):
    query = query.lower()
    if any(w in query for w in ["what", "show", "devices", "config", "connected"]):
        return "inventory"
    return "troubleshooting"


def get_confidence(score):
    if score > 80: return "High"
    if score > 50: return "Medium"
    return "Low"


# ✅ INVENTORY MODE
def handle_inventory(query):
    bench = get_bench_info(query)

    if not bench:
        return "❌ No bench found"

    return f"""
✅ Bench Configuration

Bench: {bench['bench']}

🔧 Samples:
- {bench['sample1']}
- {bench['sample2']}
- {bench['sample3']}

⚙️ Devices:
- PSU: {bench['psu']}
- Vector: {bench['vector1']}
- Relay: {bench['relay']}
- NetGear: {bench['netgear']}
- Lauterbach: {bench['lauterbach1']}
- PDU: {bench['pdu']}
"""


# ✅ TROUBLESHOOTING MODE
def handle_troubleshooting(query):
    global total_tokens_used

    matches = find_similar_issues(query)
    bench = get_bench_info(query)

    if matches:
        confidence = get_confidence(matches[0]["score"])
        issue_context = "\n".join([
            f"Issue: {m['issue']} | Solution: {m['solution']}"
            for m in matches
        ])
    else:
        confidence = "Low"
        issue_context = "No similar issues"

    # Device rules
    device_context = ""
    if bench:
        rules = get_device_suggestions(bench, query)
        device_context = "\n".join(rules)

    prompt = f"""
You are an ECU troubleshooting assistant.

Bench Config:
{bench}

Device Knowledge:
{device_context}

Past Issues:
{issue_context}

User problem:
{query}

Give clear answer:

Root Cause:
Solution:
Confidence: {confidence}
"""

    res = llm.ask([{"role": "user", "content": prompt}])

    total_tokens_used += res["tokens"]

    print(f"\n📊 Tokens: {res['tokens']} | Total: {total_tokens_used}")

    return res["reply"]


def chat(user_input):
    intent = detect_intent(user_input)

    if intent == "inventory":
        return handle_inventory(user_input)

    return handle_troubleshooting(user_input)


def main():
    print("🤖 Smart Agent Running\n")

    while True:
        user = input("You: ")

        if user.lower() == "exit":
            break

        print("Agent:\n", chat(user))


if __name__ == "__main__":
    main()
