param(
    [Parameter(Mandatory = $true)]
    [string]$Ref,
    [switch]$HardReset
)

$dirty = git status --porcelain
if ($dirty) {
    Write-Host "Uncommitted changes detected. Commit or stash before rollback." -ForegroundColor Yellow
    exit 1
}

if ($HardReset) {
    Write-Host "Performing hard rollback to $Ref" -ForegroundColor Yellow
    git reset --hard $Ref
} else {
    Write-Host "Switching to $Ref in detached HEAD for safe verification" -ForegroundColor Cyan
    git switch --detach $Ref
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Rollback failed for ref: $Ref" -ForegroundColor Red
    exit 1
}

Write-Host "Rollback target ready: $Ref" -ForegroundColor Green
