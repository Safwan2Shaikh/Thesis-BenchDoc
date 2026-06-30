"""
bench_retriever.py

Bench identification from: b   

1. Full Bench Name
2. IP Address
"""

import re
import pandas as pd
from thesis.infra.paths import knowledge_base_dir


# ==========================================
# LOAD BENCH DATABASE
# ==========================================

FILE_PATH = knowledge_base_dir() / "Bench_mapping.csv"

print("Loading Bench Mapping...")

def _load_bench_mapping():
    raw = pd.read_csv(
        FILE_PATH,
        header=None,
        names=["bench_name", "ip", "hostname"],
        dtype=str,
        keep_default_na=False,
        engine="python",
    )

    if not raw.empty and str(raw.iloc[0, 0]).strip().lower() in {"bench name", "bench_name"}:
        raw = raw.iloc[1:].reset_index(drop=True)

    raw = raw.map(
        lambda value: value.strip()
        if isinstance(value, str)
        else value
    )

    raw = raw[
        raw["bench_name"].astype(str).str.strip() != ""
    ]

    return raw


df = _load_bench_mapping()

print(
    f"SUCCESS - Bench mappings loaded: {len(df)}"
)


# ==========================================
# FIND BY FULL BENCH NAME
# ==========================================

def find_by_bench_name(query):

    query = query.lower()

    for _, row in df.iterrows():

        bench_name = str(
            row["bench_name"]
        ).strip()

        if bench_name.lower() in query:

            return {
                "bench_name": bench_name,
                "ip": row["ip"],
                "hostname": row.get("hostname", "")
            }

    return None


# ==========================================
# FIND BY IP
# ==========================================

def find_by_ip(query):

    ip_match = re.search(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        query
    )

    if not ip_match:
        return None

    ip = ip_match.group(0)

    match = df[
        df["ip"].astype(str) == ip
    ]

    if len(match) == 0:
        return None

    row = match.iloc[0]

    return {
        "bench_name": row["bench_name"],
        "ip": row["ip"],
        "hostname": row.get("hostname", "")
    }


# ==========================================
# MAIN FUNCTION
# ==========================================

def identify_bench(query):

    result = find_by_bench_name(
        query
    )

    if result:
        return result

    result = find_by_ip(
        query
    )

    if result:
        return result

    return None


def list_benches():
    benches = []

    for _, row in df.iterrows():
        bench_name = str(row.get("bench_name", "")).strip()
        if not bench_name or bench_name.lower() == "nan":
            continue

        benches.append({
            "bench_name": bench_name,
            "ip": row.get("ip", ""),
            "hostname": row.get("hostname", "")
        })

    return benches