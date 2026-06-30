# Thesis Project Structure (Research-First)

## Goals
- Keep development fast for ongoing thesis research.
- Keep hardware bench scripting and LLM/RAG diagnosis in one unified architecture.
- Support many upcoming device checks without import chaos.
- Keep room for future packaging and slimming later.

## Target Layout

```text
Thesis/
  src/
    thesis/
      app/
        cli.py
      domain/
        models/
        types.py
        errors.py
      workflows/
        health_check_workflow.py
        diagnose_workflow.py
      bench/
        orchestrator/
        checks/
        controllers/
        adapters/
      intelligence/
        orchestrator/
        llm/
        retrieval/
        agents/
      knowledge/
        loaders/
        index/
      infra/
        config.py
        paths.py
        logging.py
  data/
    knowledge_base/
    logs/
      raw/
      diagnostic/
    processed/
  tests/
    unit/
    integration/
    fixtures/
  scripts/
    run_health_check.py
    run_diagnose.py
  docs/
```

## Mapping From Current Repo

### Existing code to move
- `Health_Check/PDU/*` -> `src/thesis/bench/controllers` and `src/thesis/bench/checks`
- `Health_Check/PMB/*` -> `src/thesis/bench/controllers` and `src/thesis/bench/checks`
- `Health_Check/PSU/*` -> `src/thesis/bench/controllers` and `src/thesis/bench/checks`
- `Health_Check/PC_ports/*` -> `src/thesis/bench/checks` + `src/thesis/bench/adapters`
- `Health_Check/VectorHW/*` -> `src/thesis/bench/checks`
- `src/retrievers/*` -> `src/thesis/intelligence/retrieval`
- `src/agents/*` -> `src/thesis/intelligence/agents`
- `src/chat_agent.py` -> `src/thesis/intelligence/orchestrator/chat_service.py`
- `src/diagnostic_engine.py` -> `src/thesis/intelligence/orchestrator/diagnostic_engine.py`
- `src/llm_client.py` -> `src/thesis/intelligence/llm/client.py`
- `knowledgeBase/*` -> `data/knowledge_base/*`
- `logfiles/*` -> `data/logs/raw/*` (and curated outputs under `data/logs/diagnostic/*`)
- `processed_kb/*` -> `data/processed/*`

## Migration Strategy (Safe)
1. Create the new package skeleton first.
2. Move modules in small slices (one subsystem at a time).
3. Keep compatibility wrappers in old paths for a transition window.
4. Update imports after each slice.
5. Run tests and smoke scripts per slice.
6. Remove wrappers only after workflows are stable.

## Compatibility Rule
During migration, old entry scripts should keep working. Only remove legacy paths after at least one milestone tag confirms stability.

## Done Criteria For Final Consolidation
- All runtime code imported from `src/thesis/*`.
- `Health_Check` and old `src/*` become wrappers or removed.
- Bench checks and diagnosis can run from one CLI.
- Tests are split into unit and integration.
