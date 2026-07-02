# Streamlit UI

## Purpose

This UI is a lightweight Streamlit layer for the AI-assisted Radar ECU Testbench Troubleshooting System. It does not replace the existing chatbot, retrievers, diagnostic engine, or agent architecture. It reuses the current diagnosis workflow and provides a local testbench workspace for thesis demonstrations and testbench-PC usage.

## Installation

Activate the existing thesis environment:

```powershell
conda activate trail_test
```

Install the UI dependencies:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe -m pip install -r ui/requirements.txt
```

Required libraries:

- `streamlit`
- `pandas`
- `pyyaml`

## Launch

From the repository root:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe -m streamlit run ui/app.py
```

Streamlit will print a local browser URL, usually `http://localhost:8501`.

## User Flow

1. The home screen discovers testbenches dynamically from `data/knowledge_base/Bench_Config/`.
2. Select a testbench to open its workspace.
3. Use the tabs for chat, inventory, logged issues, and YAML configuration.
4. Use `← Change Testbench` to return to the home screen without losing chat history.
5. Select another testbench at any time.

## Project Structure

```text
ui/
  app.py              # Streamlit application
  requirements.txt    # UI-only dependencies
```

The UI reads:

```text
data/knowledge_base/
  Bench_Config/<bench>/
    trail.yaml
    graph_trail.yaml
    troubleshooting_trail.yaml
  TB_Inventory.csv
  Logged_Issues.csv
  Bench_mapping.csv
```

## Architecture Overview

The UI calls the existing workflow:

```python
thesis.workflows.diagnose_workflow.run(
    prompt,
    selected_bench=bench,
    include_external_agents=False,
    include_general_chunks=False,
)
```

This keeps the UI connected to the existing chatbot, retrievers, and diagnostic engine while avoiding a new chatbot framework.

For UI sessions:

- selected testbench is passed into the existing diagnosis workflow,
- inventory and issue tables are filtered to the selected testbench,
- topology/config retrieval uses only the selected bench folder,
- external agents such as Trace32 are disabled,
- general markdown chunk retrieval is disabled to avoid cross-bench context during UI demos.

## Chat History

Chat history is stored in `st.session_state["chat_history"]` as a dictionary keyed by testbench name. Switching benches preserves each bench's conversation for the current Streamlit session.

## Actions

The sidebar provides:

- `Run Diagnosis`: sends a diagnostic summary prompt through the existing assistant for the selected bench.
- `Refresh Data`: clears Streamlit's cached CSV/YAML/testbench discovery data.
- `Show Configuration`: expands YAML configuration panels.

## Error Handling

The UI handles these cases without crashing:

- missing `Bench_Config` folder,
- missing YAML files,
- YAML parsing errors,
- empty or missing CSV files,
- retrieval/LLM failures,
- file access errors.

Errors are shown with `st.warning`, `st.error`, or `st.info`.

## Troubleshooting

### Streamlit Is Not Installed

Run:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe -m pip install -r ui/requirements.txt
```

### No Testbenches Appear

Check that the folder exists:

```text
data/knowledge_base/Bench_Config/
```

Each testbench must be a subfolder, for example:

```text
data/knowledge_base/Bench_Config/RNG-C-0050F/
```

### Inventory Or Issues Are Empty

Verify the selected bench name matches the bench name in:

- `TB_Inventory.csv`
- `Logged_Issues.csv`

The UI performs exact case-insensitive matching after trimming whitespace.

### LLM Call Fails

The UI catches the error and displays it in the chat. For full LLM operation, make sure the existing environment variables used by the project are configured, especially `MODEL_FARM_API_KEY`.

### Trace32 Agent Is Not Called

This is intentional. The Streamlit UI disables external agents to reduce token usage and avoid external service failures during local demos.

## Future Improvements

- Add a small topology visualization for `graph_trail.yaml`.
- Add export of chat history per testbench.
- Add role-based quick prompts for PSU, PDU, PMB, Vector, and Trace32 checks.
- Add a read-only health-check result panel.
- Add editable YAML validation for bench maintainers.