"""
bench_retriever.py

Bench identification from: b   

1. Full Bench Name
2. IP Address
"""

import os
import re
import pandas as pd
from pathlib import Path


# ==========================================
# LOAD BENCH DATABASE
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

FILE_PATH = (
    BASE_DIR
    / "knowledgeBase"
    / "Bench_Mapping.csv"
)

print("Loading Bench Mapping...")

df = pd.read_csv(FILE_PATH)


df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

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
                "ip": row["ip"]
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
        "ip": row["ip"]
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