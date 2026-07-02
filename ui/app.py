from __future__ import annotations

import re
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

DEVICE_FIELD_LABELS = {
    "psu": "PSU",
    "vector_box_1": "Vector Box 1",
    "vector_box_2": "Vector Box 2",
    "relay_card": "Relay Card",
    "netgear": "Netgear",
    "pdu": "PDU",
    "lauterbach_1": "Lauterbach 1",
    "lauterbach_2": "Lauterbach 2",
}

DEVICE_VALUE_FIELDS = [
    "psu",
    "vector_box_1",
    "vector_box_2",
    "relay_card",
    "netgear",
    "pdu",
    "lauterbach_1",
    "lauterbach_2",
]


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
    .bench-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.25;
        margin-bottom: 0.4rem;
    }
    .bench-subtitle {
        font-size: 0.95rem;
        color: #334155;
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


def is_installed(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text not in {"", "no", "none", "nan", "null"}


def clean_device_value(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def truncate_words(text: str, max_words: int = 150) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).strip() + " ..."


def compact_assistant_response(raw_text: str) -> str:
    if not raw_text:
        return "Likely Cause:\nNo diagnosis was returned.\n\nRecommended Checks:\n• Verify bench power and communication links.\n• Re-run the diagnostic query.\n• Review bench configuration files."

    text = str(raw_text).replace("\r", "")

    # Hide retrieval/diagnostic traces and internal sections.
    cut_tokens = [
        "DIAGNOSTIC EXECUTION TRACE",
        "Issue Analysis",
        "Supporting Evidence",
        "Retriever",
        "Knowledge Sources",
        "Performance",
        "External Agents",
    ]
    for token in cut_tokens:
        if token in text:
            text = text.split(token, 1)[0]

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    bullet_lines = []
    for line in lines:
        normalized = line.lstrip()
        if normalized.startswith(("-", "•", "*")) or re.match(r"^\d+[\).]\s+", normalized):
            bullet_lines.append(re.sub(r"^[-•*]\s*|^\d+[\).]\s*", "", normalized).strip())

    prose_lines = [
        line
        for line in lines
        if line not in bullet_lines and not re.match(r"^(likely cause|recommended checks)\s*:?$", line.lower())
    ]
    prose_text = " ".join(prose_lines)
    prose_text = re.sub(r"\s+", " ", prose_text).strip()

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose_text) if s.strip()]
    likely_cause = " ".join(sentences[:2]).strip()
    if not likely_cause:
        likely_cause = "Likely cause is a communication or power-path issue on the selected bench."

    checks = []
    for item in bullet_lines:
        if item and item not in checks:
            checks.append(item)
        if len(checks) == 3:
            break

    if len(checks) < 3:
        fallback = [
            "Verify power state and cable connections of affected devices.",
            "Confirm interface/channel mapping and bench configuration.",
            "Restart the relevant hardware/software component and retest.",
        ]
        for item in fallback:
            if item not in checks:
                checks.append(item)
            if len(checks) == 3:
                break

    result = (
        "Likely Cause:\n"
        f"{likely_cause}\n\n"
        "Recommended Checks:\n"
        f"• {checks[0]}\n"
        f"• {checks[1]}\n"
        f"• {checks[2]}"
    )

    return truncate_words(result, max_words=150)


def get_connected_devices(bench: str) -> list[str]:
    inventory = get_inventory(bench)
    if inventory.empty:
        return []

    row = inventory.iloc[0]
    devices = []
    for field in DEVICE_VALUE_FIELDS:
        if field not in row:
            continue
        value = row.get(field)
        if not is_installed(value):
            continue
        cleaned = clean_device_value(value)
        if cleaned and cleaned not in devices:
            devices.append(cleaned)

    return devices


def get_connected_device_status(bench: str) -> list[dict[str, Any]]:
    inventory = get_inventory(bench)
    if inventory.empty:
        return []

    row = inventory.iloc[0]
    status = []

    for field, label in DEVICE_FIELD_LABELS.items():
        value = row.get(field, None)
        status.append(
            {
                "label": label,
                "installed": is_installed(value),
                "raw": value,
            }
        )

    return status


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
                (
                    "<div class='bench-card'>"
                    f"<div class='bench-title'>{bench}</div>"
                    f"<div class='bench-subtitle'>{available}/{len(CONFIG_FILES)} config files available</div>"
                    "</div>"
                ),
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
    connected_devices = get_connected_devices(bench)
    issues = get_logged_issues(bench)
    status = get_config_status(bench)
    connected_count = len(connected_devices)
    config_count = sum(1 for exists in status.values() if exists)

    st.subheader(f"Testbench: {bench}")

    c1, c3, c4 = st.columns(3)
    c1.metric("Connected Devices", connected_count)
    c3.metric("Config Files", config_count)
    c4.metric("Logged Issues", len(issues))


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

    response = compact_assistant_response(response)

    history.append({"role": "assistant", "content": response})
    st.session_state["last_diagnostic"][bench] = {
        "source": source,
        "prompt": prompt,
        "response": response,
    }


def render_chat_tab(bench: str) -> None:
    st.caption("Chat uses the existing troubleshooting assistant with retrieval scoped to the selected testbench. External agents are disabled in this UI.")
    st.markdown(f"**Current Context: {bench}**")

    for message in get_history(bench):
        role_label = "You" if message["role"] == "user" else "Assistant"
        with st.chat_message(message["role"]):
            st.markdown(f"**{role_label}:**")
            st.markdown(message["content"])

    prompt = st.chat_input(f"Ask about {bench}")
    if prompt:
        history = get_history(bench)
        history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown("**You:**")
            st.markdown(prompt)

        with st.chat_message("assistant"):
            progress = st.progress(0)
            with st.spinner("Thinking..."):
                progress.progress(25)
            with st.spinner("Searching documentation..."):
                progress.progress(55)
            try:
                with st.spinner("Running diagnostics..."):
                    response = run_diagnosis(
                        prompt,
                        selected_bench=bench,
                        include_external_agents=False,
                        include_general_chunks=False,
                    )
                    progress.progress(100)
            except Exception as exc:
                response = f"The assistant could not complete the request: {exc}"
                progress.progress(100)

            response = compact_assistant_response(response)

            progress.empty()
            st.markdown("**Assistant:**")
            st.markdown(response)

        history.append({"role": "assistant", "content": response})
        st.session_state["last_diagnostic"][bench] = {
            "source": "chat",
            "prompt": prompt,
            "response": response,
        }
        st.rerun()


def render_inventory_tab(bench: str) -> None:
    connected_devices = get_connected_devices(bench)
    if not connected_devices:
        st.info("No inventory rows found for this testbench.")
        return

    st.subheader("Connected Devices")
    st.metric("Connected Devices", len(connected_devices))

    for device in connected_devices:
        st.write(f"• {device}")


def render_issues_tab(bench: str) -> None:
    issues = get_logged_issues(bench)
    st.write(f"Logged issues: {len(issues)}")
    if issues.empty:
        st.info("No logged issues found for this testbench.")
        return

    drop_patterns = [
        "reporter",
        "author",
        "created_by",
        "createdby",
        "time_invested",
        "effort",
    ]

    filtered = issues.copy()
    columns_to_drop = [
        column
        for column in filtered.columns
        if any(pattern in str(column).lower() for pattern in drop_patterns)
    ]

    if columns_to_drop:
        filtered = filtered.drop(columns=columns_to_drop, errors="ignore")

    st.dataframe(filtered, use_container_width=True, hide_index=True)


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