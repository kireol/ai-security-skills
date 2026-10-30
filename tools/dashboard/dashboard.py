#!/usr/bin/env python3
"""Local dashboard for ai-security-skills live reporting (core/reporting-protocol.md).

Standard library only; Python 3.9+.

  dashboard.py serve [--host 127.0.0.1] [--port 8770] [--data DIR] [--allow-host NAME ...]
  dashboard.py validate FILE.jsonl ...
"""
import argparse
import hmac
import json
import os
import re
import secrets
import sys
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCHEMA = "ai-security-skills/event/v1"
DEFAULT_DATA = Path(os.environ.get("AISS_DASHBOARD_DATA", Path.home() / ".ai-security-dashboard"))
DEFAULT_PORT = 8770
MAX_BODY = 1_000_000
MAX_TEXT = 4000
MAX_LIST = 50
STATIC_DIR = Path(__file__).resolve().parent / "static"
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
EXPOSURE = ("internet", "vpn", "lan", "isolated", "unknown")
COVERAGE = ("pending", "in_progress", "assessed", "no_skill", "out_of_scope", "skipped")
CLOSED_STATES = ("resolved", "accepted_risk")

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
                         "evidence_label": (EVIDENCE, False), "summary": ("text", False)},
    "change.recorded": {"description": ("text", True), "operation_class": (OPERATION_CLASS, True),
                        "result": (CHANGE_RESULT, True), "finding_id": (FINDING_ID, False),
                        "approved_by": ("text", False), "rollback": ("text", False)},
    "incident.status": {"status": (INCIDENT, True), "summary": ("text", False), "containment": ("list", False)},
    "asset.upserted": {"id": (ASSET_ID, True), "label": ("text", False), "kind": ("text", False),
                       "addresses": ("list", False), "services": ("list", False), "exposure": (EXPOSURE, False),
                       "skill": (SKILL_NAME, False), "coverage": (COVERAGE, False),
                       "assessment_id": (ASSESSMENT_ID, False), "note": ("text", False)},
    "assessment.completed": {"summary": ("text", False)},
}

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


def _normalize(value, allowed):
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
                if not isinstance(value, str) or not kind.match(value):
                    raise InvalidEvent("has an invalid format")
                clean[name] = value
        except InvalidEvent as exc:
            raise InvalidEvent(f"data.{name} {exc}") from None
    return {"assessment_id": aid, "type": etype, "time": time, "data": clean}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class EventStore:
    """Events live in <data>/events/*.jsonl, written by agents directly or by the HTTP endpoint."""

    def __init__(self, data_dir):
        self.events_dir = Path(data_dir) / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._cache = {}

    def append(self, events):
        with self._lock:
            for event in events:
                line = json.dumps({"schema": SCHEMA, **event}, ensure_ascii=False)
                with open(self.events_dir / f"{event['assessment_id']}.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")

    def _read_file(self, path):
        stat = path.stat()
        key = (stat.st_mtime_ns, stat.st_size)
        cached = self._cache.get(path)
        if cached and cached[0] == key:
            return cached[1], cached[2]
        events, rejected = [], []
        received = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds")
        received = received.replace("+00:00", "Z")
        with open(path, encoding="utf-8", errors="replace") as fh:
            for number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    events.append(validate_event(json.loads(line), received))
                except json.JSONDecodeError:
                    rejected.append({"file": path.name, "line": number, "reason": "not valid JSON"})
                except InvalidEvent as exc:
                    rejected.append({"file": path.name, "line": number, "reason": str(exc)})
        self._cache[path] = (key, events, rejected)
        return events, rejected

    def load(self):
        events, rejected = [], []
        with self._lock:
            for path in sorted(self.events_dir.glob("*.jsonl")):
                file_events, file_rejected = self._read_file(path)
                events.extend(file_events)
                rejected.extend(file_rejected)
        return events, rejected


def _new_assessment(aid):
    return {"id": aid, "skill": None, "skill_version": None, "target": None, "scope": None, "agent": None,
            "parent": None, "assets": {}, "mode": None, "modes_visited": [], "completed": False, "summary": None, "started": None, "updated": None,
            "domains": {}, "findings": {}, "changes": [], "incident": None}


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
        elif etype == "incident.status":
            a["incident"] = {**data, "time": time}
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
    return {"generated": _now(), "assessments": result, "rejected": list(rejected)[-100:]}


class Handler(BaseHTTPRequestHandler):
    server_version = "ai-security-dashboard"
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
                self._json(HTTPStatus.OK, aggregate(*self.server.store.load()))
        else:
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    do_HEAD = do_GET

    def do_POST(self):
        if not self._host_ok():
            return
        if self.path.split("?", 1)[0] != "/api/events":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        if not self._authorized():
            return
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Content-Type must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": f"body must be at most {MAX_BODY} bytes"})
            return
        try:
            payload = json.loads(self.rfile.read(length) or b"null")
        except json.JSONDecodeError:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "body is not valid JSON"})
            return
        raw_events = payload if isinstance(payload, list) else [payload]
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
        return path.read_text().strip()
    token = secrets.token_urlsafe(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(token + "\n")
    return token


def make_server(host, port, data_dir, token, extra_hosts=()):
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.store = EventStore(data_dir)
    server.token = token
    server.allowed_hosts = {"localhost", "127.0.0.1", "[::1]", host.lower()} | {h.lower() for h in extra_hosts}
    return server


def cmd_serve(args):
    if args.host in ("0.0.0.0", "::") and not args.allow_host:
        sys.exit("Listening on all interfaces requires --allow-host <name-or-ip> for each address you'll browse to.")
    data_dir = Path(args.data).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(data_dir, 0o700)
    token = load_token(data_dir)
    server = make_server(args.host, args.port, data_dir, token, args.allow_host)
    shown = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    print(f"Dashboard:   http://{shown}:{server.server_address[1]}/#token={token}")
    print(f"Events dir:  {server.store.events_dir}")
    print(f"HTTP ingest: POST http://{shown}:{server.server_address[1]}/api/events (Bearer token)")
    print("Keep this dashboard off the internet: it is a map of your weaknesses.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


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
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve.add_argument("--data", default=str(DEFAULT_DATA), help=f"data directory (default {DEFAULT_DATA})")
    serve.add_argument("--allow-host", action="append", default=[],
                       help="extra Host name/IP to accept (repeatable); required when binding all interfaces")
    validate = sub.add_parser("validate", help="check event files without running the server")
    validate.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    return cmd_serve(args) if args.command == "serve" else cmd_validate(args)


if __name__ == "__main__":
    sys.exit(main())
