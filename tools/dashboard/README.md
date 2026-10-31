# Live Dashboard

A small local web page that shows what AI agents running these skills have found, live: each
assessment's current mode, what the agent is doing right now (highlighted when it's waiting for you), the
status of every domain, findings by priority and state, changes made, and any active incident. When it
has nothing to show, it lists the folders it's watching.

For a full-assessment run, the **Kick-off settings** tab lists every kick-off question with its current
answer and where it was given (in the chat or in the dashboard). You can answer or change answers there
instead of typing them to the agent; after saving, tell the agent you've answered in the dashboard. It
also re-reads them at every checkpoint and confirms them with you before it acts. Answers to a completed
run are read-only, so the tab doubles as a record of how the run was set up.

Agents report using the [live reporting protocol](../../core/reporting-protocol.md). The dashboard is one
Python file with no dependencies (Python 3.9+).

## Run it

The easiest way is `scripts/assess.sh --dashboard`, which starts the dashboard, opens it, and starts the
assessment in one command. `scripts/assess.sh --stop` stops the dashboard however it was started. To run the dashboard on its own:

```sh
python3 tools/dashboard/dashboard.py serve --open
```

It prints:

- **Dashboard URL**, including the token, e.g. `http://127.0.0.1:8770/#token=…`. Open it in a browser.
  The token is in the URL fragment, which browsers never send to the server; the page moves it to session
  storage and removes it from the address bar.
- **Run folders**: it shows every `~/ai-security-reports/<run-id>/events*.jsonl` (change with `--reports`).
- **Events folder**, by default `~/.ai-security-dashboard/events/`.
- **HTTP endpoint**: `POST http://127.0.0.1:8770/api/events`.

Options: `--lan`, `--port`, `--data DIR` (or `AISS_DASHBOARD_DATA`), `--host`, `--allow-host`. The token is
generated on first run and stored in `<data>/token` (mode 600); set `AISS_DASHBOARD_TOKEN` to override it.

## Point an agent at it

Tell the agent, at the start of an assessment, one of:

- *"Report live events to the folder `~/.ai-security-dashboard/events/`."* Best for agents on the same
  machine (Claude Code, Codex, local agents). The agent appends JSON lines to a `.jsonl` file there.
- *"Report live events to `http://127.0.0.1:8770/api/events` with token `<token>`."* For agents that
  can make HTTP requests. Example:

```sh
curl -X POST http://127.0.0.1:8770/api/events \
  -H "Authorization: Bearer $AISS_DASHBOARD_TOKEN" -H "Content-Type: application/json" \
  -d '{"schema":"ai-security-skills/event/v1","assessment_id":"2026-01-15-nas",
       "type":"mode.changed","data":{"mode":"recommend"}}'
```

To see the dashboard with invented data, copy `examples/sample-events.jsonl` into the events folder.

## Reports

At the end of a run, the agent generates the final reports from the run folder:

```sh
python3 tools/dashboard/dashboard.py report ~/ai-security-reports/<run-id>
```

This writes `report.md` and `report.html` (owner-only permissions) and prints the number of systems,
serious problems (open P0–P2), warnings (open P3), and informational items (open P4), plus the file
paths. It works whether or not the dashboard was running.

Check event files without running the server:

```sh
python3 tools/dashboard/dashboard.py validate path/to/events.jsonl
```

Suggest kick-off answers detected on this computer (the launchers run this too):

```sh
python3 tools/dashboard/dashboard.py prefill [--data DIR] [--no-lookup]
```

It prints suggestions for three questions: **In-scope networks** (the /24 around this computer's address,
left out unless it's a private LAN address), **Internet edge** (this network's public address, from an
outside service: `api.ipify.org`, falling back to `ifconfig.me`; `--no-lookup` skips it), and
**Agents** (1). With `--data`, it also saves them to `kickoff-prefill.json` there, and the Kick-off settings
form fills them into unanswered questions. They become answers only when the user presses Save answers.
The dashboard itself never contacts anything outside this computer.

See what is on the dashboard port (the launchers run this before starting a dashboard):

```sh
python3 tools/dashboard/dashboard.py probe [--port 8770] [--data DIR]
```

It prints `free`, `current` (a dashboard from this copy, running this version, that accepts this data
folder's token), `outdated` (from another copy, or started before this copy's code changed),
`wrong_token` (started with another data folder), or `other` (not this dashboard). For `current` and
`outdated` it also prints who can view it and the project folder it runs from. The launchers reuse only
a `current` dashboard; for anything else they say what's on the port and stop.

## Security

The dashboard is a map of your weaknesses. It is built to stay private:

- **Localhost only by default.** To view it from another device on your LAN (for example when the agent
  runs on a computer without a screen), run with `--lan` (or `scripts/assess.sh --dashboard --lan`). It
  then listens on all interfaces, accepts this computer's LAN address and name, and prints a link for each.
  Plain HTTP means the page and token can be read by anyone who can watch your network traffic, so use LAN
  mode only on a network you trust and stop the dashboard when you're done. The more private alternative
  is to keep it local and use an SSH tunnel: `ssh -L 8770:127.0.0.1:8770 <that computer>`, then open the
  `127.0.0.1` link on your own computer. For other names or addresses, use `--host 0.0.0.0 --allow-host
  <name-or-ip>`. Never expose it to the internet or put it behind a public tunnel.
- **Token required** for reading state, posting events, and saving kick-off answers.
- **One narrow write.** The page itself can write only kick-off answers (`POST /api/kickoff`): validated
  like any event, screened for secrets, for a run that's still open, appended to that run's
  `events-dashboard.jsonl` (mode 600). It can't change findings or anything else the agent reported.
- **Host header check:** requests with an unexpected `Host` are refused, which blocks DNS-rebinding attacks
  from malicious web pages.
- **Untrusted content stays text.** Findings contain text from scanned systems (hostnames, labels, logs).
  The page renders everything with `textContent`, never as HTML, and a strict Content-Security-Policy
  blocks inline scripts.
- **Secret screening.** Events that look like they contain private keys, tokens, or passwords are rejected
  (HTTP) or skipped and listed as rejected (folder). This is a backstop; agents must redact anyway.
- **Plain files.** Everything is stored as JSON lines under the data directory (mode 700). Back it up or
  delete it like any other file.

Unlike the skills themselves, the dashboard's data is *your* data, so it will contain your real hostnames
and addresses. Keep the data directory out of this repository.

## Tests

```sh
python3 -m unittest discover -s tools/dashboard
```
