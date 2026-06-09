import os
import requests
import pandas as pd
from rapidfuzz import fuzz
from dotenv import load_dotenv

# =============================
# CONFIG
# =============================
load_dotenv()

API_KEY = os.getenv("MODEL_FARM_API_KEY")

URL = "https://aoai-farm.bosch-temp.com/api/openai/deployments/gpt-5-nano-2025-08-07/chat/completions?api-version=2024-05-01-preview"

HEADERS = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

EXCEL_FILE = "../KnowledgeBase/Bench Maintain.xlsx"
TOP_K = 3

# ✅ IMPORTANT: set your column names correctly
ISSUE_COLUMN = "Issue"       # change if needed
SOLUTION_COLUMN = "Solution" # change if needed

# =============================
# TOKEN TRACKING
# =============================

total_tokens_used = 0

# =============================
# LOAD & CLEAN EXCEL
# =============================

df = pd.read_excel(EXCEL_FILE, engine="openpyxl")

# Clean NaN
df = df.fillna("")

print("✅ Columns detected:", list(df.columns))

# Validate columns exist
if ISSUE_COLUMN not in df.columns or SOLUTION_COLUMN not in df.columns:
    raise ValueError(f"Excel must contain columns: {ISSUE_COLUMN}, {SOLUTION_COLUMN}")

print(f"✅ Loaded {len(df)} issue records\n")

# =============================
# FUZZY MATCHING (UPGRADED)
# =============================

def find_similar_issues(query):
    scored = []

    for _, row in df.iterrows():
        issue_text = str(row[ISSUE_COLUMN])
        solution_text = str(row[SOLUTION_COLUMN])

        # ✅ Fuzzy similarity
        score = fuzz.partial_ratio(query.lower(), issue_text.lower())

        scored.append({
            "score": score,
            "issue": issue_text,
            "solution": solution_text
        })

    # Sort best first
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Return top matches
    return scored[:TOP_K]

# =============================
# CHAT FUNCTION
# =============================

def chat(user_input):
    global total_tokens_used

    matches = find_similar_issues(user_input)

    # ✅ Show matches (very useful)
    print("\n🔍 Top similar past issues:")
    for m in matches:
        print(f"- ({m['score']}%) {m['issue']}")

    # Build context for LLM
    if matches:
        context = "\n".join([
            f"Issue: {m['issue']} | Solution: {m['solution']}"
            for m in matches
        ])
    else:
        context = "No similar issues found."

    prompt = f"""
You are a troubleshooting assistant.

Similar past issues:
{context}

User problem:
{user_input}

Instructions:
- Use the similar issues to suggest a fix
- If similarity is low, say you're not confident
- Give the most relevant solution
- Be concise
"""

    payload = {
        "model": "gpt-5-nano-2025-08-07",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("❌ Error:", response.text)
        return

    data = response.json()

    reply = data["choices"][0]["message"]["content"]

    # ✅ Token tracking
    usage = data.get("usage", {})
    tokens_this_call = usage.get("total_tokens", 0)
    total_tokens_used += tokens_this_call

    print(f"\n📊 Tokens this call: {tokens_this_call}")
    print(f"📈 Total tokens used: {total_tokens_used}\n")

    return reply

# =============================
# MAIN LOOP
# =============================

def main():
    print("🤖 Issue Lookup Agent (Fuzzy Matching Enabled)")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        reply = chat(user_input)
        print("Agent:", reply, "\n")

if __name__ == "__main__":
    main()