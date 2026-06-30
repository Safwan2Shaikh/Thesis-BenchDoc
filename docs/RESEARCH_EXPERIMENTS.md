# Research Experiment Tracking

Use this lightweight format for every `exp/*` branch.

## Experiment Template
- Branch:
- Date:
- Hypothesis:
- Change:
- Dataset / Logs Used:
- Metrics / Evaluation Method:
- Result Summary:
- Decision: `promote` or `discard`
- Follow-up:

## Promotion Rule
Promote experiment code into `feature/*` only when:
- result is reproducible,
- value is clear for bench diagnosis,
- and code can be maintained in core modules.

## Storage
- Keep per-experiment notes in `docs/experiments/`.
- Keep benchmark outputs in `data/processed/experiments/`.

## Example File Names
- `docs/experiments/2026-07-01-hybrid-rag-retrieval.md`
- `docs/experiments/2026-07-03-prompt-routing-ablation.md`
