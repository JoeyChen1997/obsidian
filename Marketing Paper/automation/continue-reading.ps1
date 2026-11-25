[CmdletBinding()]
param([switch]$Install)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$taskName = 'Paperlist Research - Continue Reading'
$project = (Get-Item -LiteralPath (Split-Path -Parent $PSScriptRoot)).FullName
$configuredRunner = Join-Path $PSScriptRoot 'run-configured-codex.py'

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
        -Description 'Resume the local Paperlist ledger using the approved model configuration; no overlapping sessions.'
    return
}

$logDirectory = Join-Path $env:LOCALAPPDATA 'PaperlistResearch\automation'
$null = New-Item -ItemType Directory -Path $logDirectory -Force
$log = Join-Path $logDirectory 'reading.log'
function Write-RunLog([string]$Message) {
    Add-Content -Encoding UTF8 -LiteralPath $log -Value ('{0:o} {1}' -f (Get-Date), $Message)
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
    $python = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    $agent = Join-Path $project 'research_agent.py'
    $queue = Join-Path $project ([string]::Concat([char]0x9010,[char]0x7BC7,[char]0x6838,[char]0x8BFB,[char]0x6279,[char]0x6B21,[char]0x961F,[char]0x5217,'.md'))
    foreach ($file in @($python, $agent, $configuredRunner, $queue)) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            Write-RunLog 'blocked dependency missing: Python, runner, research agent or queue'
            exit 3
        }
    }
    if (-not (Test-Path -LiteralPath 'C:\paperlist' -PathType Container)) {
        Write-RunLog 'blocked source folder missing'
        exit 3
    }
    Set-Location -LiteralPath $project
    function Read-GraphStatus {
        $report = & $python -B -X utf8 $agent validate 2>$null
        if ($LASTEXITCODE -ne 0) { throw 'Knowledge base validation failed' }
        return ($report | Out-String | ConvertFrom-Json)
    }
    function Get-CoreCount($Report) { return [int]$Report.reading_states.core_read }
    function Get-CursorLine($Path) {
        $marker = [string]::new([char[]](0x5F53,0x524D,0x5165,0x53E3))
        $line = @(Get-Content -Encoding UTF8 -LiteralPath $Path | Where-Object { $_.StartsWith('- **' + $marker) })
        if ($line.Count -ne 1) { throw 'Reading queue cursor missing or ambiguous' }
        return $line[0]
    }

    # Decode the native validator's JSON as UTF-8.
    $OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
    $before = Read-GraphStatus
    Write-RunLog ('started core_read={0}' -f (Get-CoreCount $before))
    $beforeCursor = Get-CursorLine $queue
    $runnerSummary = & $python -B -X utf8 $configuredRunner
    $codexExit = $LASTEXITCODE
    if ($runnerSummary -match '^cli_exit=-?\d+ completed=[01] commands=\d+ command_errors=\d+ patches=\d+ clues=[a-z+]+$') {
        Write-RunLog $runnerSummary
    }
    $after = Read-GraphStatus
    $queueChanged = $beforeCursor -ne (Get-CursorLine $queue)
    $newMissing = @($after.missing_markdown_cards | Where-Object { $_ -notin @($before.missing_markdown_cards) })
    Write-RunLog ('finished runner_exit={0} core_read={1} exclusions={2} variants={3} queue_changed={4}' -f `
        $codexExit, (Get-CoreCount $after), $after.source_exclusion_records_checked, $after.variant_identity_pages_checked, $queueChanged)
    if ($codexExit -ne 0) { exit 4 }
    if ($newMissing.Count) {
        Write-RunLog 'validation incomplete: new graph entries lack their markdown cards'
        exit 11
    }
    if (-not $queueChanged) { exit 10 }
    exit 0
} catch {
    Write-RunLog ('runner error: ' + $_.Exception.GetType().Name + '; inspect the configuration and research_agent.py validate before retrying')
    exit 5
} finally {
    if ($locked) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
