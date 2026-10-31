#!/usr/bin/env python3
"""Local dashboard for ai-security-skills live reporting (core/reporting-protocol.md).

Standard library only; Python 3.9+.

  dashboard.py serve [--lan | --host 127.0.0.1] [--port 8770] [--data DIR] [--reports DIR] [--open]
  dashboard.py validate FILE.jsonl ...
  dashboard.py report RUN_DIR      write report.md and report.html for a run and print the totals
  dashboard.py probe [--port 8770] [--data DIR]   what is on the port (used by the launchers; see cmd_probe)
  dashboard.py prefill [--data DIR]   suggest kick-off answers detected on this computer (see cmd_prefill)
"""
import argparse
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import socket
import sys
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCHEMA = "ai-security-skills/event/v1"
DEFAULT_DATA = Path(os.environ.get("AISS_DASHBOARD_DATA", Path.home() / ".ai-security-dashboard"))
DEFAULT_REPORTS = Path(os.environ.get("AISS_REPORTS", Path.home() / "ai-security-reports"))
DEFAULT_PORT = 8770
O_BINARY = getattr(os, "O_BINARY", 0)  # Windows only: no newline translation below the text layer
MAX_BODY = 1_000_000
MAX_TEXT = 4000
MAX_LIST = 50
STATIC_DIR = Path(__file__).resolve().parent / "static"
# Which copy of the project this is, and a fingerprint of this file as it was when the process started, so
# the launchers can tell a running dashboard from this copy and version apart from an older or other one.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
CODE_FINGERPRINT = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
SERVER_NAME = "ai-security-dashboard"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}

ASSESSMENT_ID = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
FINDING_ID = re.compile(r"^[A-Z][A-Z0-9]{0,9}-[0-9]{1,5}$")
SHORT = re.compile(r"^[A-Za-z0-9._-]{1,20}$")
ASSET_ID = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
SKILL_NAME = re.compile(r"^[a-z0-9-]{1,64}$")

MODES = ("discover", "recommend", "remediate", "respond")
DOMAIN_STATUS = ("in_progress", "pass", "finding", "not_assessed", "not_applicable", "accepted_risk")
PRIORITY = ("P0", "P1", "P2", "P3", "P4")
CONFIDENCE = ("confirmed", "likely", "potential")
FINDING_STATE = ("open", "resolved", "partially_resolved", "failed", "unverified", "accepted_risk")
OPERATION_CLASS = ("R", "C1", "C2", "C3")
EVIDENCE = ("observed", "vendor_documented", "third_party_documented", "user_reported", "inferred", "unknown")
CHANGE_RESULT = ("planned", "verified", "failed", "unverified", "rolled_back")
INCIDENT = ("suspected", "likely", "confirmed", "closed")
WAITING_ON = ("nothing", "user", "background_task")
EXPOSURE = ("internet", "vpn", "lan", "isolated", "unknown")
COVERAGE = ("pending", "in_progress", "assessed", "no_skill", "out_of_scope", "skipped")
CLOSED_STATES = ("resolved", "accepted_risk")
SOURCE = ("chat", "dashboard")

# The kick-off questions of the full-assessment skill, in the order they're asked. The dashboard's
# Kick-off tab is built from this list, so the skill's form, the protocol, and this list change together.
# Each entry: (key, question, choices or None for free text, hint). Choices are (value, label).
# (key, question, choices or None for free text, placeholder, description shown under the question).
# The questions and choices match the kick-off form in skills/orchestration/full-assessment/SKILL.md.
KICKOFF_FIELDS = [
    ("environment", "Environment", [("home", "Home"), ("office", "Office"), ("homelab", "Homelab"),
                                     ("mixed", "Mixed")], "",
     "What kind of network this is. It sets which risks matter most and how careful to be with shared or "
     "business systems."),
    ("in_scope", "In-scope networks", None, "Subnets or VLANs to assess, e.g. 192.0.2.0/24",
     "The only networks the agent may look at. Anything not listed here is left alone."),
    ("out_of_scope", "Out of scope", None, "Devices or ranges to skip",
     "Devices or address ranges inside the in-scope networks that the agent must not touch, for example "
     "someone else's devices or a work laptop."),
    ("internet_edge", "Internet edge", None, "Public IP or hostname to check from outside, or \"skip\"",
     "Your public address, so the agent can confirm what the internet can reach. It is checked only with "
     "your approval, from a place you approve. Enter \"skip\" to leave it out."),
    ("known_systems", "Known systems", None, "Anything you already know is there: firewall, NAS, cameras, ...",
     "Systems you already know about. This speeds up the inventory and helps the agent notice anything "
     "missing or unexpected."),
    ("discovery_level", "Discovery level", [("0", "0: passive, no probing (default)"),
                                            ("1", "1: light discovery (host and port checks)"),
                                            ("2", "2: service identification (banners, versions)")], "",
     "How actively the agent may look for devices. 0 uses only what already exists (your lists, the "
     "router's DHCP leases and ARP tables) and sends nothing to your devices. 1 adds slow ping and port "
     "checks on in-scope networks. 2 also reads service banners, versions, web page titles, and TLS "
     "certificates on open ports. Each level includes the ones below it. Levels 1 and 2 still need your "
     "approval before they start; password guessing and exploits are never used."),
    ("access_depth", "Access depth", [("none", "None: I'll run the commands (default)"),
                                      ("read_only", "Read-only credentials"),
                                      ("admin", "Admin credentials (only for approved changes)")], "",
     "Whether the agent gets its own access to your systems. None: it tells you what to run and you paste "
     "the output (safest, slower, sees only what you share). Read-only: it reads settings and logs itself "
     "(more complete, low risk if the accounts can't change anything). Admin: it can also make changes "
     "you approve (highest risk; only needed for remediation)."),
    ("access_available", "Access available", None,
     "Per system: SSH, API tokens, web logins, MCP tools. Never type a password or key here.",
     "Which kinds of access exist for which system, for example \"NAS: read-only SSH account\". Only the "
     "kind of access: keep the credentials themselves in environment variables, an SSH agent, or a "
     "credential store."),
    ("fragile_devices", "Fragile devices", None, "Devices that must not be probed",
     "Devices that could crash or misbehave if probed, such as medical or industrial equipment, old "
     "printers, or some cameras. The agent won't send anything to them."),
    ("time_window", "Time window", None, "When probing and changes are allowed",
     "When the agent may probe the network or make approved changes, for example \"weekday evenings\" or "
     "\"any time\". Outside it, the agent does neither."),
    ("goal", "Goal", [("discover", "Discover only"), ("recommend", "Discover and recommend"),
                      ("remediate", "Allow remediation with approval")], "",
     "How far the run goes. Discover only: find and report. Discover and recommend: also say what to fix "
     "and in what order. Allow remediation: the agent may also make fixes, each one only after you approve "
     "it."),
    ("agents", "Agents", None, "1 (default), or how many agents to run at once",
     "How many AI agents check systems at the same time. One is slowest and easiest to follow. Several "
     "finish sooner but use tokens much faster; only read-only checks run in parallel, and changes are "
     "always made one at a time."),
    ("pace", "Pace", [("phases", "In phases (stop at checkpoints)"), ("all_at_once", "All at once")], "",
     "In phases: the agent stops after the inventory and after each batch of a few systems, so you can "
     "review, pause, or resume later. Recommended for more than about five systems. All at once: it runs "
     "to the final report without stopping."),
    ("dashboard", "Live dashboard", [("none", "None"), ("local", "This computer only"),
                                     ("lan", "Devices on my local network (LAN)"),
                                     ("already_running", "Already running")], "",
     "Who can open this dashboard. This computer only is the most private. Devices on your local network "
     "is for a computer without a screen; the page is unencrypted on your network, so use it only on a "
     "network you trust."),
]
AGENT_COUNT = re.compile(r"^[1-9][0-9]?$")
# Kick-off answers the launcher can suggest. They pre-fill the dashboard form until the user saves answers.
PREFILL_FILE = "kickoff-prefill.json"
PREFILL_KEYS = ("in_scope", "internet_edge", "agents")
PUBLIC_ADDRESS_URLS = ("https://api.ipify.org", "https://ifconfig.me/ip")

# type -> {field: (kind, required)}; kind is "text", "list", a regex, or a tuple of allowed values.
EVENT_FIELDS = {
    "assessment.started": {"skill": ("text", True), "target": ("text", True), "skill_version": ("text", False),
                           "scope": ("text", False), "agent": ("text", False), "parent": (ASSESSMENT_ID, False)},
    "mode.changed": {"mode": (MODES, True), "note": ("text", False)},
    "domain.status": {"domain": (SHORT, True), "status": (DOMAIN_STATUS, True), "title": ("text", False),
                      "note": ("text", False)},
    "finding.upserted": {"id": (FINDING_ID, True), "title": ("text", False), "priority": (PRIORITY, False),
                         "confidence": (CONFIDENCE, False), "state": (FINDING_STATE, False),
                         "component": ("text", False), "operation_class": (OPERATION_CLASS, False),
                         "evidence_label": (EVIDENCE, False), "summary": ("text", False),
                         "evidence": ("text", False), "exposure": ("text", False),
                         "recommendation": ("text", False), "verification": ("text", False),
                         "rollback": ("text", False)},
    "change.recorded": {"description": ("text", True), "operation_class": (OPERATION_CLASS, True),
                        "result": (CHANGE_RESULT, True), "finding_id": (FINDING_ID, False),
                        "approved_by": ("text", False), "rollback": ("text", False)},
    "incident.status": {"status": (INCIDENT, True), "summary": ("text", False), "containment": ("list", False)},
    "status.updated": {"activity": ("text", True), "waiting_on": (WAITING_ON, False)},
    "asset.upserted": {"id": (ASSET_ID, True), "label": ("text", False), "kind": ("text", False),
                       "addresses": ("list", False), "services": ("list", False), "exposure": (EXPOSURE, False),
                       "skill": (SKILL_NAME, False), "coverage": (COVERAGE, False),
                       "assessment_id": (ASSESSMENT_ID, False), "note": ("text", False)},
    "assessment.completed": {"summary": ("text", False)},
    "kickoff.answered": {"source": (SOURCE, False),
                         **{key: (AGENT_COUNT if key == "agents" else tuple(v for v, _ in choices) if choices else "text", False)
                            for key, _, choices, *_ in KICKOFF_FIELDS}},
}
KICKOFF_KEYS = [key for key, *_ in KICKOFF_FIELDS]

# Redacted placeholders such as <token>, ***, or [REDACTED] are allowed after "password:" and similar.
SECRET_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\bssh-(ed25519|rsa|dss) AAAA",
    r"\bgh[pousr]_[A-Za-z0-9]{20,}",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.",
    r"\b(password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*(?![<*\[])\S{4,}",
    r"[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@",
)]


class InvalidEvent(ValueError):
    pass


_BAD = object()  # a request body that was refused (the error response has already been sent)


def _normalize(value, allowed):
    if isinstance(value, int) and not isinstance(value, bool):
        value = str(value)
    if not isinstance(value, str):
        raise InvalidEvent("must be a string")
    simple = value.strip().replace(" ", "_").replace("-", "_")
    for candidate in (value, simple.lower(), simple.upper()):
        if candidate in allowed:
            return candidate
    raise InvalidEvent("must be one of: " + ", ".join(allowed))


def _text(value):
    if not isinstance(value, str):
        raise InvalidEvent("must be a string")
    if len(value) > MAX_TEXT:
        raise InvalidEvent(f"longer than {MAX_TEXT} characters")
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            raise InvalidEvent("looks like it contains a secret; redact it")
    return value


def validate_event(raw, received=None):
    """Return a clean event dict, or raise InvalidEvent with a reason that never echoes field values."""
    if not isinstance(raw, dict):
        raise InvalidEvent("event must be a JSON object")
    if raw.get("schema") != SCHEMA:
        raise InvalidEvent(f"schema must be {SCHEMA!r}")
    aid = raw.get("assessment_id")
    if not isinstance(aid, str) or not ASSESSMENT_ID.match(aid):
        raise InvalidEvent("assessment_id must be 1-80 letters, digits, '.', '_' or '-'")
    etype = raw.get("type")
    if etype not in EVENT_FIELDS:
        raise InvalidEvent("unknown type")
    time = raw.get("time")
    if time is None:
        time = received
    else:
        try:
            parsed = datetime.fromisoformat(str(time).replace("Z", "+00:00"))
        except ValueError:
            raise InvalidEvent("time must be ISO-8601") from None
        if parsed.tzinfo is None:
            raise InvalidEvent("time must include a timezone")
        time = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    data = raw.get("data", {})
    if not isinstance(data, dict):
        raise InvalidEvent("data must be a JSON object")

    clean = {}
    for name, (kind, required) in EVENT_FIELDS[etype].items():
        if name not in data or data[name] is None:
            if required:
                raise InvalidEvent(f"data.{name} is required")
            continue
        value = data[name]
        try:
            if kind == "text":
                clean[name] = _text(value)
            elif kind == "list":
                if not isinstance(value, list) or len(value) > MAX_LIST:
                    raise InvalidEvent(f"must be a list of at most {MAX_LIST} strings")
                clean[name] = [_text(item) for item in value]
            elif isinstance(kind, tuple):
                clean[name] = _normalize(value, kind)
            else:
                if isinstance(value, int) and not isinstance(value, bool):
                    value = str(value)
                if not isinstance(value, str) or not kind.match(value):
                    raise InvalidEvent("has an invalid format")
                clean[name] = value
        except InvalidEvent as exc:
            raise InvalidEvent(f"data.{name} {exc}") from None
    return {"assessment_id": aid, "type": etype, "time": time, "data": clean}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class EventStore:
    """Events live in <data>/events/*.jsonl (agents or the HTTP endpoint) and, when a reports directory is
    given, in each run folder's <reports>/<run-id>/events*.jsonl (one file per parallel agent)."""

    def __init__(self, data_dir, reports_dir=None):
        self.events_dir = Path(data_dir) / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path(reports_dir) if reports_dir else None
        self._lock = threading.Lock()
        self._cache = {}
        self.homes = {}  # assessment_id -> run folder its assessment.started was read from

    def append_kickoff(self, event):
        """Write a kick-off answer from the dashboard where the agent will read it: the run folder's own
        events-dashboard.jsonl, or the events folder for an assessment that has no run folder."""
        home = self.homes.get(event["assessment_id"])
        if home and self.reports_dir and home.parent.resolve() == self.reports_dir.resolve():
            path = home / "events-dashboard.jsonl"
        else:
            path = self.events_dir / f"{event['assessment_id']}.jsonl"
        line = json.dumps({"schema": SCHEMA, **event}, ensure_ascii=False)
        with self._lock:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | O_BINARY, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(line + "\n")
        return path

    def append(self, events):
        with self._lock:
            for event in events:
                line = json.dumps({"schema": SCHEMA, **event}, ensure_ascii=False)
                with open(self.events_dir / f"{event['assessment_id']}.jsonl", "a", encoding="utf-8", newline="\n") as fh:
                    fh.write(line + "\n")

    def _read_file(self, path):
        stat = path.stat()
        key = (stat.st_mtime_ns, stat.st_size)
        cached = self._cache.get(path)
        if cached and cached[0] == key:
            return cached[1], cached[2]
        events, rejected = [], []
        label = f"{path.parent.name}/{path.name}" if path.parent != self.events_dir else path.name
        received = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds")
        received = received.replace("+00:00", "Z")
        with open(path, encoding="utf-8", errors="replace") as fh:
            for number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    events.append(validate_event(json.loads(line), received))
                except json.JSONDecodeError:
                    rejected.append({"file": label, "line": number, "reason": "not valid JSON"})
                except InvalidEvent as exc:
                    rejected.append({"file": label, "line": number, "reason": str(exc)})
        self._cache[path] = (key, events, rejected)
        return events, rejected

    def sources(self):
        """Where the dashboard looks for events, so an empty dashboard can say so."""
        found = [str(self.events_dir / "*.jsonl")]
        if self.reports_dir:
            found.append(str(self.reports_dir / "<run-id>" / "events*.jsonl"))
        return found

    def load(self):
        events, rejected = [], []
        paths = sorted(self.events_dir.glob("*.jsonl"))
        if self.reports_dir and self.reports_dir.is_dir():
            paths += sorted(self.reports_dir.glob("*/events*.jsonl"))
        with self._lock:
            for path in paths:
                file_events, file_rejected = self._read_file(path)
                events.extend(file_events)
                rejected.extend(file_rejected)
                for event in file_events:
                    if event["type"] == "assessment.started" and path.parent != self.events_dir:
                        self.homes[event["assessment_id"]] = path.parent
        return events, rejected


def _new_assessment(aid):
    return {"id": aid, "skill": None, "skill_version": None, "target": None, "scope": None, "agent": None,
            "parent": None, "assets": {}, "mode": None, "modes_visited": [], "completed": False, "summary": None, "started": None, "updated": None,
            "domains": {}, "findings": {}, "changes": [], "incident": None, "status": None, "kickoff": {}}


def aggregate(events, rejected=()):
    """Fold events (in order) into the current state of every assessment."""
    assessments = {}
    for event in events:
        a = assessments.setdefault(event["assessment_id"], _new_assessment(event["assessment_id"]))
        data, time, etype = event["data"], event["time"], event["type"]
        if time and (a["updated"] is None or time > a["updated"]):
            a["updated"] = time
        if etype == "assessment.started":
            a.update({k: data.get(k) for k in ("skill", "skill_version", "target", "scope", "agent", "parent")})
            a["started"] = time
            a["mode"] = a["mode"] or "discover"
        elif etype == "mode.changed":
            a["mode"] = data["mode"]
        elif etype == "domain.status":
            domain = a["domains"].setdefault(data["domain"], {"domain": data["domain"], "title": None})
            domain.update(data)
            domain["updated"] = time
        elif etype == "finding.upserted":
            finding = a["findings"].setdefault(data["id"], {"id": data["id"], "first_seen": time})
            finding.update(data)
            finding["updated"] = time
        elif etype == "asset.upserted":
            asset = a["assets"].setdefault(data["id"], {"id": data["id"], "first_seen": time})
            asset.update(data)
            asset["updated"] = time
        elif etype == "change.recorded":
            a["changes"].append({**data, "time": time})
        elif etype == "status.updated":
            a["status"] = {"activity": data["activity"], "waiting_on": data.get("waiting_on", "nothing"), "time": time}
        elif etype == "incident.status":
            a["incident"] = {**data, "time": time}
        elif etype == "kickoff.answered":
            # Answers can come from the chat (written by the agent) or the dashboard, in different files,
            # so the newest answer to each question wins regardless of file order.
            for key in KICKOFF_KEYS:
                if key in data:
                    current = a["kickoff"].get(key)
                    if current is None or (time or "") >= (current["time"] or ""):
                        a["kickoff"][key] = {"value": data[key], "source": data.get("source", "chat"), "time": time}
        elif etype == "assessment.completed":
            a["completed"] = True
            a["summary"] = data.get("summary")
        if a["mode"] and a["mode"] not in a["modes_visited"]:
            a["modes_visited"].append(a["mode"])

    result = []
    for a in assessments.values():
        findings = sorted(a["findings"].values(), key=lambda f: (f.get("priority") or "P9", f["id"]))
        counts = {p: 0 for p in PRIORITY}
        for f in findings:
            if f.get("priority") in counts and f.get("state") not in CLOSED_STATES:
                counts[f["priority"]] += 1
        result.append({**a, "findings": findings, "open_counts": counts,
                       "domains": sorted(a["domains"].values(), key=lambda d: d["domain"]),
                       "assets": sorted(a["assets"].values(), key=lambda x: ((x.get("label") or x["id"]).lower())),
                       "changes": list(reversed(a["changes"])), "children": []})
    result.sort(key=lambda a: a["updated"] or "", reverse=True)

    # Group per-asset assessments under their run, and total open findings across the run.
    by_id = {a["id"]: a for a in result}
    for a in result:
        parent = by_id.get(a["parent"]) if a["parent"] != a["id"] else None
        if parent is None:
            a["parent"] = None
        else:
            parent["children"].append(a["id"])
    for a in result:
        rollup = dict(a["open_counts"])
        for child_id in a["children"]:
            for p, n in by_id[child_id]["open_counts"].items():
                rollup[p] += n
        a["rollup_counts"] = rollup
    return {"generated": _now(), "assessments": result, "rejected": list(rejected)[-100:], "sources": [],
            "kickoff_fields": [{"key": k, "question": q, "choices": c, "hint": h, "description": d}
                               for k, q, c, h, d in KICKOFF_FIELDS]}


class Handler(BaseHTTPRequestHandler):
    server_version = SERVER_NAME
    sys_version = ""

    def log_message(self, fmt, *args):
        # Log method and path only; never headers (they carry the token).
        sys.stderr.write(f"{self.log_date_time_string()} {self.command} {self.path.split('?')[0]}"
                         f" -> {args[1] if len(args) > 1 else ''}\n")

    def _send(self, status, body=b"", content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
                         "img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _host_ok(self):
        # Refuse unexpected Host headers, which defeats DNS-rebinding attacks from web pages.
        host = (self.headers.get("Host") or "").strip().lower()
        if host.startswith("["):
            host = host[: host.find("]") + 1]
        else:
            host = host.rsplit(":", 1)[0]
        if host in self.server.allowed_hosts:
            return True
        self._json(HTTPStatus.MISDIRECTED_REQUEST, {"error": "unexpected Host header"})
        return False

    def _authorized(self):
        auth = self.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else ""
        if token and hmac.compare_digest(token.encode(), self.server.token.encode()):
            return True
        self._json(HTTPStatus.UNAUTHORIZED, {"error": "missing or invalid token"})
        return False

    def do_GET(self):
        if not self._host_ok():
            return
        path = self.path.split("?", 1)[0]
        if path in STATIC_FILES:
            name, content_type = STATIC_FILES[path]
            self._send(HTTPStatus.OK, (STATIC_DIR / name).read_bytes(), content_type)
        elif path == "/api/state":
            if self._authorized():
                state = aggregate(*self.server.store.load())
                state["sources"] = self.server.store.sources()
                state["dashboard_access"] = self.server.access
                state["server"] = dict(self.server.identity)
                state["kickoff_prefill"] = read_prefill(self.server.data_dir)
                self._json(HTTPStatus.OK, state)
        else:
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    do_HEAD = do_GET

    def do_POST(self):
        if not self._host_ok():
            return
        path = self.path.split("?", 1)[0]
        if path not in ("/api/events", "/api/kickoff"):
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        if not self._authorized():
            return
        payload = self._read_json()
        if payload is _BAD:
            return
        if path == "/api/kickoff":
            self._kickoff(payload)
        else:
            self._post_events(payload if isinstance(payload, list) else [payload])

    def _read_json(self):
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Content-Type must be application/json"})
            return _BAD
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": f"body must be at most {MAX_BODY} bytes"})
            return _BAD
        try:
            return json.loads(self.rfile.read(length) or b"null")
        except json.JSONDecodeError:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "body is not valid JSON"})
            return _BAD

    def _kickoff(self, payload):
        """Kick-off answers typed into the dashboard: {"assessment_id": ..., "answers": {key: value}}."""
        if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "expected {assessment_id, answers}"})
            return
        aid = payload.get("assessment_id")
        state = aggregate(*self.server.store.load())
        run = next((a for a in state["assessments"] if a["id"] == aid), None)
        if run is None or run["parent"] or run["completed"]:
            self._json(HTTPStatus.NOT_FOUND, {"error": "no open run with that assessment_id"})
            return
        # Blank answers are left out rather than erasing what was said in the chat.
        answers = {k: v for k, v in payload["answers"].items() if k in KICKOFF_KEYS and v not in (None, "")}
        if not answers:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "no answers given"})
            return
        try:
            event = validate_event({"schema": SCHEMA, "assessment_id": aid, "time": _now(), "type": "kickoff.answered",
                                    "data": {**answers, "source": "dashboard"}})
        except InvalidEvent as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        self.server.store.append_kickoff(event)
        self._json(HTTPStatus.ACCEPTED, {"accepted": len(answers)})

    def _post_events(self, raw_events):
        received = _now()
        accepted, errors = [], []
        for index, raw in enumerate(raw_events):
            try:
                accepted.append(validate_event(raw, received))
            except InvalidEvent as exc:
                errors.append({"index": index, "reason": str(exc)})
        if errors:
            # All-or-nothing, so an agent never has to work out which half of a batch landed.
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid events; none were stored", "details": errors})
            return
        self.server.store.append(accepted)
        self._json(HTTPStatus.ACCEPTED, {"accepted": len(accepted)})


def load_token(data_dir):
    env = os.environ.get("AISS_DASHBOARD_TOKEN")
    if env:
        return env
    path = Path(data_dir) / "token"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    token = secrets.token_urlsafe(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | O_BINARY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(token + "\n")
    return token


def lan_names():
    """Addresses and names other devices on the LAN can use to reach this computer."""
    names = []
    try:
        # Connecting a UDP socket sends nothing; it only picks the interface of the default route.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 9))
            names.append(probe.getsockname()[0])
    except OSError:
        pass
    hostname = socket.gethostname().lower()
    if hostname:
        names.append(hostname)
        if "." not in hostname:
            names.append(hostname + ".local")
    return [n for n in dict.fromkeys(names) if n and not n.startswith("127.")]


def make_server(host, port, data_dir, token, extra_hosts=(), reports_dir=None):
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.store = EventStore(data_dir, reports_dir)
    server.token = token
    server.allowed_hosts = {"localhost", "127.0.0.1", "[::1]", host.lower()} | {h.lower() for h in extra_hosts}
    server.access = "local" if host in ("127.0.0.1", "localhost", "::1") else "lan"
    server.identity = {"root": PROJECT_ROOT, "code": CODE_FINGERPRINT}
    server.data_dir = Path(data_dir)
    return server


def cmd_serve(args):
    lan = []
    if args.lan:
        lan = lan_names()
        if not lan:
            sys.exit("Couldn't find this computer's LAN address; use --host 0.0.0.0 --allow-host <address>.")
        args.host = "0.0.0.0"
        args.allow_host = list(args.allow_host) + lan
    if args.host in ("0.0.0.0", "::") and not args.allow_host:
        sys.exit("Listening on all interfaces requires --allow-host <name-or-ip> for each address you'll browse to.")
    data_dir = Path(args.data).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(data_dir, 0o700)
    token = load_token(data_dir)
    reports_dir = Path(args.reports).expanduser()
    server = make_server(args.host, args.port, data_dir, token, args.allow_host, reports_dir)
    shown = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    url = f"http://{shown}:{server.server_address[1]}/#token={token}"
    print(f"Dashboard:   {url}")
    for name in lan or (args.allow_host if args.host in ("0.0.0.0", "::") else []):
        print(f"On your LAN: http://{name}:{server.server_address[1]}/#token={token}")
    print(f"Run folders: {reports_dir}/<run-id>/events.jsonl")
    print(f"Events dir:  {server.store.events_dir}")
    print(f"HTTP ingest: POST http://{shown}:{server.server_address[1]}/api/events (Bearer token)")
    if server.access == "lan":
        print("LAN mode: the page and token travel unencrypted on your network. Use it only on a network you "
              "trust, and stop the dashboard when you're done.")
    print("Keep this dashboard off the internet: it is a map of your weaknesses.", flush=True)
    if args.open:
        import webbrowser
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def probe(port, data_dir, timeout=3):
    """Say what is listening on 127.0.0.1:port: (status, access, root).

    free         nothing is listening
    current      a dashboard from this copy of the project, running this version of the code
    outdated     a dashboard from another copy, or started before this copy's code changed
    wrong_token  a dashboard that doesn't accept this data folder's token (started with another --data)
    other        something that isn't this project's dashboard
    """
    import http.client
    token = os.environ.get("AISS_DASHBOARD_TOKEN", "")
    token_file = Path(data_dir).expanduser() / "token"
    if not token and token_file.exists():  # read only; never create a token here
        token = token_file.read_text(encoding="utf-8").strip()
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        conn.request("GET", "/api/state", headers={"Host": f"127.0.0.1:{port}", "Authorization": f"Bearer {token}"})
        response = conn.getresponse()
        body = response.read()
    except ConnectionRefusedError:
        return "free", "", ""
    except (OSError, http.client.HTTPException):
        return "other", "", ""
    finally:
        conn.close()
    if not (response.getheader("Server") or "").strip().startswith(SERVER_NAME):
        return "other", "", ""
    if response.status == HTTPStatus.UNAUTHORIZED:
        return "wrong_token", "", ""
    try:
        state = json.loads(body)
    except ValueError:
        return "other", "", ""
    if response.status != HTTPStatus.OK or not isinstance(state, dict):
        return "other", "", ""
    access = state.get("dashboard_access") or "unknown"
    server = state.get("server") if isinstance(state.get("server"), dict) else {}  # absent in older versions
    root = server.get("root") or "unknown"
    same_copy = os.path.normcase(root) == os.path.normcase(PROJECT_ROOT)
    status = "current" if same_copy and server.get("code") == CODE_FINGERPRINT else "outdated"
    return status, access, root


def local_subnet():
    """The /24 around this computer's address on its default route, or "" if unknown or ambiguous."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 9))  # a UDP connect sends nothing; it only picks the outgoing interface
            address = ipaddress.ip_address(s.getsockname()[0])
    except (OSError, ValueError):
        return ""
    # Only a private LAN address. Anything else (a public address on the interface, a carrier-grade NAT or
    # VPN range, link-local, loopback) doesn't say which home network this is.
    if not address.is_private or address.is_loopback or address.is_link_local or address.is_reserved \
            or address.is_unspecified:
        return ""
    return str(ipaddress.ip_network(f"{address}/24", strict=False))


def public_address(timeout=3):
    """This network's public address as an outside service sees it, or "" if it can't be found."""
    import urllib.request
    for url in PUBLIC_ADDRESS_URLS:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                address = ipaddress.ip_address(response.read(64).decode("ascii", "replace").strip())
        except (OSError, ValueError):
            continue
        if address.is_global:
            return str(address)
    return ""


def read_prefill(data_dir):
    """Validated suggestions from <data>/kickoff-prefill.json, or {} if there are none."""
    try:
        raw = json.loads((Path(data_dir) / PREFILL_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    clean = {}
    for key in PREFILL_KEYS:
        value = raw.get(key)
        if not isinstance(value, str) or not value.strip():
            continue
        try:
            clean[key] = _text(value.strip()[:200])
        except InvalidEvent:
            continue
    if "agents" in clean and not AGENT_COUNT.match(clean["agents"]):
        del clean["agents"]
    return clean


def cmd_prefill(args):
    # Prints "Question: answer" lines for the launcher's prompt; with --data, also saves them for the dashboard.
    found = {"in_scope": local_subnet(), "internet_edge": "" if args.no_lookup else public_address(), "agents": "1"}
    found = {k: v for k, v in found.items() if v}
    if args.data:
        data_dir = Path(args.data).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = data_dir / PREFILL_FILE
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(found, fh)
            fh.write("\n")
    questions = {key: question for key, question, *_ in KICKOFF_FIELDS}
    for key in PREFILL_KEYS:
        if key in found:
            print(f"{questions[key]}: {found[key]}")
    return 0


def cmd_probe(args):
    # One value per line (status, access, project folder), so shell and PowerShell can read it without parsing.
    print("\n".join(probe(args.port, args.data)))
    return 0


def cmd_validate(args):
    status = 0
    for name in args.files:
        with open(name, encoding="utf-8") as fh:
            for number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    validate_event(json.loads(line))
                except (json.JSONDecodeError, InvalidEvent) as exc:
                    print(f"{name}:{number}: {exc}")
                    status = 1
    if status == 0:
        print("validate: all events are valid.")
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="run the dashboard")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--lan", action="store_true",
                       help="let other devices on your local network view it (listens on all interfaces and "
                            "accepts this computer's LAN address and name)")
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve.add_argument("--data", default=str(DEFAULT_DATA), help=f"data directory (default {DEFAULT_DATA})")
    serve.add_argument("--reports", default=str(DEFAULT_REPORTS),
                       help=f"folder of run folders to show (default {DEFAULT_REPORTS})")
    serve.add_argument("--allow-host", action="append", default=[],
                       help="extra Host name/IP to accept (repeatable); required when binding all interfaces")
    serve.add_argument("--open", action="store_true", help="open the dashboard in the default browser")
    validate = sub.add_parser("validate", help="check event files without running the server")
    validate.add_argument("files", nargs="+")
    probe_cmd = sub.add_parser("probe", help="say what is listening on the dashboard port (for the launchers)")
    probe_cmd.add_argument("--port", type=int, default=DEFAULT_PORT)
    probe_cmd.add_argument("--data", default=str(DEFAULT_DATA), help=f"data directory (default {DEFAULT_DATA})")
    prefill = sub.add_parser("prefill", help="suggest kick-off answers detected on this computer (for the launchers)")
    prefill.add_argument("--data", help="also save them in this data directory, for the dashboard's kick-off form")
    prefill.add_argument("--no-lookup", action="store_true",
                         help="don't ask an outside service for this network's public address")
    report = sub.add_parser("report", help="write report.md and report.html for a run folder and print totals")
    report.add_argument("run_dir")
    args = parser.parse_args(argv)
    if args.command == "report":
        # Load by path: isolated mode (python3 -I) doesn't put this folder on the import path.
        import importlib.util
        spec = importlib.util.spec_from_file_location("aiss_report", Path(__file__).resolve().parent / "report.py")
        report_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report_module)
        return report_module.main(args.run_dir)
    if args.command == "probe":
        return cmd_probe(args)
    if args.command == "prefill":
        return cmd_prefill(args)
    return cmd_serve(args) if args.command == "serve" else cmd_validate(args)


if __name__ == "__main__":
    sys.exit(main())
