"""
agent_router.py

Determines whether a specialized
agent should be consulted.
"""

TRACE32_KEYWORDS = [

    "trace32",
    "t32",
    "lauterbach",
    "debugger",
    "breakpoint",
    "practice",
    "jtag",
    "cmm",
    "symbol",
    "attach",
    "debug"
]


def needs_trace32_agent(query):

    query = query.lower()

    return any(
        keyword in query
        for keyword in TRACE32_KEYWORDS
    )