param(
    [string]$TagName = "pre-restructure-snapshot",
    [switch]$IncludeDate
)

if ($IncludeDate) {
    $date = Get-Date -Format "yyyyMMdd-HHmmss"
    $TagName = "$TagName-$date"
}

$hasChanges = git status --porcelain
if ($hasChanges) {
    Write-Host "Working tree has uncommitted changes. Commit or stash first." -ForegroundColor Yellow
    exit 1
}

git tag $TagName
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create tag: $TagName" -ForegroundColor Red
    exit 1
}

Write-Host "Snapshot created: $TagName" -ForegroundColor Green
Write-Host "Push tag with: git push origin $TagName"
