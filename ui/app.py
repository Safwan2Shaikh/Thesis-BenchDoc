from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import yaml


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from thesis.workflows.diagnose_workflow import run as run_diagnosis


KB_DIR = ROOT / "data" / "knowledge_base"
BENCH_CONFIG_DIR = KB_DIR / "Bench_Config"
INVENTORY_FILE = KB_DIR / "TB_Inventory.csv"
ISSUES_FILE = KB_DIR / "Logged_Issues.csv"
CONFIG_FILES = ["trail.yaml", "graph_trail.yaml", "troubleshooting_trail.yaml"]


st.set_page_config(
    page_title="Radar ECU Testbench Assistant",
    page_icon="",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    .bench-card {
        border: 1px solid #d7dde5;
        border-radius: 8px;
        padding: 1rem;
        background: #ffffff;
        min-height: 6.5rem;
    }
    .metric-row {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem;
        background: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    st.session_state.setdefault("selected_testbench", None)
    st.session_state.setdefault("chat_history", {})
    st.session_state.setdefault("show_configuration", False)
    st.session_state.setdefault("last_diagnostic", {})


@st.cache_data(show_spinner=False)
def discover_testbenches() -> list[str]:
    if not BENCH_CONFIG_DIR.exists():
        return []

    benches = [
        path.name
        for path in BENCH_CONFIG_DIR.iterdir()
        if path.is_dir()
    ]

    return sorted(benches)


@st.cache_data(show_spinner=False)
def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path, encoding="latin1")
    except Exception:
        try:
            return pd.read_csv(path, encoding="latin1", engine="python", on_bad_lines="skip")
        except Exception:
            return pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_yaml_text(path: Path) -> tuple[str, Any | None, str | None]:
    if not path.exists():
        return "", None, "missing"

    try:
        text = path.read_text(encoding="utf-8")
        parsed = yaml.safe_load(text) or {}
        return text, parsed, None
    except Exception as exc:
        return "", None, str(exc)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    normalized = df.copy()
    normalized.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in normalized.columns
    ]
    return normalized


def filter_by_bench(df: pd.DataFrame, bench: str, possible_columns: list[str]) -> pd.DataFrame:
    if df.empty:
        return df

    normalized = normalize_columns(df)

    for column in possible_columns:
        if column in normalized.columns:
            return normalized[
                normalized[column]
                .astype(str)
                .str.strip()
                .str.upper()
                == bench.upper()
            ]

    return pd.DataFrame()


def get_inventory(bench: str) -> pd.DataFrame:
    return filter_by_bench(
        read_csv_safe(INVENTORY_FILE),
        bench,
        ["name", "bench_name", "test_bench_name"],
    )


def get_logged_issues(bench: str) -> pd.DataFrame:
    return filter_by_bench(
        read_csv_safe(ISSUES_FILE),
        bench,
        ["test_bench_name", "bench_name", "name"],
    )


def get_config_status(bench: str) -> dict[str, bool]:
    folder = BENCH_CONFIG_DIR / bench
    return {
        file_name: (folder / file_name).exists()
        for file_name in CONFIG_FILES
    }


def clear_cached_data() -> None:
    discover_testbenches.clear()
    read_csv_safe.clear()
    read_yaml_text.clear()


def select_bench(bench: str) -> None:
    st.session_state["selected_testbench"] = bench
    st.session_state["chat_history"].setdefault(bench, [])
    st.session_state["show_configuration"] = False


def render_home() -> None:
    st.title("Radar ECU Testbench Assistant")
    st.caption("Select a testbench to open its troubleshooting workspace.")

    benches = discover_testbenches()
    if not benches:
        st.warning(f"No testbench folders found under {BENCH_CONFIG_DIR}.")
        return

    columns = st.columns(3)
    for index, bench in enumerate(benches):
        with columns[index % 3]:
            status = get_config_status(bench)
            available = sum(1 for exists in status.values() if exists)
            st.markdown(
                f"<div class='bench-card'><strong>{bench}</strong><br>{available}/{len(CONFIG_FILES)} config files available</div>",
                unsafe_allow_html=True,
            )
            if st.button("Open Workspace", key=f"open-{bench}", use_container_width=True):
                select_bench(bench)
                st.rerun()


def render_sidebar(bench: str) -> None:
    st.sidebar.header("Selected Testbench")
    st.sidebar.write(bench)

    if st.sidebar.button("← Change Testbench", use_container_width=True):
        st.session_state["selected_testbench"] = None
        st.session_state["show_configuration"] = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.header("Actions")

    if st.sidebar.button("Run Diagnosis", use_container_width=True):
        prompt = f"Run a diagnostic summary for {bench}."
        run_chat_prompt(bench, prompt, source="diagnostic_action")
        st.rerun()

    if st.sidebar.button("Refresh Data", use_container_width=True):
        clear_cached_data()
        st.sidebar.success("Data cache refreshed.")

    if st.sidebar.button("Show Configuration", use_container_width=True):
        st.session_state["show_configuration"] = True


def render_summary(bench: str) -> None:
    inventory = get_inventory(bench)
    issues = get_logged_issues(bench)
    status = get_config_status(bench)

    st.subheader(f"Testbench: {bench}")

    col_files, col_inventory, col_issues = st.columns(3)
    with col_files:
        st.markdown("**Available Config Files**")
        for file_name, exists in status.items():
            st.write(f"{'✓' if exists else '-'} {file_name}")

    with col_inventory:
        st.metric("Inventory Records", len(inventory))

    with col_issues:
        st.metric("Logged Issues", len(issues))


def get_history(bench: str) -> list[dict[str, str]]:
    return st.session_state["chat_history"].setdefault(bench, [])


def run_chat_prompt(bench: str, prompt: str, source: str = "chat") -> None:
    history = get_history(bench)
    history.append({"role": "user", "content": prompt})

    try:
        response = run_diagnosis(
            prompt,
            selected_bench=bench,
            include_external_agents=False,
            include_general_chunks=False,
        )
    except Exception as exc:
        response = f"The assistant could not complete the request: {exc}"

    history.append({"role": "assistant", "content": response})
    st.session_state["last_diagnostic"][bench] = {
        "source": source,
        "prompt": prompt,
        "response": response,
    }


def render_chat_tab(bench: str) -> None:
    st.caption("Chat uses the existing troubleshooting assistant with retrieval scoped to the selected testbench. External agents are disabled in this UI.")

    for message in get_history(bench):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(f"Ask about {bench}")
    if prompt:
        run_chat_prompt(bench, prompt)
        st.rerun()


def render_inventory_tab(bench: str) -> None:
    inventory = get_inventory(bench)
    st.write(f"Inventory records: {len(inventory)}")
    if inventory.empty:
        st.info("No inventory rows found for this testbench.")
        return
    st.dataframe(inventory, use_container_width=True, hide_index=True)


def render_issues_tab(bench: str) -> None:
    issues = get_logged_issues(bench)
    st.write(f"Logged issues: {len(issues)}")
    if issues.empty:
        st.info("No logged issues found for this testbench.")
        return
    st.dataframe(issues, use_container_width=True, hide_index=True)


def render_configuration_tab(bench: str) -> None:
    folder = BENCH_CONFIG_DIR / bench
    if not folder.exists():
        st.warning(f"Configuration folder is missing: {folder}")
        return

    for file_name in CONFIG_FILES:
        path = folder / file_name
        text, parsed, error = read_yaml_text(path)
        with st.expander(file_name, expanded=st.session_state.get("show_configuration", False)):
            if error == "missing":
                st.warning("File is missing.")
            elif error:
                st.error(f"Could not parse YAML: {error}")
            else:
                st.code(text, language="yaml")
                if isinstance(parsed, dict):
                    st.caption(f"Top-level keys: {', '.join(parsed.keys())}")


def render_workspace(bench: str) -> None:
    render_sidebar(bench)
    render_summary(bench)

    tabs = st.tabs(["Chat", "Inventory", "Logged Issues", "Configuration"])
    with tabs[0]:
        render_chat_tab(bench)
    with tabs[1]:
        render_inventory_tab(bench)
    with tabs[2]:
        render_issues_tab(bench)
    with tabs[3]:
        render_configuration_tab(bench)


def main() -> None:
    init_state()
    selected = st.session_state.get("selected_testbench")

    if selected:
        render_workspace(selected)
    else:
        render_home()


if __name__ == "__main__":
    main()