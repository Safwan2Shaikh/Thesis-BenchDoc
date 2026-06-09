"""
fuzzy_retriever.py

Issue-based retrieval using fuzzy matching
"""

import os
import pandas as pd
from rapidfuzz import fuzz

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "processed", "cleaned_issues.csv")

print("📂 Loading issue dataset...")
df = pd.read_csv(DATA_FILE)
print(f"✅ Loaded {len(df)} issue records")

TOP_K = 3
MIN_SCORE = 50


def find_similar_issues(query):
    query = query.lower()
    results = []

    for _, row in df.iterrows():
        text = row["combined"]

        score = (
            0.5 * fuzz.token_sort_ratio(query, text) +
            0.3 * fuzz.partial_ratio(query, text) +
            0.2 * fuzz.token_set_ratio(query, text)
        )

        results.append({
            "score": score,
            "issue": row["Issue"],
            "solution": row["Solution"],
            "root_cause": row.get("Root_Cause_Problem", ""),
            "symptoms": row.get("Symptoms_Observed", "")
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return [r for r in results if r["score"] >= MIN_SCORE][:TOP_K]