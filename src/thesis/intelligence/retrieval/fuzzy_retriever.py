"""
fuzzy_retriever.py

Historical issue retrieval using RapidFuzz similarity matching.
"""

import pandas as pd
from rapidfuzz import fuzz

from thesis.infra.paths import knowledge_base_dir, processed_dir


DATA_FILE = processed_dir() / "cleaned_issues.csv"
RAW_DATA_FILE = knowledge_base_dir() / "Logged_Issues.csv"

print("Loading Issue Database...")

df = pd.read_csv(DATA_FILE)

if RAW_DATA_FILE.exists():
    raw_df = pd.read_csv(RAW_DATA_FILE, encoding="latin1")
    raw_df.columns = (
        raw_df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    raw_df = raw_df.dropna(how="all")
else:
    raw_df = pd.DataFrame()

print(
    f"SUCCESS - Loaded {len(df)} issue records"
)


TOP_K = 3
MIN_SCORE = 50


def calculate_score(query, text):
    return (
        0.5 * fuzz.token_sort_ratio(query, text)
        + 0.3 * fuzz.partial_ratio(query, text)
        + 0.2 * fuzz.token_set_ratio(query, text)
    )


def _source_rows_for_bench(bench):
    if not bench:
        return df

    if raw_df.empty or "test_bench_name" not in raw_df.columns:
        return df.iloc[0:0]

    return raw_df[
        raw_df["test_bench_name"]
        .astype(str)
        .str.strip()
        .str.upper()
        == str(bench).strip().upper()
    ]


def _row_text(row):
    if "combined" in row and pd.notna(row.get("combined")):
        return str(row.get("combined", "")).lower()

    return " ".join(
        str(row.get(column, ""))
        for column in [
            "issue",
            "symptoms_observed",
            "root_cause_problem",
            "solution",
            "category",
            "device",
        ]
        if pd.notna(row.get(column, ""))
    ).lower()


def _field(row, *names):
    for name in names:
        value = row.get(name, "")
        if pd.notna(value):
            return value
    return ""


def find_similar_issues(query, bench=None):
    query = str(query or "").lower()
    results = []

    for _, row in _source_rows_for_bench(bench).iterrows():
        combined_text = _row_text(row)
        if not combined_text.strip():
            continue

        score = calculate_score(query, combined_text)

        results.append({
            "score": score,
            "bench": _field(row, "test_bench_name"),
            "issue": _field(row, "Issue", "issue"),
            "solution": _field(row, "Solution", "solution"),
            "root_cause": _field(row, "Root_Cause_Problem", "root_cause_problem"),
            "symptoms": _field(row, "Symptoms_Observed", "symptoms_observed"),
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    filtered = [
        result
        for result in results
        if result["score"] >= MIN_SCORE
    ][:TOP_K]

    print("\n=== ISSUE RETRIEVAL ===")

    for result in filtered:
        bench_label = f" | {result['bench']}" if result.get("bench") else ""
        print(f"{result['score']:.1f}{bench_label} | {result['issue']}")

    return filtered


if __name__ == "__main__":
    for result in find_similar_issues("vector hardware not detected"):
        print(result["issue"])
        print(result["root_cause"])
        print("-" * 60)