param (
    [Parameter(Mandatory=$false)]
    [string]$Repo = ""
)

if (-not $Repo) {
    Write-Host "Usage: .\create_github_backlog.ps1 -Repo <owner/repo>" -ForegroundColor Yellow
    Write-Host "Example: .\create_github_backlog.ps1 -Repo svmx1718x/AI-Powered-Content-Management-System" -ForegroundColor Cyan
    exit 1
}

Write-Host "Creating backlog issues in $Repo..." -ForegroundColor Cyan

gh milestone create -R $Repo --title "Sprint-1" --description "Core pipeline, Auth, Intake, AI Enrichment, Search" 2>$null
gh milestone create -R $Repo --title "Sprint-2" --description "Metadata, Admin, Deletion, UI, Security, Freeze" 2>$null
gh milestone create -R $Repo --title "Sprint-3" --description "Spillover, Benchmarks, 38 TCs, Reports" 2>$null

$csv = Import-Csv "backlog\backlog.csv"

foreach ($row in $csv) {
    $title = "[$($row.ID)] $($row.title)"
    $body = @"
**Requirements**: $($row.req_IDs)
**Points**: $($row.story_points) | **Assignee**: $($row.assignee)
**Type**: $($row.type)

**Acceptance Criteria**:
$($row.acceptance_criteria)

**Linked TCs**:
$($row.linked_TCs)
"@
    Write-Host "Creating issue: $title" -ForegroundColor Green
    gh issue create -R $Repo --title $title --body $body --milestone $row.sprint
}

Write-Host "Completed backlog creation." -ForegroundColor Green
