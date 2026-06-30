# AI-Assisted Radar ECU Troubleshooting System

## Overview
This thesis project provides a unified platform for:
- bench hardware health checks (PDU, PMB, PSU, Vector, PC ports), and
- LLM-assisted troubleshooting with retrieval from bench knowledge sources.

Bench scripting and LLM/RAG logic are now integrated in one modular package under src/thesis.

## Final Folder Structure

```text
Thesis/
  src/
    thesis/
      app/                        # app entry modules
      bench/
        checks/                   # per-device health checks
        controllers/              # hardware control interfaces
        orchestrator/             # unified bench orchestrator
      intelligence/
        orchestrator/             # chat/diagnostic orchestration
        retrieval/                # retrievers (inventory/issues/chunks/topology)
        llm/                      # LLM client
        agents/                   # specialist agents (Trace32)
      workflows/                  # high-level health/diagnose workflows
      infra/                      # shared path/config helpers
  data/
    knowledge_base/               # migrated bench knowledge source files
    logs/
      raw/                        # migrated runtime/diagnostic logs
      diagnostic/                 # generated diagnostic outputs
    processed/                    # processed artifacts (e.g. cleaned issues)
  scripts/
    run_health_check.py           # manual per-device health check runner
    run_diagnose.py               # interactive/non-interactive diagnosis runner
    create_restructure_snapshot.ps1
    rollback_restructure.ps1
  tests/
    unit/
    integration/
```

## How To Use

### 1. Run Health Checks (per device)

From repository root:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_health_check.py --device pc_ports
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_health_check.py --device vector
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_health_check.py --device psu --serial-port COM3
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_health_check.py --device pmb --serial-port COM3
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_health_check.py --device pdu --pdu-exe "D:\path\dcc-pdu-terminal.exe" --pdu-cfg "D:\path\PDU_VALUE_8-WAY.yaml"
```

Run all checks:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_health_check.py --device all
```

### 2. Run LLM Diagnosis

Interactive mode:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_diagnose.py --interactive
```

Single query mode:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe scripts/run_diagnose.py "ABT-C-00483 vector not detected"
```

### 3. Required Environment Variables (LLM)
Set these in your environment/.env for full LLM operation:
- MODEL_FARM_API_KEY
- TRACE32_AGENT_TOKEN (optional, for Trace32 routed prompts)
- TRACE32_AGENT_ID (optional, for Trace32 routed prompts)

## Data and Retriever Behavior
- Retrievers read from data/knowledge_base and data/processed.
- Diagnostic context combines:
  - bench inventory,
  - historical issues,
  - knowledge markdown chunks,
  - bench topology rules.

## Diagnostic Transparency
LLM diagnosis responses include a `DIAGNOSTIC EXECUTION TRACE` section showing:
- which knowledge/data paths were used,
- which retrievers ran,
- how many records/chunks/rules were returned,
- retriever elapsed time in milliseconds,
- whether external agents such as Trace32 were routed or used.

## Legacy Layout
The old pre-restructure folder layout is no longer kept in the active branch. It is preserved in Git under:

```powershell
git switch archive/legacy-layout
```

Return to the active refactored branch with:

```powershell
git switch feature/trace32-agent
```

## Testing
Run full suite:

```powershell
c:/Users/shs2rng/.conda/envs/trail_test/python.exe -m pytest tests/unit tests/integration -q
```

Current status: modular + integration tests are passing.

## Rollback
If needed, use:
- scripts/create_restructure_snapshot.ps1
- scripts/rollback_restructure.ps1

Rollback guide: docs/ROLLBACK_PLAN.md

## Development Workflow
See:
- docs/GIT_WORKFLOW.md
- docs/GIT_REORG_ACTIONS.md
- docs/RESEARCH_EXPERIMENTS.md
- CONTRIBUTING.md
