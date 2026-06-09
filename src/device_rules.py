"""
device_rules.py

Device-aware troubleshooting rules
"""


def get_device_suggestions(bench_info, query):
    query = query.lower()
    suggestions = []

    psu = str(bench_info.get("psu", "")).lower()

    if "psu" in query:
        if "ea-ps" in psu:
            suggestions.append("Restart EA-PS PSU, check IP config, verify output channel")
        else:
            suggestions.append("Check PSU power and restart")

    vector = str(bench_info.get("vector1", "")).lower()

    if "vector" in query or "can" in query:
        if "vn56" in vector:
            suggestions.append("Restart Vector interface, check drivers and CAN config")

    if "relay" in query:
        suggestions.append("Check relay switching and wiring")

    if "laut" in query or "trace32" in query:
        suggestions.append("Restart Lauterbach, verify connection")

    return suggestions
