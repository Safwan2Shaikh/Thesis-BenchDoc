# Git Workflow (Thesis Research Friendly)

## Branch Model
- `main`: stable thesis baseline (demo-ready, tagged milestones).
- `dev`: integration branch for validated features.
- `feature/*`: normal feature delivery.
- `exp/*`: research experiments (RAG variants, prompt methods, retrieval trials).
- `fix/*`: focused bug fixes.
- `chore/*`: repo maintenance, structure, docs, tooling.

## Naming Convention
- `feature/bench-<topic>`
- `feature/llm-<topic>`
- `feature/rag-<topic>`
- `exp/<hypothesis-short-name>`
- `fix/<area>-<issue>`

## Commit Convention
Use clear, scoped commits:
- `feat(bench): add pdu health check wrapper`
- `feat(rag): add hybrid retrieval experiment`
- `fix(pmb): handle serial timeout`
- `chore(structure): move retrievers into intelligence package`
- `docs(research): log ablation result for reranker`

## Merge Policy
- Merge `feature/*` into `dev` through PR.
- Merge `exp/*` into `dev` only if experiment has a result note and clear keep/drop decision.
- Merge `dev` into `main` for milestones only.

## Tags
Use milestone tags to track thesis progress:
- `thesis-v0.4-unified-architecture`
- `thesis-v0.5-rag-comparison`
- `thesis-v0.6-device-coverage`

## Pull Request Minimums
- Problem statement
- Scope and affected modules
- Test evidence (unit/integration/manual bench)
- Research note link (for `exp/*`)
- Safety note for bench-impacting changes

## Suggested Branch Cleanup
- Keep `main` and `dev` as primary branches.
- Keep old `master` as read-only for now, then archive/delete when team confirms no dependencies.

## Local Safety Commands

```powershell
git fetch --all --prune
git branch -vv
```

Before deleting an old local branch:

```powershell
git branch --merged dev
git branch -d <branch-name>
```

Force deletion only when intentionally discarding local-only work:

```powershell
git branch -D <branch-name>
```
