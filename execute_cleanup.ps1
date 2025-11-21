# RIS-2025-11-20-CLEANUP-001 Execution Script
# Mode: MOVE-ONLY (no deletions)
# Generated: 2025-11-20
# Compliance: SOC2 CC8.1, CC6.6 | HIPAA 164.308(a)(1)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$quarantineBase = "c:\CM-MULTI-REPO\credentialmate-quarantine"
$provenanceLog = @()
$moveCount = @{deletion=0; archive=0; "needs-review"=0}
$errors = @()

function Move-ToQuarantine {
    param(
        [string]$SourcePath,
        [string]$Bucket,
        [string]$OriginalRepo
    )

    $relativePath = $SourcePath -replace [regex]::Escape("c:\CM-MULTI-REPO\$OriginalRepo\"), ""
    $destDir = Join-Path $quarantineBase "$Bucket\$OriginalRepo\$(Split-Path $relativePath -Parent)"
    $destPath = Join-Path $quarantineBase "$Bucket\$OriginalRepo\$relativePath"

    if (Test-Path $SourcePath) {
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        try {
            Move-Item -Path $SourcePath -Destination $destPath -Force
            $script:provenanceLog += [PSCustomObject]@{
                file_moved = (Split-Path $SourcePath -Leaf)
                original_repo = $OriginalRepo
                original_path = $relativePath
                destination_path = "$Bucket\$OriginalRepo\$relativePath"
                timestamp_utc = $timestamp
                bucket = $Bucket
            }
            $script:moveCount[$Bucket]++
            return $true
        }
        catch {
            $script:errors += "Failed to move $SourcePath : $_"
            return $false
        }
    }
    else {
        return $false
    }
}

Write-Host "Starting RIS-2025-11-20-CLEANUP-001 Execution..." -ForegroundColor Cyan
Write-Host "Timestamp: $timestamp" -ForegroundColor Gray

# ============ DELETION BUCKET ============
Write-Host "`n=== DELETION BUCKET ===" -ForegroundColor Yellow

# credentialmate-docs (12 files)
$docsDeleteFiles = @(
    "issues\auto_issues_export.csv",
    "issues\auto_issues_new.csv",
    "issues\auto_issues_fixed.csv",
    "issues\auto_issues_regressions.csv",
    "issues\auto_issues_log.jsonl",
    "issues\agent_issue_wrapper.py",
    "issues\log_login_bug_fix.py",
    "issues\append_fix_status.py",
    "qa\auto\run_automated_qa_suite.py",
    "retrofit_script.py",
    "issues\REPORT_MANIFEST.txt",
    "qa\uat\ISSUES_LOG.csv"
)
foreach ($file in $docsDeleteFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-docs\$file" -Bucket "deletion" -OriginalRepo "credentialmate-docs"
}

# credentialmate-schemas (14 old migrations)
$oldMigrations = Get-ChildItem -Path "c:\CM-MULTI-REPO\credentialmate-schemas\alembic\old_migrations\*" -File -ErrorAction SilentlyContinue
foreach ($file in $oldMigrations) {
    Move-ToQuarantine -SourcePath $file.FullName -Bucket "deletion" -OriginalRepo "credentialmate-schemas"
}

# credentialmate-ai (backup files + nul)
$aiBackupPatterns = @(
    "governance\orchestration\COMPLIANCE.backup_*.csv",
    "governance\orchestration\METRICS_HISTORY.backup_*.csv",
    "governance\orchestration\TRACKERS.backup_*.csv",
    "governance\orchestration\SESSIONS.csv.backup-migration"
)
foreach ($pattern in $aiBackupPatterns) {
    $files = Get-ChildItem -Path "c:\CM-MULTI-REPO\credentialmate-ai\$pattern" -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Move-ToQuarantine -SourcePath $file.FullName -Bucket "deletion" -OriginalRepo "credentialmate-ai"
    }
}
# nul file
Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-ai\nul" -Bucket "deletion" -OriginalRepo "credentialmate-ai"

# credentialmate-infra (1 file)
Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-infra\_archive\scripts\deploy-to-production.sh" -Bucket "deletion" -OriginalRepo "credentialmate-infra"

# credentialmate-app deletion items
$appDeleteFiles = @(
    "accuracy_test_output.txt",
    "field_extraction_test_output.txt",
    "haiku_5doc_test_output.txt",
    "haiku_improved_gt_test_output.txt",
    "haiku_vs_sonnet_test_output.txt",
    "backend\nguyen_test_output.txt",
    "haiku_5doc_test_results.json",
    "haiku_accuracy_test_results.json",
    "haiku_improved_gt_test_results.json",
    "sonnet_accuracy_test_results.json",
    ".env.prod.tmp",
    "coverage.xml",
    "coverage.json",
    "backend\coverage.xml",
    "backend\coverage.json"
)
foreach ($file in $appDeleteFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-app\$file" -Bucket "deletion" -OriginalRepo "credentialmate-app"
}

# Move htmlcov directories
if (Test-Path "c:\CM-MULTI-REPO\credentialmate-app\htmlcov") {
    $htmlcovFiles = Get-ChildItem -Path "c:\CM-MULTI-REPO\credentialmate-app\htmlcov" -Recurse -File
    foreach ($file in $htmlcovFiles) {
        Move-ToQuarantine -SourcePath $file.FullName -Bucket "deletion" -OriginalRepo "credentialmate-app"
    }
}
if (Test-Path "c:\CM-MULTI-REPO\credentialmate-app\backend\htmlcov") {
    $htmlcovFiles = Get-ChildItem -Path "c:\CM-MULTI-REPO\credentialmate-app\backend\htmlcov" -Recurse -File
    foreach ($file in $htmlcovFiles) {
        Move-ToQuarantine -SourcePath $file.FullName -Bucket "deletion" -OriginalRepo "credentialmate-app"
    }
}

# Move ground truth backups
$gtBackups = Get-ChildItem -Path "c:\CM-MULTI-REPO\credentialmate-app\backend\tests\fixtures\ground_truth\backups\*" -File -ErrorAction SilentlyContinue
foreach ($file in $gtBackups) {
    Move-ToQuarantine -SourcePath $file.FullName -Bucket "deletion" -OriginalRepo "credentialmate-app"
}

# Move __pycache__ .pyc files
$pycFiles = Get-ChildItem -Path "c:\CM-MULTI-REPO\credentialmate-app" -Recurse -Filter "*.pyc" -File -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -like "*__pycache__*" }
foreach ($file in $pycFiles) {
    Move-ToQuarantine -SourcePath $file.FullName -Bucket "deletion" -OriginalRepo "credentialmate-app"
}

Write-Host "Deletion bucket: $($moveCount['deletion']) files moved" -ForegroundColor Green

# ============ ARCHIVE BUCKET ============
Write-Host "`n=== ARCHIVE BUCKET ===" -ForegroundColor Yellow

# credentialmate-docs (3 files)
$docsArchiveFiles = @(
    "deployment\20251120-AWS-Deploy-v1.md",
    "deployment\AWS Success Deploy 20251119-200000.md",
    "deployment\DB-Seed-AWS-success.md"
)
foreach ($file in $docsArchiveFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-docs\$file" -Bucket "archive" -OriginalRepo "credentialmate-docs"
}

# credentialmate-app (4 files)
$appArchiveFiles = @(
    "backend\app\routers\v2\audit_backup.py",
    "backend\app\routers\v2\notifications_backup.py",
    "terraform\terraform.tfstate.backup",
    "credentialmate-pricing.md.md"
)
foreach ($file in $appArchiveFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-app\$file" -Bucket "archive" -OriginalRepo "credentialmate-app"
}

# credentialmate-notification (2 files)
$notifArchiveFiles = @(
    ".github\workflows\notification-ci.yml",
    "src\queue_stub.py"
)
foreach ($file in $notifArchiveFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-notification\$file" -Bucket "archive" -OriginalRepo "credentialmate-notification"
}

# credentialmate-schemas (4 files)
$schemasArchiveFiles = @(
    "snapshots\v1.0.0\cme_activities.json",
    "snapshots\v1.0.0\documents.json",
    "snapshots\v1.0.0\licenses.json",
    "snapshots\v1.0.0\users.json"
)
foreach ($file in $schemasArchiveFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-schemas\$file" -Bucket "archive" -OriginalRepo "credentialmate-schemas"
}

# credentialmate-ai (5 files)
$aiArchiveFiles = @(
    "agents-legacy\agent-handoff-rules.md",
    "agents-legacy\claude-code-config.md",
    "agents-legacy\code-safety-rules.md",
    "agents-legacy\codex-config.md",
    "agents-legacy\cursor-ai-config.md"
)
foreach ($file in $aiArchiveFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-ai\$file" -Bucket "archive" -OriginalRepo "credentialmate-ai"
}

# credentialmate-infra (10 files)
$infraArchiveFiles = @(
    "_archive\terraform-legacy\main.tf",
    "_archive\terraform-legacy\variables.tf",
    "_archive\terraform-legacy\outputs.tf",
    "_archive\terraform-legacy\tfplan",
    "_archive\terraform-legacy\infrastructure-outputs.json",
    "_archive\terraform-legacy\terraform.tfvars.example",
    "_archive\legacy\orchestration_config.json",
    "_archive\README.md",
    "_archive\terraform-legacy\infra_terraform_legacy_v1.0.md",
    "terraform-legacy\.gitignore"
)
foreach ($file in $infraArchiveFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-infra\$file" -Bucket "archive" -OriginalRepo "credentialmate-infra"
}

Write-Host "Archive bucket: $($moveCount['archive']) files moved" -ForegroundColor Green

# ============ NEEDS-REVIEW BUCKET ============
Write-Host "`n=== NEEDS-REVIEW BUCKET ===" -ForegroundColor Yellow

# credentialmate-docs (2 files)
$docsReviewFiles = @(
    "compliance\CME-requirements-temp.csv",
    "compliance\HIPAA_SECURITY_PROJECT_PLAN_LOW_TRAFFIC.csv"
)
foreach ($file in $docsReviewFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-docs\$file" -Bucket "needs-review" -OriginalRepo "credentialmate-docs"
}

# credentialmate-notification (2 files)
$notifReviewFiles = @(
    ".github\workflows\code-scanning.yml",
    ".github\workflows\soc2-security-checks.yml"
)
foreach ($file in $notifReviewFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-notification\$file" -Bucket "needs-review" -OriginalRepo "credentialmate-notification"
}

# credentialmate-schemas (12 files)
$schemasReviewFiles = @(
    "synthetic_data\test_cme.json",
    "synthetic_data\test_licenses.json",
    "synthetic_data\test_users.json",
    "contracts\api_schemas\schema_api_contracts_v1.0.md",
    "contracts\event_schemas\schema_event_contracts_v1.0.md",
    "migrations\alembic\versions\schema_alembic_versions_v1.0.md",
    "migrations\schema_migrations_v1.0.md",
    "snapshots\current\schema_current_version_v1.0.md",
    "exports\credentialmate-app_database_schema.csv",
    "exports\credentialmate-app_state_cme_requirements_schema.csv",
    "migrations\alembic\alembic.ini",
    "migrations\alembic\env.py"
)
foreach ($file in $schemasReviewFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-schemas\$file" -Bucket "needs-review" -OriginalRepo "credentialmate-schemas"
}

# credentialmate-ai (16 files - CSV files for review)
$aiReviewFiles = @(
    "governance\orchestration\COMPLIANCE.csv",
    "governance\orchestration\METRICS_HISTORY.csv",
    "RIS_compliance.csv",
    "governance\orchestration\TASK_LOG_UPLOAD_AUTH_20251112.csv"
)
foreach ($file in $aiReviewFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-ai\$file" -Bucket "needs-review" -OriginalRepo "credentialmate-ai"
}

# credentialmate-infra (3 files)
$infraReviewFiles = @(
    "environments\dev\terraform.tfvars",
    "environments\prod\terraform.tfvars",
    "environments\staging\terraform.tfvars"
)
foreach ($file in $infraReviewFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-infra\$file" -Bucket "needs-review" -OriginalRepo "credentialmate-infra"
}

# credentialmate-app needs-review items (subset based on plan)
$appReviewFiles = @(
    "test-fresh-login.json",
    "test-full-register.json",
    "test-login.json",
    "test-provider-login.json",
    "test-register.json",
    "CHANGES_SUMMARY.txt",
    "REBUILD_READY.txt"
)
foreach ($file in $appReviewFiles) {
    Move-ToQuarantine -SourcePath "c:\CM-MULTI-REPO\credentialmate-app\$file" -Bucket "needs-review" -OriginalRepo "credentialmate-app"
}

Write-Host "Needs-review bucket: $($moveCount['needs-review']) files moved" -ForegroundColor Green

# ============ SAVE PROVENANCE LOG ============
Write-Host "`n=== SAVING PROVENANCE LOG ===" -ForegroundColor Cyan

$provenancePath = Join-Path $quarantineBase "manifests\provenance\RIS-2025-11-20-CLEANUP-001-provenance.json"
$provenanceLog | ConvertTo-Json -Depth 10 | Out-File -FilePath $provenancePath -Encoding UTF8

# Create summary CSV
$summaryPath = Join-Path $quarantineBase "manifests\provenance\RIS-2025-11-20-CLEANUP-001-summary.csv"
$provenanceLog | Export-Csv -Path $summaryPath -NoTypeInformation

# ============ FINAL SUMMARY ============
Write-Host "`n========== EXECUTION SUMMARY ==========" -ForegroundColor Cyan
Write-Host "Plan ID: RIS-2025-11-20-CLEANUP-001"
Write-Host "Timestamp: $timestamp"
Write-Host ""
Write-Host "BUCKET BREAKDOWN:" -ForegroundColor Yellow
Write-Host "  Deletion:     $($moveCount['deletion']) files"
Write-Host "  Archive:      $($moveCount['archive']) files"
Write-Host "  Needs-Review: $($moveCount['needs-review']) files"
Write-Host "  --------------------------------"
$total = $moveCount['deletion'] + $moveCount['archive'] + $moveCount['needs-review']
Write-Host "  TOTAL:        $total files moved"
Write-Host ""

if ($errors.Count -gt 0) {
    Write-Host "ERRORS: $($errors.Count)" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
}
else {
    Write-Host "ERRORS: 0" -ForegroundColor Green
}

Write-Host ""
Write-Host "RIS UPDATES:" -ForegroundColor Yellow
Write-Host "  - Provenance JSON: $provenancePath"
Write-Host "  - Summary CSV: $summaryPath"
Write-Host ""
Write-Host "Zero deletions performed. All files moved to quarantine." -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

# Return summary object
@{
    total_moved = $total
    bucket_breakdown = $moveCount
    errors = $errors.Count
    ris_updates = @($provenancePath, $summaryPath)
}
