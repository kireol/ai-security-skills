<#
One command to start a full security assessment (PowerShell version of scripts/assess.sh).

  scripts/assess.ps1                ask which AI assistant to use, then start it with the kick-off prompt
  scripts/assess.ps1 -Dashboard     also start the live dashboard and open it in your browser
  scripts/assess.ps1 -Stop          stop the dashboard

Options: -Agent claude|codex|gemini|print   skip the question and use this choice
         -Local | -Lan                      dashboard viewable from this computer only, or from your LAN
         -Port N                            dashboard port (default 8770)

Reports and run data go to ~/ai-security-reports/<run-id>/ (override with AISS_REPORTS).
Works with Windows PowerShell 5.1 and PowerShell 7 on Windows, macOS, and Linux. If scripts are blocked, run:
  powershell -ExecutionPolicy Bypass -File scripts\assess.ps1
#>
[CmdletBinding()]
param(
    [switch]$Dashboard,
    [switch]$Stop,
    [string]$Agent = "",
    [switch]$Local,
    [switch]$Lan,
    [int]$Port = 8770,
    [Alias("h")][switch]$Help
)

Set-StrictMode -Version 2
$ErrorActionPreference = "Stop"

if ($Help) {
    (Get-Content -LiteralPath $PSCommandPath -TotalCount 15 | Select-Object -Skip 1) -join "`n" | Write-Output
    exit 0
}
if ($Local -and $Lan) { [Console]::Error.WriteLine("Choose -Local or -Lan, not both."); exit 2 }

$OnWindows = ($PSVersionTable.PSVersion.Major -lt 6) -or $IsWindows
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Data = if ($env:AISS_DASHBOARD_DATA) { $env:AISS_DASHBOARD_DATA } else { Join-Path $HOME ".ai-security-dashboard" }
$Reports = if ($env:AISS_REPORTS) { $env:AISS_REPORTS } else { Join-Path $HOME "ai-security-reports" }
$KnownAgents = @("claude", "codex", "gemini")
$Access = if ($Local) { "local" } elseif ($Lan) { "lan" } else { "" }
$Interactive = -not [Console]::IsInputRedirected
$PidFile = Join-Path $Data "dashboard.pid"

function Fail([string]$Message, [int]$Code = 1) {
    [Console]::Error.WriteLine($Message)
    exit $Code
}

function Test-Command([string]$Name) {
    [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-ProcessCommandLine([int]$Id) {
    if ($OnWindows) {
        $p = Get-CimInstance Win32_Process -Filter "ProcessId = $Id" -ErrorAction SilentlyContinue
        if ($p) { return [string]$p.CommandLine }
        return ""
    }
    return [string](& ps -p $Id -o command= 2>$null)
}

function Test-Running([int]$Id) {
    [bool](Get-Process -Id $Id -ErrorAction SilentlyContinue)
}

if ($Stop) {
    # Prefer the process this script started; otherwise find whatever dashboard is listening on the port.
    $target = $null
    if (Test-Path -LiteralPath $PidFile) {
        $saved = (Get-Content -LiteralPath $PidFile -TotalCount 1)
        if ($saved -match '^\d+$' -and (Test-Running ([int]$saved))) { $target = [int]$saved }
    }
    if (-not $target) {
        $candidates = @()
        if ($OnWindows -and (Test-Command "Get-NetTCPConnection")) {
            $candidates = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty OwningProcess -Unique)
        } elseif (Test-Command "lsof") {
            $candidates = @(& lsof -ti "tcp:$Port" -sTCP:LISTEN 2>$null)
        } else {
            Write-Output "(Can't list listening processes here, so only a dashboard started by this script can be found.)"
        }
        foreach ($c in $candidates) {
            if ((Get-ProcessCommandLine ([int]$c)) -match 'dashboard\.py"? serve') { $target = [int]$c }
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
    if ($target) {
        try { Stop-Process -Id $target -ErrorAction Stop; Write-Output "Dashboard stopped."; exit 0 } catch { }
    }
    Write-Output "No dashboard is running on port $Port."
    exit 0
}

# Ask which assistant to use before starting anything, so "exit" leaves nothing running.
if (-not $Agent) {
    $installed = @($KnownAgents | Where-Object { Test-Command $_ })
    if (-not $Interactive) {
        $Agent = "print"
    } else {
        Write-Output "Which AI assistant should run the assessment?"
        $n = $installed.Count
        for ($i = 0; $i -lt $n; $i++) { Write-Output "  $($i + 1)) $($installed[$i])" }
        $printChoice = $n + 1; $exitChoice = $n + 2
        Write-Output "  $printChoice) Print the prompt so I can paste it into another assistant"
        Write-Output "  $exitChoice) Exit without doing anything"
        if ($n -eq 0) { Write-Output "(No supported assistant found on this computer: $($KnownAgents -join ' ').)" }
        $choice = Read-Host "Choose 1-$exitChoice"
        if ($choice -notmatch '^\d+$') { Write-Output "Not a valid choice; nothing started."; exit 1 }
        $choice = [int]$choice
        if ($choice -eq $exitChoice) { Write-Output "Nothing started."; exit 0 }
        elseif ($choice -eq $printChoice) { $Agent = "print" }
        elseif ($choice -ge 1 -and $choice -le $n) { $Agent = $installed[$choice - 1] }
        else { Write-Output "Not a valid choice; nothing started."; exit 1 }
    }
}
$Agent = $Agent.ToLowerInvariant()
if ($KnownAgents -contains $Agent) {
    if (-not (Test-Command $Agent)) { Fail "$Agent isn't installed on this computer." }
} elseif ($Agent -ne "print") {
    Fail "Unknown assistant: $Agent (use claude, codex, gemini, or print)" 2
}

# Who may view the dashboard. A headless computer has no browser, so "this computer only" would mean
# nobody can see it unless they use an SSH tunnel.
if ($Dashboard -and -not $Access) {
    if (-not $Interactive) {
        $Access = "local"
    } else {
        Write-Output ""
        Write-Output "Who should be able to view the dashboard?"
        Write-Output "  1) Only this computer (most private; from another computer, use an SSH tunnel:"
        Write-Output "     ssh -L ${Port}:127.0.0.1:${Port} <this computer>, then open the link on that computer)"
        Write-Output "  2) Any device on my local network (choose this for a computer without a screen;"
        Write-Output "     the page is unencrypted on your network, so only on a network you trust)"
        $choice = Read-Host "Choose 1-2"
        switch ($choice) {
            "1" { $Access = "local" }
            "2" { $Access = "lan" }
            default { Write-Output "Not a valid choice; nothing started."; exit 1 }
        }
    }
}

# Same as chmod 700: only the current user may read the reports.
New-Item -ItemType Directory -Force -Path $Reports | Out-Null
if ($OnWindows) {
    & icacls $Reports /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F" | Out-Null
} else {
    & chmod 700 $Reports
}

# The dashboard needs Python 3.9+. On Windows, "python3" may be the Microsoft Store stub, so check each candidate.
function Find-Python {
    foreach ($candidate in @(@("python3"), @("python"), @("py", "-3"))) {
        if (-not (Test-Command $candidate[0])) { continue }
        $extra = @($candidate | Select-Object -Skip 1)
        try {
            $ok = & $candidate[0] @extra -I -c "import sys; print(sys.version_info >= (3, 9))" 2>$null
            if ("$ok".Trim() -eq "True") { return ,$candidate }
        } catch { }
    }
    return $null
}

function Test-DashboardUp {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $connect = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if ($connect.AsyncWaitHandle.WaitOne(1000) -and $client.Connected) { return $true }
        return $false
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

function Open-Url([string]$Url) {
    try {
        if ($OnWindows) { Start-Process $Url }
        elseif ($IsMacOS) { & open $Url 2>$null }
        elseif (($env:DISPLAY -or $env:WAYLAND_DISPLAY) -and (Test-Command "xdg-open")) { & xdg-open $Url *> $null }
    } catch { }
}

function Quote-Arg([string]$Value) {
    # Start-Process joins arguments with spaces, so quote any that contain spaces (Windows user folders often do).
    if ($Value -match '[\s"]') { return '"' + ($Value -replace '"', '\"') + '"' }
    return $Value
}

$DashboardNote = ""
if ($Dashboard) {
    New-Item -ItemType Directory -Force -Path $Data | Out-Null
    $log = Join-Path $Data "dashboard.log"
    if (Test-DashboardUp) {
        Write-Output "Dashboard already running on port $Port. To change who can view it, stop it first:"
        Write-Output "  scripts/assess.ps1 -Stop"
    } else {
        $python = Find-Python
        if (-not $python) { Fail "The dashboard needs Python 3.9 or later (python3, python, or py -3), and none was found." }
        $pyArgs = @($python | Select-Object -Skip 1) + @("-I", (Join-Path $Repo "tools/dashboard/dashboard.py"), "serve")
        if ($Access -eq "lan") { $pyArgs += "--lan" }
        $pyArgs += @("--port", "$Port", "--data", $Data, "--reports", $Reports)
        $startArgs = @{
            FilePath               = $python[0]
            ArgumentList           = ($pyArgs | ForEach-Object { Quote-Arg $_ }) -join " "
            RedirectStandardOutput = $log
            RedirectStandardError  = (Join-Path $Data "dashboard.err.log")
            PassThru               = $true
        }
        if ($OnWindows) { $startArgs.WindowStyle = "Hidden" }
        $proc = Start-Process @startArgs
        Set-Content -LiteralPath $PidFile -Value $proc.Id -Encoding ascii
        $tries = 0
        while (-not (Test-DashboardUp)) {
            $tries++
            if ($tries -ge 20 -or $proc.HasExited) { Fail "Dashboard didn't start; see $log and $(Join-Path $Data 'dashboard.err.log')" }
            Start-Sleep -Milliseconds 250
        }
        Write-Output "Dashboard started. When you're done, stop it with: scripts/assess.ps1 -Stop"
    }
    if ($env:AISS_DASHBOARD_TOKEN) { $token = $env:AISS_DASHBOARD_TOKEN }
    else { $token = (Get-Content -LiteralPath (Join-Path $Data "token") -TotalCount 1).Trim() }
    $url = "http://127.0.0.1:$Port/#token=$token"
    Write-Output "Dashboard on this computer: $url"
    Open-Url $url
    # The dashboard flushes its startup lines at the end, so they may lag the port opening by a moment.
    $lanLines = @()
    for ($i = 0; $i -lt 8 -and $lanLines.Count -eq 0 -and $Access -eq "lan"; $i++) {
        if (Test-Path -LiteralPath $log) { $lanLines = @(Select-String -LiteralPath $log -Pattern '^On your LAN:' | ForEach-Object { $_.Line }) }
        if ($lanLines.Count -eq 0) { Start-Sleep -Milliseconds 250 }
    }
    if ($lanLines.Count -gt 0) {
        Write-Output "From another device on your network, open one of these:"
        $lanLines | ForEach-Object { "  " + ($_ -replace '^On your LAN:\s*', '') } | Write-Output
    }
    if ($Access -eq "lan") { $view = "this computer and other devices on the user's local network" }
    else { $view = "this computer only" }
    $DashboardNote = " A live dashboard is running (viewable from $view) and reads the run folder automatically, " +
        "so always write events there. I can also answer the kick-off questions in the dashboard's Kick-off settings tab; " +
        "record the dashboard choice in the kick-off answers."
}

# Single quotes around the rule name: Windows PowerShell 5.1 doesn't escape double quotes in native-command arguments.
$Prompt = "Use the full-assessment skill from the ai-security-skills collection at $Repo " +
    "(skills/orchestration/full-assessment/SKILL.md; product skills are in dist/) to run a complete security " +
    "assessment of my network. Follow its 'Before anything else' rules: set up the run folder under $Reports first, " +
    "then ask me the kick-off questions, and don't scan or probe my network until I've answered them.$DashboardNote " +
    "Don't change anything without my approval."

Set-Location -LiteralPath $Repo
switch ($Agent) {
    "claude" { & claude $Prompt; exit $LASTEXITCODE }
    "codex" { & codex $Prompt; exit $LASTEXITCODE }
    "gemini" { & gemini -i $Prompt; exit $LASTEXITCODE }
    "print" {
        Write-Output ""
        Write-Output "Paste this into your AI assistant (start it from $Repo so it can read the skills):"
        Write-Output ""
        Write-Output $Prompt
        try { Set-Clipboard -Value $Prompt; Write-Output ""; Write-Output "(Copied to the clipboard.)" } catch { }
    }
}
