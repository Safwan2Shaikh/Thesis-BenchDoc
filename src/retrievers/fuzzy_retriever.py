"""
fuzzy_retriever.py

Historical issue retrieval using
RapidFuzz similarity matching.

Responsibilities:
- Load issue database
- Search similar issues
- Return best matches
"""

import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz

# ==========================================
# LOAD ISSUE DATABASE
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "processed_kb"
    / "cleaned_issues.csv"
)

print("Loading Issue Database...")

df = pd.read_csv(DATA_FILE)

print(
    f"SUCCESS - Loaded {len(df)} issue records"
)

# ==========================================
# RETRIEVAL CONFIGURATION
# ==========================================

TOP_K = 3

MIN_SCORE = 50

# ==========================================
# CALCULATE FUZZY SCORE
# ==========================================

def calculate_score(
    query,
    text
):
    """
    Combines multiple RapidFuzz
    matching strategies.
    """

    return (

        0.5 * fuzz.token_sort_ratio(
            query,
            text
        )

        +

        0.3 * fuzz.partial_ratio(
            query,
            text
        )

        +

        0.2 * fuzz.token_set_ratio(
            query,
            text
        )
    )

# ==========================================
# FIND SIMILAR ISSUES
# ==========================================

def find_similar_issues(
    query
):
    """
    Returns the most relevant
    historical incidents.
    """

    query = query.lower()

    results = []

    for _, row in df.iterrows():

        combined_text = str(
            row["combined"]
        ).lower()

        score = calculate_score(
            query,
            combined_text
        )

        results.append({

            "score": score,

            "issue":
                row.get(
                    "Issue",
                    ""
                ),

            "solution":
                row.get(
                    "Solution",
                    ""
                ),

            "root_cause":
                row.get(
                    "Root_Cause_Problem",
                    ""
                ),

            "symptoms":
                row.get(
                    "Symptoms_Observed",
                    ""
                )
        })

    # ==============================
    # SORT BY SCORE
    # ==============================

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # ==============================
    # APPLY THRESHOLD
    # ==============================

    filtered = [

        result

        for result in results

        if result["score"] >= MIN_SCORE

    ][:TOP_K]

    # ==============================
    # DEBUG OUTPUT
    # ==============================

    print("\n=== ISSUE RETRIEVAL ===")

    for result in filtered:

        print(

            f"{result['score']:.1f} | "
            f"{result['issue']}"

        )

    return filtered

# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    query = "vector hardware not detected"

    results = find_similar_issues(
        query
    )

    print("\nResults:\n")

    for result in results:

        print(result["issue"])
        print(result["root_cause"])
        print("-" * 60)