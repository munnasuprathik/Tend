# Cursor Local History Recovery Script
# This script helps recover unsaved changes from Cursor's Local History

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cursor Local History Recovery Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Frontend files that need recovery
$frontendFiles = @(
    "frontend/src/App.js",
    "frontend/src/components/AdminUserDetails.js",
    "frontend/src/components/MessageHistory.js",
    "frontend/src/components/PersonalityManager.js",
    "frontend/src/components/ScheduleManager.js",
    "frontend/src/index.js",
    "frontend/src/components/ErrorBoundary.js",
    "frontend/src/utils/dataSanitizer.js",
    "frontend/src/utils/safeRender.js"
)

# Backend files that need recovery
$backendFiles = @(
    "backend/server.py",
    "backend/server_updates.py",
    "backend/activity_tracker.py",
    "backend/version_tracker.py"
)

# Combine all files
$filesToRecover = $frontendFiles + $backendFiles

Write-Host "Frontend files to recover: $($frontendFiles.Count)" -ForegroundColor Yellow
Write-Host "Backend files to recover: $($backendFiles.Count)" -ForegroundColor Yellow
Write-Host "Total files to recover: $($filesToRecover.Count)" -ForegroundColor Yellow
Write-Host ""

# Check for backup files
Write-Host "Checking for backup files..." -ForegroundColor Yellow
$backupFiles = Get-ChildItem -Path . -Recurse -Filter "*.backup" -ErrorAction SilentlyContinue
if ($backupFiles) {
    Write-Host "Found backup files:" -ForegroundColor Green
    foreach ($backup in $backupFiles) {
        Write-Host "  - $($backup.FullName)" -ForegroundColor Green
    }
} else {
    Write-Host "No backup files found." -ForegroundColor Gray
}
Write-Host ""

# Find Cursor workspace storage
Write-Host "Looking for Cursor workspace storage..." -ForegroundColor Yellow
$cursorStorage = "$env:APPDATA\Cursor\User\workspaceStorage"
if (Test-Path $cursorStorage) {
    Write-Host "Cursor storage found: $cursorStorage" -ForegroundColor Green
    
    # Try to find workspace ID
    $workspacePath = (Get-Location).Path
    Write-Host "Current workspace: $workspacePath" -ForegroundColor Cyan
    
    # List workspace storage folders
    $workspaceFolders = Get-ChildItem -Path $cursorStorage -Directory -ErrorAction SilentlyContinue
    Write-Host "Found $($workspaceFolders.Count) workspace storage folders" -ForegroundColor Cyan
} else {
    Write-Host "Cursor storage not found at expected location." -ForegroundColor Red
}
Write-Host ""

# Recovery instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RECOVERY INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For EACH file below, follow these steps:" -ForegroundColor Yellow
Write-Host "1. Right-click the file in Cursor's Explorer" -ForegroundColor White
Write-Host "2. Select 'Local History' or 'Timeline'" -ForegroundColor White
Write-Host "3. Find the version from BEFORE your git rollback" -ForegroundColor White
Write-Host "4. Click 'Restore' or copy the content" -ForegroundColor White
Write-Host ""

Write-Host "FRONTEND FILES:" -ForegroundColor Cyan
$counter = 1
foreach ($file in $frontendFiles) {
    $exists = Test-Path $file
    $status = if ($exists) { "[OK] Exists" } else { "[X] Missing" }
    $color = if ($exists) { "Green" } else { "Red" }
    Write-Host "  $counter. $file [$status]" -ForegroundColor $color
    $counter++
}
Write-Host ""

Write-Host "BACKEND FILES:" -ForegroundColor Cyan
foreach ($file in $backendFiles) {
    $exists = Test-Path $file
    $status = if ($exists) { "[OK] Exists" } else { "[X] Missing" }
    $color = if ($exists) { "Green" } else { "Red" }
    Write-Host "  $counter. $file [$status]" -ForegroundColor $color
    $counter++
}
Write-Host ""

# Create recovery checklist file
$checklistPath = "RECOVERY_CHECKLIST.txt"
$checklist = @"
CURSOR LOCAL HISTORY RECOVERY CHECKLIST
========================================
Generated: $(Get-Date)

INSTRUCTIONS:
For each file below, use Cursor's Local History:
1. Right-click file → "Local History" or "Timeline"
2. Find version from BEFORE git rollback
3. Restore or copy content

FRONTEND FILES TO RECOVER:
"@

$counter = 1
foreach ($file in $frontendFiles) {
    $checklist += "`r`n$counter. [ ] $file"
    $counter++
}

$checklist += "`r`n`r`nBACKEND FILES TO RECOVER:"
foreach ($file in $backendFiles) {
    $checklist += "`r`n$counter. [ ] $file"
    $counter++
}

$checklist | Out-File -FilePath $checklistPath -Encoding UTF8
Write-Host "Recovery checklist saved to: $checklistPath" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TIP: Open the checklist file to track progress!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

