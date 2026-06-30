# Restructure Rollback Plan

## Trigger Condition
Use rollback if restructure-related failures exceed your threshold (for example: repeated test failures or blocked bench operations).

## Before Migration Work
1. Ensure clean tree.
2. Create a snapshot tag.

```powershell
./scripts/create_restructure_snapshot.ps1 -TagName pre-restructure-snapshot -IncludeDate
```

## Fast Safe Rollback (Non-destructive)
Switch to snapshot in detached mode for verification:

```powershell
./scripts/rollback_restructure.ps1 -Ref pre-restructure-snapshot-YYYYMMDD-HHMMSS
```

## Full Rollback (Destructive)
Reset current branch to a known-safe tag:

```powershell
./scripts/rollback_restructure.ps1 -Ref pre-restructure-snapshot-YYYYMMDD-HHMMSS -HardReset
```

## Soft Runtime Rollback
Set legacy mode while migration stabilizes:

```powershell
$env:THESIS_USE_LEGACY_LAYOUT = "1"
```

This keeps path handling on legacy data folders while code migration completes.

## Post-Rollback Verification
- Run unit tests.
- Run one bench smoke script.
- Run one diagnosis smoke prompt.
