<#
One command to start a full security assessment (PowerShell version of scripts/assess.sh).

  scripts/assess.ps1                ask which AI assistant to use and whether to start the live dashboard,
                                    then start the assistant with the kick-off prompt
  scripts/assess.ps1 -Stop          stop the dashboard

Options: -Agent claude|codex|gemini|print   skip the question and use this choice
         -Local | -Lan | -NoDashboard       skip the dashboard question: viewable from this computer only,
                                            from your LAN, or no dashboard
         -Port N                            dashboard port (default 8770)
         -NoLookup                          don't ask an outside service for your public address

Reports and run data go to ~/ai-security-reports/<run-id>/ (override with AISS_REPORTS).
Works with Windows PowerShell 5.1 and PowerShell 7 on Windows, macOS, and Linux. If scripts are blocked, run:
  powershell -ExecutionPolicy Bypass -File scripts\assess.ps1
#>
[CmdletBinding()]
param(
    [switch]$Stop,
    [string]$Agent = "",
    [switch]$Local,
    [switch]$Lan,
    [switch]$NoDashboard,
    [int]$Port = 8770,
    [switch]$NoLookup,
    [Alias("h")][switch]$Help
)

Set-StrictMode -Version 2
$ErrorActionPreference = "Stop"

if ($Help) {
    (Get-Content -LiteralPath $PSCommandPath -TotalCount 18 | Select-Object -Skip 1) -join "`n" | Write-Output
    exit 0
}
if ([int][bool]$Local + [int][bool]$Lan + [int][bool]$NoDashboard -gt 1) {
    [Console]::Error.WriteLine("Choose one of -Local, -Lan, or -NoDashboard."); exit 2
}

$OnWindows = ($PSVersionTable.PSVersion.Major -lt 6) -or $IsWindows
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Data = if ($env:AISS_DASHBOARD_DATA) { $env:AISS_DASHBOARD_DATA } else { Join-Path $HOME ".ai-security-dashboard" }
$Reports = if ($env:AISS_REPORTS) { $env:AISS_REPORTS } else { Join-Path $HOME "ai-security-reports" }
$KnownAgents = @("claude", "codex", "gemini")
$Access = if ($Local) { "local" } elseif ($Lan) { "lan" } else { "" }
# $null until answered: -Local and -Lan mean yes, -NoDashboard means no, otherwise the script asks.
$Dashboard = if ($Access) { $true } elseif ($NoDashboard) { $false } else { $null }
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

# Only one assessment at a time. The run file holds the PID of the process running it and that process's start
# time (so a reused PID isn't mistaken for it). assess.sh uses the same file. What to stop depends on how the
# previous run was started: assess.sh execs the assistant, so its process is the assistant, or that script
# still asking questions. assess.ps1 runs the assistant as a child process, possibly inside an interactive
# PowerShell window, which must be left open.
$RunFile = Join-Path $Data "assess.pid"
$Marker = "full-assessment skill"   # appears in the assistant's command line (the prompt)
function Get-StartTime([int]$Id) {
    if ($OnWindows) {
        $p = Get-Process -Id $Id -ErrorAction SilentlyContinue
        if ($p) { try { return $p.StartTime.ToUniversalTime().ToString("o") } catch { } }
        return ""
    }
    return ("" + (& env LC_ALL=C ps -p $Id -o lstart= 2>$null)).TrimEnd()
}
function Get-ChildIds([int]$Id) {
    if ($OnWindows) {
        return @(Get-CimInstance Win32_Process -Filter "ParentProcessId = $Id" -ErrorAction SilentlyContinue |
            ForEach-Object { [int]$_.ProcessId })
    }
    return @(& ps -A -o pid= -o ppid= | ForEach-Object {
        $f = "$_".Trim() -split '\s+'
        if ($f.Count -ge 2 -and $f[1] -eq "$Id") { [int]$f[0] }
    })
}
$targets = @()
$oldPid = 0
if (Test-Path -LiteralPath $RunFile) {
    $saved = @(Get-Content -LiteralPath $RunFile -TotalCount 2) + @("", "")
    $savedPid = "$($saved[0])".Trim(); $oldStart = "$($saved[1])".Trim()
    if ($savedPid -match '^\d+$' -and [int]$savedPid -ne $PID -and (Test-Running ([int]$savedPid)) -and
        $oldStart -and (Get-StartTime ([int]$savedPid)) -eq $oldStart) {
        $oldPid = [int]$savedPid
        $agents = @(Get-ChildIds $oldPid | Where-Object { (Get-ProcessCommandLine $_).Contains($Marker) })
        $oldCmd = Get-ProcessCommandLine $oldPid
        if ($oldCmd.Contains($Marker)) { $targets = @($oldPid) }
        elseif ($oldCmd -match 'assess\.(sh|ps1)') { $targets = $agents + @($oldPid) }
        else { $targets = $agents }   # an interactive PowerShell window: only its assistant, if one is running
    }
}
if ($targets.Count -gt 0) {
    Write-Output "Another assessment started by this script is still running (process $oldPid)."
    if (-not $Interactive) { Fail "Stop it first, or run this again from a terminal to be asked." }
    Write-Output "  1) Stop the previous run and start a new one"
    Write-Output "  2) Exit and leave the previous run alone"
    $choice = Read-Host "Choose 1-2"
    if ($choice -ne "1") { Write-Output "Nothing started."; exit 0 }
    foreach ($t in $targets) {
        # On Windows, stop the whole tree: npm installs assistants behind a cmd shim, so the child is cmd.exe.
        if ($OnWindows) { & taskkill /PID $t /T /F 2>$null | Out-Null }
        else { & kill $t 2>$null }
    }
    foreach ($t in $targets) {
        try { Wait-Process -Id $t -Timeout 5 -ErrorAction Stop } catch { Stop-Process -Id $t -Force -ErrorAction SilentlyContinue }
    }
    Write-Output "Previous run stopped. Its run folder and any dashboard it started are left as they are."
}
New-Item -ItemType Directory -Force -Path $Data | Out-Null
if (-not $OnWindows) { & chmod 700 $Data }
Set-Content -LiteralPath $RunFile -Value @("$PID", (Get-StartTime $PID)) -Encoding ascii

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

# Whether to start the live dashboard, and who may view it. A computer without a screen has no browser, so
# "this computer only" would mean nobody can see it unless they use an SSH tunnel.
if ($null -eq $Dashboard) {
    if (-not $Interactive) {
        $Dashboard = $false
    } else {
        Write-Output ""
        Write-Output "Start a live dashboard so you can watch the assessment in a web browser?"
        Write-Output "  1) Yes, viewable only from this computer (most private; from another computer, use an SSH tunnel:"
        Write-Output "     ssh -L ${Port}:127.0.0.1:${Port} <this computer>, then open the link on that computer)"
        Write-Output "  2) Yes, viewable from any device on my local network (choose this for a computer without a"
        Write-Output "     screen; the page is unencrypted on your network, so only on a network you trust)"
        Write-Output "  3) No dashboard"
        $choice = Read-Host "Choose 1-3"
        switch ($choice) {
            "1" { $Dashboard = $true; $Access = "local" }
            "2" { $Dashboard = $true; $Access = "lan" }
            "3" { $Dashboard = $false }
            default { Write-Output "Not a valid choice; nothing started."; exit 1 }
        }
    }
}

# Is something already on the dashboard port? Reuse it only if it's this copy's dashboard, running this
# version of the code, with this data folder's token; otherwise say what's there and stop.
$Running = ""
$StopCmd = "scripts/assess.ps1 -Stop"
if ($Port -ne 8770) { $StopCmd += " -Port $Port" }
$python = $null
if ($Dashboard) {
    $python = Find-Python
    if (-not $python) { Fail "The dashboard needs Python 3.9 or later (python3, python, or py -3), and none was found." }
    $extra = @($python | Select-Object -Skip 1)
    $probe = @(& $python[0] @extra -I (Join-Path $Repo "tools/dashboard/dashboard.py") probe --port $Port --data $Data) + @("", "", "")
    $probeStatus = "$($probe[0])".Trim(); $probeAccess = "$($probe[1])".Trim(); $probeRoot = "$($probe[2])".Trim()
    switch ($probeStatus) {
        "free" { }
        "current" {
            $Running = $probeAccess
            if ($Access -and $Access -ne $Running) {
                Write-Output "The dashboard already running on port $Port is set to '$Running', not '$Access'. To change it,"
                Write-Output "stop it first ($StopCmd) and run this again. Using it as it is."
            }
            $Access = $Running
        }
        "outdated" {
            $sameCopy = if ($OnWindows) { $probeRoot -ieq $Repo } else { $probeRoot -ceq $Repo }
            if ($sameCopy) {
                $msg = "A dashboard started before this copy was updated is running on port $Port, so it would show the old version."
            } elseif ($probeRoot -eq "unknown") {
                $msg = "A dashboard from an older version of this project is running on port $Port."
            } else {
                $msg = "A dashboard from another copy of this project is running on port ${Port}:`n  $probeRoot"
            }
            Fail "$msg`nStop it with '$StopCmd' and run this again, or use another port with -Port N."
        }
        "wrong_token" {
            Fail ("A dashboard is running on port $Port, but it was started with a different data folder, so this script " +
                "can't give you a working link to it.`nStop it with '$StopCmd' and run this again, or use another port with -Port N.")
        }
        default { Fail "Port $Port is in use by another program. Use another port with -Port N (for example -Port $($Port + 1))." }
    }
}

# Same as chmod 700: only the current user may read the reports.
New-Item -ItemType Directory -Force -Path $Reports | Out-Null
if ($OnWindows) {
    & icacls $Reports /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F" | Out-Null
} else {
    & chmod 700 $Reports
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

# Print the dashboard link inside a box of asterisks so it stands out before the assistant takes over the
# terminal. Colour only on a console, and never when NO_COLOR is set (https://no-color.org).
function Write-UrlBox([string]$Link) {
    $label = "Copy this link into your browser to open the dashboard:"
    $width = [Math]::Max($label.Length, $Link.Length)
    $stars = "*" * ($width + 4)
    $color = -not $env:NO_COLOR -and -not [Console]::IsOutputRedirected
    Write-Output ""
    Write-Output $stars
    if ($color) {
        Write-Host -NoNewline "* "; Write-Host -NoNewline -ForegroundColor Yellow $label.PadRight($width); Write-Host " *"
        Write-Host ("* " + "".PadRight($width) + " *")
        Write-Host -NoNewline "* "; Write-Host -NoNewline -ForegroundColor Cyan $Link.PadRight($width); Write-Host " *"
    } else {
        Write-Output ("* " + $label.PadRight($width) + " *")
        Write-Output ("* " + "".PadRight($width) + " *")
        Write-Output ("* " + $Link.PadRight($width) + " *")
    }
    Write-Output $stars
    Write-Output ""
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

# Suggested kick-off answers: the /24 around this computer's address, the network's public address (from an
# outside service, unless -NoLookup), and one agent. The user confirms them; the dashboard pre-fills them.
$Suggested = ""
if (-not $python) { $python = Find-Python }
if ($python) {
    $prefillArgs = @($python | Select-Object -Skip 1) + @("-I", (Join-Path $Repo "tools/dashboard/dashboard.py"), "prefill")
    if ($Dashboard) { $prefillArgs += @("--data", $Data) }
    if ($NoLookup) { $prefillArgs += "--no-lookup" }
    Write-Output ""
    if ($NoLookup) { Write-Output "Finding suggested kick-off answers (this computer's network)..." }
    else { Write-Output "Finding suggested kick-off answers (this computer's network and its public address)..." }
    $suggestions = @()
    try { $suggestions = @(& $python[0] @prefillArgs 2>$null | Where-Object { "$_".Trim() }) } catch { }
    if ($suggestions.Count -gt 0) {
        $suggestions | ForEach-Object { "  $_" } | Write-Output
        $Suggested = " Suggested kick-off answers detected on this computer: $($suggestions -join '; '). " +
            "Offer them as defaults, and record them only once I've confirmed or changed them."
    }
}

$DashboardNote = ""
if ($Dashboard) {
    New-Item -ItemType Directory -Force -Path $Data | Out-Null
    $log = Join-Path $Data "dashboard.log"
    if ($Running) {
        Write-Output "Using the dashboard that's already running on port $Port. To change who can view it, stop it first:"
        Write-Output "  $StopCmd"
    } else {
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
            if ($tries -ge 20 -or $proc.HasExited) { Fail "Dashboard didn't start; see $log and $(Join-Path $Data 'dashboard.err.log'). If port $Port is taken, use -Port N." }
            Start-Sleep -Milliseconds 250
        }
        Write-Output "Dashboard started. When you're done, stop it with: $StopCmd"
    }
    if ($env:AISS_DASHBOARD_TOKEN) { $token = $env:AISS_DASHBOARD_TOKEN }
    else { $token = (Get-Content -LiteralPath (Join-Path $Data "token") -TotalCount 1).Trim() }
    $url = "http://127.0.0.1:$Port/#token=$token"
    Write-UrlBox $url
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
        "so always write events there. I can also answer the kick-off questions in the dashboard's Kick-off settings tab, " +
        "even before you ask: read events-dashboard.jsonl in the run folder before asking, and ask only what's still " +
        "unanswered. Record the dashboard choice in the kick-off answers."
}

# Single quotes around the rule name: Windows PowerShell 5.1 doesn't escape double quotes in native-command arguments.
$Prompt = "Use the full-assessment skill from the ai-security-skills collection at $Repo " +
    "(skills/orchestration/full-assessment/SKILL.md; product skills are in dist/) to run a complete security " +
    "assessment of my network. Follow its 'Before anything else' rules: set up the run folder under $Reports first, " +
    "then ask me the kick-off questions, and don't scan or probe my network until I've answered them.$Suggested$DashboardNote " +
    "Don't change anything without my approval."

# The assistant takes over the terminal, so give the user time to copy the dashboard links first.
if ($Dashboard -and $Agent -ne "print" -and $Interactive) {
    Write-Output ""
    Write-Host -NoNewline "Press any key to start $Agent (Ctrl+C to cancel)... "
    try { [Console]::ReadKey($true) | Out-Null } catch { Read-Host | Out-Null }  # ReadKey fails in some hosts, e.g. the ISE
    Write-Output ""
}

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
