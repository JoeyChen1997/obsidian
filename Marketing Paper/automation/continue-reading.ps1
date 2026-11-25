[CmdletBinding()]
param([switch]$Install)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$taskName = 'Paperlist Research - Continue Reading'
$project = (Get-Item -LiteralPath (Split-Path -Parent $PSScriptRoot)).FullName
$promptFile = Join-Path $PSScriptRoot 'reading-prompt.md'

if ($Install) {
    if (Get-ScheduledTask -TaskName $taskName -TaskPath '\' -ErrorAction SilentlyContinue) {
        throw 'The Paperlist task already exists. Inspect it before replacing it.'
    }
    $powershellExe = Join-Path $PSHOME 'powershell.exe'
    $action = New-ScheduledTaskAction -Execute $powershellExe `
        -Argument ('-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -File "' + $PSCommandPath + '"') `
        -WorkingDirectory $project
    # A time trigger with no repetition duration repeats indefinitely.
    $trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(2)) -RepetitionInterval (New-TimeSpan -Minutes 30)
    $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) `
        -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 25)
    Register-ScheduledTask -TaskName $taskName -TaskPath '\' -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings `
        -Description 'Resume the local Paperlist reading ledger. Requires a signed-in Codex CLI; does not run overlapping sessions.'
    return
}

$logDirectory = Join-Path $env:LOCALAPPDATA 'PaperlistResearch\automation'
$null = New-Item -ItemType Directory -Path $logDirectory -Force
$log = Join-Path $logDirectory 'reading.log'
function Write-RunLog([string]$Message) {
    Add-Content -Encoding UTF8 -LiteralPath $log -Value ('{0:o} {1}' -f (Get-Date), $Message)
}

function Get-CodexLoginExit([string]$CliPath) {
    # Windows PowerShell 5.1 can turn native stderr into a terminating
    # RemoteException under Stop, even when the streams are redirected.
    $ErrorActionPreference = 'Continue'
    & $CliPath login status *> $null
    return $LASTEXITCODE
}

function Invoke-Reading([string]$CliPath, [string]$InputPrompt, [string]$Workspace) {
    $ErrorActionPreference = 'Continue'
    $InputPrompt | & $CliPath -a never exec --ignore-user-config --ephemeral --skip-git-repo-check `
        -C $Workspace -s workspace-write -c 'sandbox_workspace_write.network_access=false' `
        --color never - 2>&1 | ForEach-Object { $null = $_ }
    return $LASTEXITCODE
}

$mutex = [Threading.Mutex]::new($false, 'Local\PaperlistResearch.ContinueReading')
$locked = $false
try {
    try { $locked = $mutex.WaitOne(0) }
    catch [Threading.AbandonedMutexException] { $locked = $true }
    if (-not $locked) {
        Write-RunLog 'skipped existing runner'
        exit 0
    }
    $cli = Join-Path $env:APPDATA 'npm\codex.cmd'
    $python = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    $agent = Join-Path $project 'research_agent.py'
    foreach ($file in @($cli, $python, $agent, $promptFile)) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            Write-RunLog 'blocked dependency missing: Codex, Python, research agent or prompt'
            exit 3
        }
    }
    if (-not (Test-Path -LiteralPath 'C:\paperlist' -PathType Container)) {
        Write-RunLog 'blocked source folder missing'
        exit 3
    }
    if ((Get-CodexLoginExit $cli) -ne 0) {
        Write-RunLog 'blocked Codex CLI not signed in; run codex login in a local terminal'
        exit 2
    }

    Set-Location -LiteralPath $project
    function Read-GraphStatus {
        $report = & $python -B -X utf8 $agent validate 2>$null
        if ($LASTEXITCODE -ne 0) { throw 'Knowledge base validation failed' }
        return ($report | Out-String | ConvertFrom-Json)
    }
    function Get-CoreCount($Report) { return [int]$Report.reading_states.core_read }

    # UTF-8 both for the prompt on stdin and for the native validator's JSON.
    $OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
    $before = Read-GraphStatus
    Write-RunLog ('started core_read={0}' -f (Get-CoreCount $before))
    $prompt = Get-Content -Raw -Encoding UTF8 -LiteralPath $promptFile
    # Model calls use the signed-in account. Model-generated commands have
    # workspace write access, no direct network, and cannot ask for escalation.
    # Do not log tool payloads, source excerpts, or authentication data.
    $codexExit = Invoke-Reading $cli $prompt $project
    $after = Read-GraphStatus
    Write-RunLog ('finished codex_exit={0} core_read={1} exclusions={2} variants={3}' -f `
        $codexExit, (Get-CoreCount $after), $after.source_exclusion_records_checked, $after.variant_identity_pages_checked)
    if ($codexExit -ne 0) { exit 4 }
    exit 0
} catch {
    Write-RunLog ('runner error: ' + $_.Exception.GetType().Name + '; inspect the configuration and research_agent.py validate before retrying')
    exit 5
} finally {
    if ($locked) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
