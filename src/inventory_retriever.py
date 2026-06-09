"""
inventory_retriever.py

Simple and stable inventory retriever
"""

import os
import re
import pandas as pd

# =============================
# PATH CONFIG
# =============================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_PATH = os.path.join(BASE_DIR, "knowledgeBase", "TB_Inventory.csv")

# =============================
# LOAD CSV
# =============================

print("📂 Loading TB inventory...")

df = pd.read_csv(FILE_PATH, encoding="latin1")

# =============================
# CLEAN COLUMN NAMES
# =============================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# =============================
# CLEAN DATAFRAME
# =============================

df = df.dropna(how="all")

df = df[df["name"].notna()]

# Strip whitespace from all string cells
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

print(f"✅ Inventory loaded: {len(df)} rows")

# =============================
# CLEAN DEVICE NAMES
# =============================

def clean_device_name(value):
    """
    Clean device names while preserving model names.
    Examples:
    -------------------------
    VN5650 1000444
    -> VN5650
    LA 3505 1000500
    -> LA 3505
    EA-PS 2342 10B 1000445
    -> EA-PS 2342 10B
    """

    if pd.isna(value):
        return "No"

    value = str(value).strip()

    words = value.split()

    cleaned = []

    for word in words:

        # ✅ Remove ONLY long standalone IDs
        if word.isdigit() and len(word) >= 5:
            continue

        cleaned.append(word)

    return " ".join(cleaned)


# =============================
# EXTRACT BENCH SUFFIX
# =============================

def extract_suffix(name):
    """
    Examples:
    ABT-C-003WE -> 3we
    ABT-C-00483 -> 483
    """

    parts = str(name).split("-")

    if not parts:
        return ""

    suffix = parts[-1]

    suffix = suffix.lstrip("0")

    return suffix.lower()


# =============================
# BUILD RESPONSE
# =============================

def build_response(row):

    return {
        "bench": clean_device_name(row.get("name", "")),

        # Samples
        "sample1": clean_device_name(row.get("sample_1", "")),
        "sample2": clean_device_name(row.get("sample_2", "")),
        "sample3": clean_device_name(row.get("sample_3", "")),

        # Devices
        "vector1": clean_device_name(row.get("vector_box_1", "")),
        "vector2": clean_device_name(row.get("vector_box_2", "")),

        "relay": clean_device_name(row.get("relay_card", "")),

        "psu": clean_device_name(row.get("psu", "")),

        "netgear": clean_device_name(row.get("netgear", "")),

        "extras": [
            clean_device_name(row.get("extra_1", "")),
            clean_device_name(row.get("extra_2", "")),
            clean_device_name(row.get("extra_3", "")),
            clean_device_name(row.get("extra_4", ""))
        ],

        "lauterbach1": clean_device_name(row.get("lauterbach_1", "")),
        "lauterbach2": clean_device_name(row.get("lauterbach_2", "")),

        "pdu": clean_device_name(row.get("pdu", ""))
    }


# =============================
# MAIN SEARCH FUNCTION
# =============================

def get_bench_info(query):

    query = query.lower().strip()

    for _, row in df.iterrows():

        bench_name = str(row.get("name", "")).lower()

        # ✅ Full match
        if bench_name and bench_name in query:
            return build_response(row)

        # ✅ Short-form match
        suffix = extract_suffix(bench_name)

        if suffix and suffix in query:
            return build_response(row)

    return None