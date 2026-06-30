from pathlib import Path


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    root = get_repo_root()
    new_data = root / "data"
    return new_data if new_data.exists() else root


def knowledge_base_dir() -> Path:
    root = get_repo_root()
    modern = root / "data" / "knowledge_base"
    legacy = root / "knowledgeBase"
    if modern.exists() and any(modern.iterdir()):
        return modern
    return legacy


def logs_dir() -> Path:
    root = get_repo_root()
    modern = root / "data" / "logs"
    legacy = root / "logfiles"
    if modern.exists() and any(modern.iterdir()):
        return modern
    return legacy


def processed_dir() -> Path:
    root = get_repo_root()
    modern = root / "data" / "processed"
    legacy = root / "processed_kb"
    if modern.exists() and any(modern.iterdir()):
        return modern
    return legacy
