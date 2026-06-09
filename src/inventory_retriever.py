"""
inventory_retriever.py

Handles testbench config + flexible matching
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_PATH = os.path.join(BASE_DIR, "knowledgeBase", "TB_Inventory.csv")

print("📂 Loading TB inventory...")

df = pd.read_csv(FILE_PATH, encoding="latin1", skiprows=1)

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

df = df.dropna(how="all")

print(f"✅ Inventory loaded: {len(df)} rows")


def extract_suffix(name):
    parts = str(name).split("-")
    return parts[-1].lstrip("0").lower() if parts else ""


def get_bench_info(query):
    query = query.lower()

    for _, row in df.iterrows():
        name = str(row.get("name", "")).lower()

        if name and name in query:
            return build(row)

        suffix = extract_suffix(name)
        if suffix and suffix in query:
            return build(row)

    return None


def build(row):
    return {
        "bench": row.get("name", ""),

        # ✅ Samples
        "sample1": row.get("sample_1", ""),
        "sample2": row.get("sample_2", ""),
        "sample3": row.get("sample_3", ""),

        # ✅ Devices
        "psu": row.get("psu", ""),
        "vector1": row.get("vector_box_1", ""),
        "vector2": row.get("vector_box_2", ""),
        "relay": row.get("relay_card", ""),
        "netgear": row.get("netgear", ""),
        "extras": row.get("extras", ""),
        "lauterbach1": row.get("lauterbach_1", ""),
        "lauterbach2": row.get("lauterbach_2", ""),
        "pdu": row.get("pdu", "")
    }
