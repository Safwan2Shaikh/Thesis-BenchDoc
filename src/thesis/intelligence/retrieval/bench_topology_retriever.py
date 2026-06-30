import re
from functools import lru_cache
from pathlib import Path

import yaml

from thesis.infra.paths import knowledge_base_dir


BENCH_DIR = knowledge_base_dir() / "Bench_Config"

STANDARD_FILES = {
    "graph": "graph_trail.yaml",
    "info": "trail.yaml",
    "rules": "troubleshooting_trail.yaml",
}


def normalize_bench_name(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def _safe_load_yaml(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _bench_id_from_info(info, fallback):
    return str(info.get("bench", {}).get("id") or fallback).strip()


@lru_cache(maxsize=1)
def list_bench_configs():
    configs = {}
    if not BENCH_DIR.exists():
        return configs

    for folder in sorted(BENCH_DIR.iterdir()):
        if not folder.is_dir():
            continue

        paths = {
            key: folder / file_name
            for key, file_name in STANDARD_FILES.items()
        }
        if not any(path.exists() for path in paths.values()):
            continue

        info = _safe_load_yaml(paths["info"])
        bench_id = _bench_id_from_info(info, folder.name)
        configs[bench_id] = {
            "bench_id": bench_id,
            "folder": folder,
            "paths": paths,
            "available_files": [
                file_name
                for file_name in STANDARD_FILES.values()
                if (folder / file_name).exists()
            ],
        }

    return configs


def get_bench_config(bench):
    if not bench:
        return None

    normalized = normalize_bench_name(bench)
    for bench_id, config in list_bench_configs().items():
        candidates = {
            normalize_bench_name(bench_id),
            normalize_bench_name(config["folder"].name),
        }
        if normalized in candidates:
            return config
    return None


def has_bench_config(bench):
    return get_bench_config(bench) is not None


def _load_context_for_config(config, query):
    graph = _safe_load_yaml(config["paths"]["graph"])
    bench_info = _safe_load_yaml(config["paths"]["info"])
    rules = _safe_load_yaml(config["paths"]["rules"])
    query = str(query or "").lower()

    context = {
        "bench_id": config["bench_id"],
        "config_folder": str(config["folder"]),
        "bench_info": bench_info,
        "connections": [],
        "rules": [],
        "failure_modes": rules.get("failure_modes", {}),
        "dependencies": rules.get("dependencies", {}),
        "metadata": {
            "files": {
                key: str(path)
                for key, path in config["paths"].items()
                if path.exists()
            }
        },
    }

    query_words = {
        word
        for word in re.split(r"\W+", query)
        if word
    }

    for edge in graph.get("edges", []):
        source = str(edge.get("source", "")).lower()
        target = str(edge.get("target", "")).lower()
        relation = str(edge.get("relation", "")).lower()
        edge_text = " ".join([source, target, relation])

        if not query or source in query or target in query or any(word in edge_text for word in query_words):
            context["connections"].append(edge)

    for rule in rules.get("diagnostic_rules", []):
        condition = str(rule.get("condition", "")).lower()
        check_text = " ".join(str(item).lower() for item in rule.get("check_order", []))
        rule_text = f"{condition} {check_text}"

        if not query or any(word in rule_text for word in query_words):
            context["rules"].append(rule)

    return context


def get_bench_context(query, bench=None):
    if bench:
        config = get_bench_config(bench)
        if not config:
            return {
                "bench_id": bench,
                "bench_info": {},
                "connections": [],
                "rules": [],
                "failure_modes": {},
                "dependencies": {},
                "metadata": {
                    "error": "No bench config folder found"
                },
            }
        return _load_context_for_config(config, query)

    contexts = []
    for config in list_bench_configs().values():
        context = _load_context_for_config(config, query)
        if context["connections"] or context["rules"]:
            contexts.append(context)

    return {
        "bench_id": "general",
        "bench_info": {},
        "connections": [
            connection
            for context in contexts
            for connection in context["connections"]
        ],
        "rules": [
            rule
            for context in contexts
            for rule in context["rules"]
        ],
        "bench_contexts": contexts,
        "metadata": {
            "searched_benches": [
                context["bench_id"]
                for context in contexts
            ]
        },
    }