# Contributing Guide

## Development Priority
This repository is thesis research software. Prioritize readability, traceability, and safe iteration over early packaging optimizations.

## Branching
- Use `feature/*`, `exp/*`, `fix/*`, `chore/*`.
- Target `dev` for normal merges.
- Merge `dev` to `main` only for milestone releases.

See [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) for details.

## Commit Quality
- Keep commits scoped and descriptive.
- Include intent in subject and rationale in body when needed.
- Avoid generic messages like "checkpoint" or "minor fixes".

## Experiments
For `exp/*` work, log experiment context and outcome.

See [docs/RESEARCH_EXPERIMENTS.md](docs/RESEARCH_EXPERIMENTS.md).

## Bench Safety
For changes affecting hardware controls, include:
- impacted device types,
- rollback behavior,
- manual test evidence.

## Pull Requests
Use the PR template and complete all required sections.
