"""
inventory_retriever.py

Inventory lookup using exact bench name.
"""

import pandas as pd
from thesis.infra.paths import knowledge_base_dir

# ==========================================
# LOAD INVENTORY DATABASE
# ==========================================

FILE_PATH = knowledge_base_dir() / "TB_Inventory.csv"

print("Loading TB Inventory...")

df = pd.read_csv(
    FILE_PATH,
    encoding="latin1"
)

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

df = df.dropna(how="all")

df = df[df["name"].notna()]

df = df.map(
    lambda x:
    x.strip()
    if isinstance(x, str)
    else x
)

print(
    f"SUCCESS - Inventory loaded: {len(df)} rows"
)

# ==========================================
# DEVICE NAME CLEANING
# ==========================================

def clean_device_name(value):
    """
    Examples

    VN5650 1000444
        -> VN5650

    LA 3505 1000500
        -> LA 3505

    EA-PS 2342 10B 1000445
        -> EA-PS 2342 10B
    """

    if pd.isna(value):
        return ""

    value = str(value).strip()

    words = value.split()

    cleaned = []

    for word in words:

        if (
            word.isdigit()
            and len(word) >= 5
        ):
            continue

        cleaned.append(word)

    return " ".join(cleaned)

# ==========================================
# BUILD INVENTORY RESPONSE
# ==========================================

def build_response(row):

    return {

        "bench":
            clean_device_name(
                row.get("name", "")
            ),

        "sample1":
            clean_device_name(
                row.get("sample_1", "")
            ),

        "sample2":
            clean_device_name(
                row.get("sample_2", "")
            ),

        "sample3":
            clean_device_name(
                row.get("sample_3", "")
            ),

        "vector1":
            clean_device_name(
                row.get(
                    "vector_box_1",
                    ""
                )
            ),

        "vector2":
            clean_device_name(
                row.get(
                    "vector_box_2",
                    ""
                )
            ),

        "relay":
            clean_device_name(
                row.get(
                    "relay_card",
                    ""
                )
            ),

        "psu":
            clean_device_name(
                row.get("psu", "")
            ),

        "netgear":
            clean_device_name(
                row.get(
                    "netgear",
                    ""
                )
            ),

        "lauterbach1":
            clean_device_name(
                row.get(
                    "lauterbach_1",
                    ""
                )
            ),

        "lauterbach2":
            clean_device_name(
                row.get(
                    "lauterbach_2",
                    ""
                )
            ),

        "pdu":
            clean_device_name(
                row.get("pdu", "")
            )
    }

# ==========================================
# LOOKUP INVENTORY BY BENCH
# ==========================================

def get_bench_inventory(
    bench_name
):
    """
    Returns full inventory
    for a given bench.
    """

    match = df[
        df["name"]
        .astype(str)
        .str.strip()
        .str.upper()
        ==
        bench_name
        .strip()
        .upper()
    ]

    if len(match) == 0:

        return None

    return build_response(
        match.iloc[0]
    )