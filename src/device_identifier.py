"""
device_identifier.py

Constraint-aware device identification

Phase 1:
- Explicit device extraction
- Bench validation

NO historical retrieval yet
"""

import pandas as pd


# ==========================================
# DEVICE KEYWORDS
# ==========================================

DEVICE_KEYWORDS = {

    # Trace32
    "t32": "Trace32",
    "trace32": "Trace32",
    "lauterbach": "Trace32",
    "debugger": "Trace32",

    # PSU
    "psu": "PSU",
    "power supply": "PSU",
    "ea-ps": "PSU",
    "pps": "PSU",

    # Vector
    "vector": "Vector",
    "can": "Vector",
    "canoe": "Vector",
    "canape": "Vector",
    "vn": "Vector",
    "vx": "Vector",

    # Relay
    "relay": "Relay",
    "pmb": "Relay",

    # PDU
    "pdu": "PDU",

    # ECU
    "ecu": "ECU"
}


# ==========================================
# NORMALIZE DEVICE
# ==========================================

def normalize_device(text):

    if pd.isna(text):
        return None

    text = str(text).lower()

    for key, value in DEVICE_KEYWORDS.items():

        if key in text:
            return value

    return None


# ==========================================
# EXTRACT BENCH DEVICES
# ==========================================

def extract_bench_devices(bench_info):

    if not bench_info:
        return []

    raw_devices = [

        bench_info.get("psu", ""),

        bench_info.get("vector1", ""),
        bench_info.get("vector2", ""),

        bench_info.get("relay", ""),

        bench_info.get("lauterbach1", ""),
        bench_info.get("lauterbach2", ""),

        bench_info.get("pdu", "")
    ]

    devices = []

    for dev in raw_devices:

        normalized = normalize_device(dev)

        if normalized:
            devices.append(normalized)

    return list(set(devices))


# ==========================================
# EXTRACT QUERY DEVICES
# ==========================================

def extract_query_devices(query):

    query = query.lower()

    found = []

    for key, value in DEVICE_KEYWORDS.items():

        if key in query:
            found.append(value)

    return list(set(found))


# ==========================================
# MAIN IDENTIFICATION
# ==========================================

def identify_devices(query, bench_info):

    bench_devices = extract_bench_devices(bench_info)

    query_devices = extract_query_devices(query)

    valid = []
    invalid = []

    for device in query_devices:

        if device in bench_devices:
            valid.append(device)
        else:
            invalid.append(device)

    return {
        "bench_devices": bench_devices,
        "query_devices": query_devices,
        "valid_devices": valid,
        "invalid_devices": invalid
    }