# Live Dashboard

A small local web page that shows what AI agents running these skills have found, live: each
assessment's current mode, the status of every domain, findings by priority and state, changes made, and
any active incident.

Agents report using the [live reporting protocol](../../core/reporting-protocol.md). The dashboard is one
Python file with no dependencies (Python 3.9+).

## Run it

The easiest way is `scripts/assess.sh --dashboard`, which starts the dashboard, opens it, and starts the
assessment in one command (`scripts/assess.sh --stop` stops it). To run the dashboard on its own:

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

Options: `--port`, `--data DIR` (or `AISS_DASHBOARD_DATA`), `--host`, `--allow-host`. The token is
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

## Security

The dashboard is a map of your weaknesses. It is built to stay private:

- **Localhost only by default.** To use it from another device on your LAN, run with `--host 0.0.0.0
  --allow-host <the-ip-or-name-you-browse-to>`. Never expose it to the internet or put it behind a public
  tunnel.
- **Token required** for reading state and posting events.
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
