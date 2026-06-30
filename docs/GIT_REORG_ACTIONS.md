# Git Reorganization Actions (Safe Sequence)

This file provides a practical sequence to normalize branch usage for thesis work.

## 1. Confirm Clean Working Tree

```powershell
git status --short --branch
```

If there are local edits, commit or stash first.

## 2. Fetch and Prune

```powershell
git fetch --all --prune
```

## 3. Confirm Canonical Main Branch

If your team agrees that `main` is canonical, keep `main` + `dev` as primary long-lived branches.

## 4. Keep `master` Read-Only (Temporary)

Do not delete immediately. Mark as legacy in docs and stop merging into it.

## 5. Enforce Branch Targets
- `feature/*`, `fix/*`, `chore/*` -> PR to `dev`
- `exp/*` -> PR to `dev` only with experiment note
- `dev` -> PR to `main` for milestone release

## 6. Tag Milestones

```powershell
git tag thesis-v0.4-unified-architecture
git push origin thesis-v0.4-unified-architecture
```

## 7. Local Branch Cleanup (Only merged branches)

```powershell
git branch --merged dev
git branch -d <merged-branch-name>
```

## 8. Optional Final Step (Later)
After team validation and CI updates, archive/delete `master`.
