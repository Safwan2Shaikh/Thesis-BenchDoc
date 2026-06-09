"""
chat_agent.py

Simple stable chat agent
"""

from fuzzy_retriever import find_similar_issues
from inventory_retriever import get_bench_info
from llm_client import LLMClient

llm = LLMClient()

total_tokens_used = 0


# =============================
# INTENT DETECTION
# =============================

def detect_intent(query):

    query = query.lower()

    inventory_words = [
        "what",
        "show",
        "devices",
        "config",
        "connected"
    ]

    if any(word in query for word in inventory_words):
        return "inventory"

    return "troubleshooting"


# =============================
# CONFIDENCE
# =============================

def get_confidence(score):

    if score > 80:
        return "High"

    if score > 50:
        return "Medium"

    return "Low"


# =============================
# INVENTORY MODE
# =============================

def handle_inventory(query):

    bench = get_bench_info(query)

    if not bench:
        return "❌ No bench found"

    return f"""
✅ Bench Configuration

Bench:
{bench['bench']}

====================

🔧 Samples
Sample 1:{bench['sample1']}
Sample 2:{bench['sample2']}
Sample 3:{bench['sample3']}
====================

⚙️ Devices
PSU:{bench['psu']}
Vector 1:{bench['vector1']}
Vector 2:{bench['vector2']}
Relay:{bench['relay']}
NetGear:{bench['netgear']}
Extras:{bench['extras']}
Lauterbach 1:{bench['lauterbach1']}
Lauterbach 2:{bench['lauterbach2']}
PDU:{bench['pdu']}
"""


# =============================
# TROUBLESHOOTING MODE
# =============================

def handle_troubleshooting(query):

    global total_tokens_used

    bench = get_bench_info(query)

    matches = find_similar_issues(query)

    # ✅ Bench context
    if bench:
        bench_context = f"""
Bench: {bench['bench']}

Samples:
- {bench['sample1']}
- {bench['sample2']}
- {bench['sample3']}

Devices:
- PSU: {bench['psu']}
- Vector: {bench['vector1']}
- Relay: {bench['relay']}
- Lauterbach: {bench['lauterbach1']}
"""
    else:
        bench_context = "No bench information found."

    # ✅ Issue context
    if matches:

        confidence = get_confidence(matches[0]["score"])

        issue_context = "\n".join([
            f"""
Issue: {m['issue']}
Root Cause: {m['root_cause']}
Solution: {m['solution']}
"""
            for m in matches
        ])

    else:
        confidence = "Low"
        issue_context = "No similar issues found."

    # ✅ Prompt
    prompt = f"""
You are an ECU troubleshooting assistant.

Bench Context:
{bench_context}

Historical Issues:
{issue_context}

User Problem:
{query}

Instructions:
- Use bench hardware context
- Use historical issue context
- Give concise troubleshooting steps
- Do not hallucinate hardware

Format:

Root Cause:
Solution:
Confidence:
{confidence}
"""

    response = llm.ask([
        {"role": "user", "content": prompt}
    ])

    total_tokens_used += response["tokens"]

    print(f"\n📊 Tokens: {response['tokens']} | Total: {total_tokens_used}")

    return response["reply"]


# =============================
# ROUTER
# =============================

def chat(user_input):

    intent = detect_intent(user_input)

    if intent == "inventory":
        return handle_inventory(user_input)

    return handle_troubleshooting(user_input)


# =============================
# MAIN LOOP
# =============================

def main():

    print("🤖 Smart Agent Running\n")

    while True:

        user = input("You: ")

        if user.lower() == "exit":
            break

        print("\nAgent:\n")

        print(chat(user))


if __name__ == "__main__":
    main()