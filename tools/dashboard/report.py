#!/usr/bin/env python3
"""Write report.md and report.html for a run folder, then print the totals and file paths.

Standard library only; Python 3.9+.

  report.py RUN_DIR            (same as: dashboard.py report RUN_DIR)

RUN_DIR holds the run's events (events.jsonl, see core/reporting-protocol.md). The reports are written
next to them with owner-only permissions, because they describe the user's weaknesses.
"""
import html
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Load by path: isolated mode (python3 -I) doesn't put this folder on the import path.
_spec = importlib.util.spec_from_file_location("aiss_dashboard", Path(__file__).resolve().parent / "dashboard.py")
dashboard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dashboard)

SERIOUS = ("P0", "P1", "P2")
WARNING = ("P3",)
INFO = ("P4",)
PRIORITY_NAME = {"P0": "Suspected compromise", "P1": "Critical", "P2": "High", "P3": "Medium", "P4": "Low"}
DETAIL_FIELDS = [("component", "Component"), ("confidence", "Confidence"), ("state", "State"),
                 ("operation_class", "Operation class"), ("evidence_label", "Evidence label"),
                 ("evidence", "Evidence"), ("exposure", "Exposure"), ("summary", "Summary"),
                 ("recommendation", "Recommendation"), ("verification", "Verification"), ("rollback", "Rollback")]


def load_run(run_dir):
    events, rejected = [], []
    for path in sorted(Path(run_dir).glob("*.jsonl")):
        received = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
        with open(path, encoding="utf-8", errors="replace") as fh:
            for number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    events.append(dashboard.validate_event(json.loads(line), received.replace("+00:00", "Z")))
                except (json.JSONDecodeError, dashboard.InvalidEvent) as exc:
                    rejected.append(f"{path.name}:{number}: {exc}")
    return dashboard.aggregate(events, rejected), rejected


def label(value):
    return str(value).replace("_", " ") if value else "—"


def is_open(finding):
    return finding.get("state") not in dashboard.CLOSED_STATES


def totals(assessments):
    roots = [a for a in assessments if not a["parent"]]
    assets = [x for a in roots for x in a["assets"]]
    systems = len(assets) or len([a for a in assessments if a["skill"] != "full-assessment"]) or len(assessments)
    findings = [f for a in assessments for f in a["findings"]]
    open_findings = [f for f in findings if is_open(f)]
    return {
        "systems": systems,
        "serious": sum(f.get("priority") in SERIOUS for f in open_findings),
        "warnings": sum(f.get("priority") in WARNING for f in open_findings),
        "info": sum(f.get("priority") in INFO for f in open_findings),
        "resolved": len(findings) - len(open_findings),
        "changes": sum(len(a["changes"]) for a in assessments),
        "not_assessed": sum(d.get("status") == "not_assessed" for a in assessments for d in a["domains"]),
        "no_skill": sum(x.get("coverage") == "no_skill" for x in assets),
        "incidents": [a for a in assessments if a["incident"] and a["incident"].get("status") != "closed"],
    }


def actions(assessments):
    rows = [(f, a) for a in assessments for f in a["findings"] if is_open(f)]
    return sorted(rows, key=lambda r: (r[0].get("priority") or "P9", r[0]["id"]))


def gaps(assessments):
    items = []
    for a in assessments:
        for d in a["domains"]:
            if d.get("status") == "not_assessed":
                items.append(f"{a['target'] or a['id']}: domain {d['domain']} {d.get('title') or ''} not assessed"
                             + (f" ({d['note']})" if d.get("note") else ""))
        for x in a["assets"]:
            if x.get("coverage") in ("no_skill", "skipped", "out_of_scope", "pending"):
                items.append(f"{x.get('label') or x['id']}: {label(x.get('coverage'))}"
                             + (f" ({x['note']})" if x.get("note") else ""))
    return items


def period(assessments):
    starts = [a["started"] for a in assessments if a["started"]]
    ends = [a["updated"] for a in assessments if a["updated"]]
    return (min(starts) if starts else "—"), (max(ends) if ends else "—")


def kickoff_rows(assessments):
    """(question, answer, where it was answered) for each answered kick-off question of the run."""
    rows = []
    for a in assessments:
        if a["parent"] or not a.get("kickoff"):
            continue
        for key, question, choices, _ in dashboard.KICKOFF_FIELDS:
            answer = a["kickoff"].get(key)
            if answer:
                shown = dict(choices or ()).get(answer["value"], answer["value"])
                rows.append((question, shown, f"{answer['source']}, {answer['time'] or '—'}"))
    return rows


# ---------------------------------------------------------------- Markdown

def md_cell(value):
    return label(value).replace("|", "\\|").replace("\n", " ")


def markdown(state, run_dir, t, rejected):
    assessments = state["assessments"]
    roots = [a for a in assessments if not a["parent"]]
    start, end = period(assessments)
    out = [f"# Security assessment report: {', '.join(a['target'] or a['id'] for a in roots)}", "",
           f"Run folder: `{run_dir}`  ", f"Period: {start} to {end}  ", f"Generated: {dashboard._now()}", "",
           "> This report describes weaknesses in your systems. Store it privately and don't share it publicly.",
           "", "## At a glance", "",
           "| Systems | Serious problems (P0–P2) | Warnings (P3) | Informational (P4) | Resolved | Changes made |",
           "|---|---|---|---|---|---|",
           f"| {t['systems']} | {t['serious']} | {t['warnings']} | {t['info']} | {t['resolved']} | {t['changes']} |", ""]
    for a in t["incidents"]:
        out += [f"**Active incident ({label(a['incident']['status'])}) on {a['target'] or a['id']}:** "
                f"{a['incident'].get('summary') or ''}", ""]
    summaries = [a for a in roots if a["summary"]] or [a for a in assessments if a["summary"]]
    if summaries:
        out += ["## Summary", ""] + [f"{a['summary']}\n" for a in summaries]
    out += ["## Recommended actions", ""]
    rows = actions(assessments)
    if rows:
        out += ["| Priority | ID | System | Finding | Recommendation | Class |", "|---|---|---|---|---|---|"]
        out += [f"| {f.get('priority') or '—'} | {f['id']} | {md_cell(a['target'] or a['id'])} | {md_cell(f.get('title'))} "
                f"| {md_cell(f.get('recommendation') or f.get('summary'))} | {f.get('operation_class') or '—'} |"
                for f, a in rows]
    else:
        out.append("No open findings.")
    out.append("")
    assets = [x for a in roots for x in a["assets"]]
    if assets:
        out += ["## Inventory", "", "| System | Kind | Exposure | Skill | Coverage |", "|---|---|---|---|---|"]
        out += [f"| {md_cell(x.get('label') or x['id'])} | {md_cell(x.get('kind'))} | {md_cell(x.get('exposure'))} "
                f"| {md_cell(x.get('skill'))} | {md_cell(x.get('coverage'))} |" for x in assets]
        out.append("")
    gap_items = gaps(assessments)
    kickoff = kickoff_rows(assessments)
    if kickoff:
        out += ["## Kick-off choices", "", "| Question | Answer | Answered in |", "|---|---|---|"]
        out += [f"| {md_cell(q)} | {md_cell(v)} | {md_cell(w)} |" for q, v, w in kickoff] + [""]
    if gap_items:
        out += ["## Not covered", ""] + [f"- {g}" for g in gap_items] + [""]
    out += ["## Details", ""]
    for a in assessments:
        out += [f"### {a['skill'] or a['id']}: {a['target'] or a['id']}", "",
                f"Mode: {'completed' if a['completed'] else label(a['mode'])} · Started: {a['started'] or '—'}"
                + (f" · Part of run `{a['parent']}`" if a["parent"] else ""), ""]
        if a["domains"]:
            out += ["| Domain | Status | Note |", "|---|---|---|"]
            out += [f"| {d['domain']} {md_cell(d.get('title') or '')} | {md_cell(d.get('status'))} | {md_cell(d.get('note'))} |"
                    for d in a["domains"]]
            out.append("")
        for f in a["findings"]:
            out += [f"#### {f['id']}: {f.get('title') or '(untitled)'} ({f.get('priority') or '—'})", ""]
            out += [f"- **{name}:** {f[key]}" for key, name in DETAIL_FIELDS if f.get(key)]
            out.append("")
        if a["changes"]:
            out += ["**Changes made**", "", "| Time | Finding | Change | Class | Result | Approved by |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {c['time'] or '—'} | {c.get('finding_id') or '—'} | {md_cell(c['description'])} | "
                    f"{c['operation_class']} | {md_cell(c['result'])} | {md_cell(c.get('approved_by'))} |" for c in a["changes"]]
            out.append("")
    if rejected:
        out += ["## Events that could not be read", ""] + [f"- {r}" for r in rejected] + [""]
    out += ["---", "", "This report reflects only what was assessed, with the evidence available on the dates shown. "
            "It is not a guarantee that any system is secure."]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- HTML

CSS = """
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;color:#1d1f23;background:#f7f7f8;font-size:15px}
main{max-width:1100px;margin:0 auto;padding:24px 28px 60px;background:#fff}
h1{font-size:24px;margin:0 0 6px}h2{font-size:19px;margin:32px 0 10px;border-bottom:1px solid #e3e5e8;padding-bottom:4px}
h3{font-size:16px;margin:26px 0 8px}h4{font-size:14px;margin:18px 0 6px}
.muted{color:#6b7079}.warn{background:#fff6e5;border:1px solid #e8710a;padding:8px 12px;border-radius:6px}
.incident{border:2px solid #c62828;padding:10px 14px;border-radius:6px;margin:12px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.card{border:1px solid #e3e5e8;border-radius:8px;padding:12px}.card b{display:block;font-size:28px}
.card.serious b{color:#c62828}.card.warnings b{color:#b8860b}
table{border-collapse:collapse;width:100%;margin:8px 0}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #e3e5e8;vertical-align:top}
th{font-size:12px;color:#6b7079}.p{display:inline-block;padding:1px 7px;border-radius:9px;font-size:12px;font-weight:600;color:#fff;background:#6b7079}
.P0{background:#7a1020}.P1{background:#c62828}.P2{background:#e8710a}.P3{background:#c9a400;color:#111}
dl{display:grid;grid-template-columns:150px 1fr;gap:4px 12px;margin:6px 0 14px}dt{color:#6b7079}dd{margin:0;white-space:pre-wrap}
code{font-family:ui-monospace,Menlo,monospace;font-size:13px}td code{white-space:nowrap}
"""


def e(value):
    return html.escape(label(value))


def badge(priority):
    return f'<span class="p {html.escape(priority or "")}">{e(priority)}</span>' if priority else "—"


def table(headers, rows):
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def html_report(state, run_dir, t, rejected):
    assessments = state["assessments"]
    roots = [a for a in assessments if not a["parent"]]
    start, end = period(assessments)
    title = "Security assessment report: " + ", ".join(a["target"] or a["id"] for a in roots)
    p = [f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
         f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title>'
         f"<style>{CSS}</style></head><body><main>",
         f"<h1>{html.escape(title)}</h1>",
         f'<p class="muted">Run folder <code>{html.escape(str(run_dir))}</code> · {e(start)} to {e(end)} · '
         f"generated {e(dashboard._now())}</p>",
         '<p class="warn">This report describes weaknesses in your systems. Store it privately and don\'t share it '
         "publicly.</p>", "<h2>At a glance</h2>", '<div class="cards">']
    for key, name, cls in (("systems", "Systems", ""), ("serious", "Serious problems (P0–P2)", "serious"),
                           ("warnings", "Warnings (P3)", "warnings"), ("info", "Informational (P4)", ""),
                           ("resolved", "Resolved", ""), ("changes", "Changes made", "")):
        p.append(f'<div class="card {cls}"><b>{t[key]}</b>{html.escape(name)}</div>')
    p.append("</div>")
    for a in t["incidents"]:
        p.append(f'<div class="incident"><b>Active incident ({e(a["incident"]["status"])}) on '
                 f'{e(a["target"] or a["id"])}:</b> {e(a["incident"].get("summary") or "")}</div>')
    summaries = [a for a in roots if a["summary"]] or [a for a in assessments if a["summary"]]
    if summaries:
        p.append("<h2>Summary</h2>" + "".join(f'<p style="white-space:pre-wrap">{e(a["summary"])}</p>' for a in summaries))
    p.append("<h2>Recommended actions</h2>")
    rows = actions(assessments)
    p.append(table(["Priority", "ID", "System", "Finding", "Recommendation", "Class"],
                   [[badge(f.get("priority")), f"<code>{e(f['id'])}</code>", e(a["target"] or a["id"]), e(f.get("title")),
                     e(f.get("recommendation") or f.get("summary")), e(f.get("operation_class"))] for f, a in rows])
             if rows else "<p>No open findings.</p>")
    assets = [x for a in roots for x in a["assets"]]
    if assets:
        p.append("<h2>Inventory</h2>" + table(["System", "Kind", "Exposure", "Skill", "Coverage"],
                 [[e(x.get("label") or x["id"]), e(x.get("kind")), e(x.get("exposure")), e(x.get("skill")),
                   e(x.get("coverage"))] for x in assets]))
    gap_items = gaps(assessments)
    kickoff = kickoff_rows(assessments)
    if kickoff:
        p.append("<h2>Kick-off choices</h2>" + table(["Question", "Answer", "Answered in"],
                 [[e(q), e(v), e(w)] for q, v, w in kickoff]))
    if gap_items:
        p.append("<h2>Not covered</h2><ul>" + "".join(f"<li>{html.escape(g)}</li>" for g in gap_items) + "</ul>")
    p.append("<h2>Details</h2>")
    for a in assessments:
        p.append(f"<h3>{e(a['skill'] or a['id'])}: {e(a['target'] or a['id'])}</h3>")
        p.append(f'<p class="muted">Mode: {"completed" if a["completed"] else e(a["mode"])} · started {e(a["started"])}'
                 + (f" · part of run <code>{e(a['parent'])}</code>" if a["parent"] else "") + "</p>")
        if a["domains"]:
            p.append(table(["Domain", "Status", "Note"],
                           [[e(f"{d['domain']} {d.get('title') or ''}"), e(d.get("status")), e(d.get("note"))]
                            for d in a["domains"]]))
        for f in a["findings"]:
            p.append(f"<h4>{badge(f.get('priority'))} <code>{e(f['id'])}</code> {e(f.get('title'))}</h4><dl>"
                     + "".join(f"<dt>{html.escape(name)}</dt><dd>{e(f[key])}</dd>" for key, name in DETAIL_FIELDS
                               if f.get(key)) + "</dl>")
        if a["changes"]:
            p.append("<h4>Changes made</h4>" + table(["Time", "Finding", "Change", "Class", "Result", "Approved by"],
                     [[e(c["time"]), e(c.get("finding_id")), e(c["description"]), e(c["operation_class"]),
                       e(c["result"]), e(c.get("approved_by"))] for c in a["changes"]]))
    if rejected:
        p.append("<h2>Events that could not be read</h2><ul>"
                 + "".join(f"<li>{html.escape(r)}</li>" for r in rejected) + "</ul>")
    p.append('<hr><p class="muted">This report reflects only what was assessed, with the evidence available on the '
             "dates shown. It is not a guarantee that any system is secure.</p></main></body></html>")
    return "\n".join(p) + "\n"


def write_private(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_BINARY", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main(run_dir):
    run_dir = Path(run_dir).expanduser().resolve()
    if not run_dir.is_dir():
        print(f"report: {run_dir} is not a folder", file=sys.stderr)
        return 2
    state, rejected = load_run(run_dir)
    if not state["assessments"]:
        print(f"report: no valid events in {run_dir}", file=sys.stderr)
        return 1
    t = totals(state["assessments"])
    md_path, html_path = run_dir / "report.md", run_dir / "report.html"
    write_private(md_path, markdown(state, run_dir, t, rejected))
    write_private(html_path, html_report(state, run_dir, t, rejected))
    print(f"Systems found:     {t['systems']}")
    print(f"Serious problems:  {t['serious']}  (open P0–P2)")
    print(f"Warnings:          {t['warnings']}  (open P3)")
    print(f"Informational:     {t['info']}  (open P4)")
    if t["no_skill"] or t["not_assessed"]:
        print(f"Not covered:       {t['no_skill']} systems with no skill, {t['not_assessed']} domains not assessed")
    for a in t["incidents"]:
        print(f"ACTIVE INCIDENT:   {label(a['incident']['status'])} on {a['target'] or a['id']}")
    print(f"Report (HTML):     {html_path}")
    print(f"Report (Markdown): {md_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
