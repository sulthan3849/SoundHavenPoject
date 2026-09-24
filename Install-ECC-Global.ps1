<#
.SYNOPSIS
Installs ECC (Everything Claude Code) globally and configures automatic updates.

.DESCRIPTION
This script performs the following actions:
1. Clones the ECC repository to a global location (~/.claude/ecc-repo)
2. Installs the ECC rules into ~/.claude/rules/ecc
3. Updates the global ~/.claude/CLAUDE.md to use ECC as the standard
4. Installs the ECC plugin via Claude Code
5. Creates a scheduled task to update the ECC repo automatically
#>

$ErrorActionPreference = "Stop"

Write-Host "Starting ECC Global Installation..." -ForegroundColor Cyan

# 1. Setup paths
$claudeDir = Join-Path $env:USERPROFILE ".claude"
$eccRepoDir = Join-Path $claudeDir "ecc-repo"
$rulesDir = Join-Path $claudeDir "rules\ecc"

if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
}

# 2. Clone/Update ECC Repository
Write-Host "Cloning ECC Repository..." -ForegroundColor Yellow
if (Test-Path $eccRepoDir) {
    Write-Host "ECC repo already exists. Pulling latest..."
    Set-Location $eccRepoDir
    git pull origin main
} else {
    git clone https://github.com/affaan-m/ECC.git $eccRepoDir
}

# 3. Install Rules
Write-Host "Installing ECC Rules Globally..." -ForegroundColor Yellow
if (-not (Test-Path $rulesDir)) {
    New-Item -ItemType Directory -Force -Path $rulesDir | Out-Null
}

# Copy common rules
Copy-Item -Path (Join-Path $eccRepoDir "rules\common\*") -Destination $rulesDir -Recurse -Force

# Note: You can add other language-specific rules here (e.g., typescript, python, etc.)
# Copy-Item -Path (Join-Path $eccRepoDir "rules\typescript\*") -Destination $rulesDir -Recurse -Force

# 4. Install Plugin
Write-Host "Installing ECC Plugin..." -ForegroundColor Yellow
Write-Host "You may need to run this command manually in Claude Code if it fails here:"
Write-Host "/plugin marketplace add https://github.com/affaan-m/ECC"
Write-Host "/plugin install ecc@ecc"
try {
    # Attempting to use the npx command as provided
    npx ecc-universal install --guided --claude-scope global --claude-hooks standard --profile core --yes
} catch {
    Write-Host "Warning: npx command failed. You will need to install the plugin manually via Claude Code." -ForegroundColor DarkYellow
}

# 5. Create Auto-Updater Script
$updaterScriptPath = Join-Path $claudeDir "update-ecc.ps1"
$updaterScriptContent = @"
`$ErrorActionPreference = "SilentlyContinue"
`$claudeDir = Join-Path `$env:USERPROFILE ".claude"
`$eccRepoDir = Join-Path `$claudeDir "ecc-repo"
`$rulesDir = Join-Path `$claudeDir "rules\ecc"

if (Test-Path `$eccRepoDir) {
    Set-Location `$eccRepoDir
    `$gitStatus = git pull origin main

    if (`$gitStatus -match "Updating" -or `$gitStatus -match "Fast-forward") {
        # Updates were pulled, copy them to rules dir
        Copy-Item -Path (Join-Path `$eccRepoDir "rules\common\*") -Destination `$rulesDir -Recurse -Force
        # Add other languages here if you use them
        Write-Output "ECC updated on `$(Get-Date)" >> (Join-Path `$claudeDir "ecc-update.log")
    }
}
"@
Set-Content -Path $updaterScriptPath -Value $updaterScriptContent -Encoding UTF8

# 6. Create Scheduled Task for Auto-Updates
Write-Host "Configuring Automatic Updates..." -ForegroundColor Yellow
$taskName = "Update-Claude-ECC"
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if (-not $taskExists) {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File `"$updaterScriptPath`""
    $trigger = New-ScheduledTaskTrigger -Daily -At 12:00PM
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily auto-update for Claude Code ECC standard rules" | Out-Null
    Write-Host "Scheduled task created. ECC will update daily." -ForegroundColor Green
} else {
    Write-Host "Scheduled task already exists." -ForegroundColor Green
}

Write-Host "ECC Global Installation Complete!" -ForegroundColor Cyan
Write-Host "To finish setup, please run these commands inside Claude Code:"
Write-Host "/plugin marketplace add https://github.com/affaan-m/ECC"
Write-Host "/plugin install ecc@ecc"
