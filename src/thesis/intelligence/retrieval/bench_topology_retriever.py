import yaml

from thesis.infra.paths import knowledge_base_dir


BENCH_DIR = knowledge_base_dir() / "Bench_Config"

GRAPH_FILE = (
    BENCH_DIR
    / "47D_graph_trail.yaml"
)

INFO_FILE = (
    BENCH_DIR
    / "47D_trail.yaml"
)

RULE_FILE = (
    BENCH_DIR
    / "47D_troubleshooting_trail.yaml"
)


# ==========================================
# LOAD FILES
# ==========================================

with open(GRAPH_FILE, "r") as f:
    GRAPH = yaml.safe_load(f)

with open(INFO_FILE, "r") as f:
    BENCH_INFO = yaml.safe_load(f)

with open(RULE_FILE, "r") as f:
    RULES = yaml.safe_load(f)


# ==========================================
# RETRIEVE BENCH CONTEXT
# ==========================================

def get_bench_context(query):

    query = query.lower()

    context = {
        "bench_info": BENCH_INFO,
        "connections": [],
        "rules": []
    }

    # ------------------------
    # Relevant graph edges
    # ------------------------

    for edge in GRAPH.get("edges", []):

        source = str(
            edge.get("source", "")
        ).lower()

        target = str(
            edge.get("target", "")
        ).lower()

        if (
            source in query
            or target in query
        ):
            context["connections"].append(
                edge
            )

    # ------------------------
    # Relevant troubleshooting rules
    # ------------------------

    for rule in RULES.get(
        "diagnostic_rules",
        []
    ):

        condition = str(
            rule.get(
                "condition",
                ""
            )
        ).lower()

        if any(
            word in condition
            for word in query.split()
        ):
            context["rules"].append(
                rule
            )

    return context