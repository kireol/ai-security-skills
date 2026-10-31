"""Tests for dashboard.py. Run: python3 -m unittest discover tools/dashboard"""
import http.client
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dashboard  # noqa: E402

SAMPLE = Path(__file__).resolve().parent / "examples" / "sample-events.jsonl"


def event(etype, aid="test-1", time="2026-01-15T14:00:00Z", **data):
    return {"schema": dashboard.SCHEMA, "assessment_id": aid, "time": time, "type": etype, "data": data}


class ValidationTests(unittest.TestCase):
    def test_enums_are_normalized(self):
        clean = dashboard.validate_event(event("domain.status", domain="C", status="Not assessed"))
        self.assertEqual(clean["data"]["status"], "not_assessed")
        clean = dashboard.validate_event(event("finding.upserted", id="NAS-001", priority="p2", state="Open"))
        self.assertEqual((clean["data"]["priority"], clean["data"]["state"]), ("P2", "open"))

    def test_unknown_fields_are_dropped(self):
        clean = dashboard.validate_event(event("mode.changed", mode="recommend", extra="x"))
        self.assertEqual(clean["data"], {"mode": "recommend"})

    def test_rejections(self):
        bad = [
            event("mode.changed", mode="sleeping"),
            event("mode.changed"),
            event("finding.upserted", id="../etc/passwd"),
            event("unknown.type"),
            {**event("mode.changed", mode="discover"), "assessment_id": "../escape"},
            {**event("mode.changed", mode="discover"), "schema": "other"},
            {**event("mode.changed", mode="discover"), "time": "2026-01-15T14:00:00"},
            event("assessment.started", skill="x", target="y" * (dashboard.MAX_TEXT + 1)),
        ]
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises(dashboard.InvalidEvent):
                dashboard.validate_event(raw)

    def test_secrets_are_rejected_without_echoing_them(self):
        # Assembled at runtime so scripts/check-content.sh doesn't flag these fake secrets in the source.
        secrets = [
            "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
            "token " + "ghp" + "_abcdefghijklmnopqrstuvwxyz0123",
            "password: hunter22",
            "url https://admin:s3cret@192.0.2.1/",
            "AK" + "IAABCDEFGHIJKLMNOP",
        ]
        for text in secrets:
            with self.subTest(text=text):
                with self.assertRaises(dashboard.InvalidEvent) as ctx:
                    dashboard.validate_event(event("finding.upserted", id="NAS-001", summary=text))
                self.assertNotIn(text, str(ctx.exception))

    def test_redacted_placeholders_are_allowed(self):
        for text in ("password: <redacted>", "api_key = ***", "token: [REDACTED]"):
            dashboard.validate_event(event("finding.upserted", id="NAS-001", summary=text))

    def test_sample_file_is_valid(self):
        for line in SAMPLE.read_text().splitlines():
            dashboard.validate_event(json.loads(line))


class AggregateTests(unittest.TestCase):
    def setUp(self):
        events = [dashboard.validate_event(json.loads(line)) for line in SAMPLE.read_text().splitlines()]
        state = dashboard.aggregate(events)
        self.by_id = {a["id"]: a for a in state["assessments"]}
        self.state = state

    def test_newest_assessment_first(self):
        self.assertEqual(self.state["assessments"][0]["id"], "2026-01-15-example-home-run")

    def test_partial_finding_update_merges(self):
        nas = self.by_id["2026-01-15-example-nas"]
        finding = next(f for f in nas["findings"] if f["id"] == "NAS-002")
        self.assertEqual(finding["state"], "resolved")
        self.assertEqual(finding["title"], "Built-in admin account enabled")

    def test_open_counts_exclude_resolved(self):
        nas = self.by_id["2026-01-15-example-nas"]
        self.assertEqual(nas["open_counts"]["P2"], 1)
        self.assertEqual(nas["open_counts"]["P3"], 0)

    def test_latest_domain_status_and_mode(self):
        nas = self.by_id["2026-01-15-example-nas"]
        self.assertEqual({d["domain"]: d["status"] for d in nas["domains"]}["A"], "pass")
        self.assertEqual(nas["mode"], "remediate")

    def test_run_groups_children_and_rolls_up_counts(self):
        run = self.by_id["2026-01-15-example-home-run"]
        self.assertIsNone(run["parent"])
        self.assertEqual(sorted(run["children"]), ["2026-01-15-example-nas", "2026-01-16-example-firewall"])
        # Run's own NET-001 (P3) + NAS-001 (P2) + firewall P0 and P1; resolved NAS-002 excluded.
        self.assertEqual(run["rollup_counts"], {"P0": 1, "P1": 1, "P2": 1, "P3": 1, "P4": 0})
        self.assertEqual(self.by_id["2026-01-15-example-nas"]["parent"], run["id"])

    def test_asset_partial_updates_merge(self):
        assets = {x["id"]: x for x in self.by_id["2026-01-15-example-home-run"]["assets"]}
        self.assertEqual(assets["nas"]["coverage"], "assessed")
        self.assertEqual(assets["nas"]["assessment_id"], "2026-01-15-example-nas")
        self.assertEqual(assets["nas"]["kind"], "NAS")
        self.assertEqual(assets["camera-1"]["coverage"], "no_skill")

    def test_unknown_parent_is_ignored(self):
        events = [dashboard.validate_event(event("assessment.started", skill="x", target="y", parent="missing"))]
        state = dashboard.aggregate(events)
        self.assertIsNone(state["assessments"][0]["parent"])

    def test_asset_validation(self):
        clean = dashboard.validate_event(event("asset.upserted", id="cam-1", exposure="Internet", coverage="No skill"))
        self.assertEqual((clean["data"]["exposure"], clean["data"]["coverage"]), ("internet", "no_skill"))
        with self.assertRaises(dashboard.InvalidEvent):
            dashboard.validate_event(event("asset.upserted", id="cam 1"))

    def test_incident_and_priority_order(self):
        fw = self.by_id["2026-01-16-example-firewall"]
        self.assertEqual(fw["incident"]["status"], "suspected")
        self.assertEqual(fw["modes_visited"], ["discover", "respond"])
        self.assertEqual([f["id"] for f in fw["findings"]], ["OPN-002", "OPN-001"])


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.server = dashboard.make_server("127.0.0.1", 0, self.data, "test-token")
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def request(self, method, path, body=None, token="test-token", host=None, content_type="application/json"):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Host": host or f"127.0.0.1:{self.port}"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if body is not None:
            headers["Content-Type"] = content_type
            body = json.dumps(body).encode() if not isinstance(body, bytes) else body
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        payload = response.read()
        conn.close()
        return response, payload

    def test_static_page_has_security_headers(self):
        response, body = self.request("GET", "/", token=None)
        self.assertEqual(response.status, 200)
        self.assertIn(b"AI Security Skills", body)
        self.assertIn("script-src 'self'", response.getheader("Content-Security-Policy"))
        self.assertEqual(response.getheader("X-Content-Type-Options"), "nosniff")

    def test_state_lists_watched_folders(self):
        state = json.loads(self.request("GET", "/api/state")[1])
        self.assertTrue(any(s.endswith("*.jsonl") for s in state["sources"]))

    def test_api_requires_token(self):
        self.assertEqual(self.request("GET", "/api/state", token=None)[0].status, 401)
        self.assertEqual(self.request("GET", "/api/state", token="wrong")[0].status, 401)
        self.assertEqual(self.request("GET", "/api/state")[0].status, 200)

    def test_unexpected_host_is_refused(self):
        self.assertEqual(self.request("GET", "/api/state", host="attacker.example")[0].status, 421)
        self.assertEqual(self.request("GET", f"/api/state", host=f"localhost:{self.port}")[0].status, 200)

    def test_post_then_read(self):
        response, _ = self.request("POST", "/api/events", [
            event("assessment.started", skill="synology-dsm", target="example NAS"),
            event("finding.upserted", id="NAS-001", title="t", priority="P2", confidence="confirmed", state="open"),
        ])
        self.assertEqual(response.status, 202)
        state = json.loads(self.request("GET", "/api/state")[1])
        self.assertEqual(state["assessments"][0]["open_counts"]["P2"], 1)
        self.assertTrue((self.data / "events" / "test-1.jsonl").exists())

    def test_invalid_batch_stores_nothing(self):
        response, body = self.request("POST", "/api/events", [
            event("mode.changed", mode="discover"),
            event("finding.upserted", id="NAS-001", summary="password: hunter22"),
        ])
        self.assertEqual(response.status, 400)
        self.assertNotIn(b"hunter22", body)
        self.assertEqual(list((self.data / "events").glob("*.jsonl")), [])

    def test_post_limits(self):
        self.assertEqual(self.request("POST", "/api/events", b"{}", content_type="text/plain")[0].status, 415)
        # Announce an oversized body without sending it; the server must refuse before reading.
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.putrequest("POST", "/api/events", skip_host=True)
        for name, value in (("Host", f"127.0.0.1:{self.port}"), ("Authorization", "Bearer test-token"),
                            ("Content-Type", "application/json"), ("Content-Length", str(dashboard.MAX_BODY + 1))):
            conn.putheader(name, value)
        conn.endheaders()
        self.assertEqual(conn.getresponse().status, 413)
        conn.close()
        self.assertEqual(self.request("POST", "/api/events", b"{not json")[0].status, 400)

    def test_folder_ingest_and_rejected_lines(self):
        lines = [json.dumps(event("mode.changed", aid="folder-1", mode="recommend")), "not json",
                 json.dumps(event("mode.changed", aid="folder-1", mode="bogus"))]
        (self.data / "events" / "agent.jsonl").write_text("\n".join(lines) + "\n")
        state = json.loads(self.request("GET", "/api/state")[1])
        self.assertEqual(state["assessments"][0]["mode"], "recommend")
        self.assertEqual(len(state["rejected"]), 2)



class ReportTests(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("aiss_report", Path(__file__).resolve().parent / "report.py")
        self.report = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.report)
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def quiet_main(self):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return self.report.main(self.run)

    def write(self, events):
        (self.run / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    def test_sample_run_totals_and_files(self):
        (self.run / "events.jsonl").write_text(SAMPLE.read_text())
        self.assertEqual(self.quiet_main(), 0)
        t = self.report.totals(self.report.load_run(self.run)[0]["assessments"])
        self.assertEqual((t["systems"], t["serious"], t["warnings"], t["info"]), (4, 3, 1, 0))
        for name in ("report.md", "report.html"):
            self.assertEqual((self.run / name).stat().st_mode & 0o777, 0o600)
        self.assertIn("| Discovery level | 1: light discovery (host and port checks) | dashboard,",
                      (self.run / "report.md").read_text())

    def test_untrusted_text_is_escaped_in_html(self):
        hostile = "<script>alert(1)</script>"
        self.write([event("assessment.started", skill="x", target=hostile),
                    event("finding.upserted", id="X-001", title=hostile, priority="P1", state="open",
                          recommendation=hostile)])
        self.quiet_main()
        page = (self.run / "report.html").read_text()
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_systems_without_inventory_count_assessments(self):
        self.write([event("assessment.started", aid="a", skill="opnsense", target="fw"),
                    event("assessment.started", aid="b", skill="synology-dsm", target="nas")])
        t = self.report.totals(self.report.load_run(self.run)[0]["assessments"])
        self.assertEqual(t["systems"], 2)

    def test_empty_run_fails(self):
        self.assertEqual(self.quiet_main(), 1)


class StatusTests(unittest.TestCase):
    def test_status_validation_and_latest_wins(self):
        events = [dashboard.validate_event(event("assessment.started", skill="x", target="y")),
                  dashboard.validate_event(event("status.updated", activity="scanning", waiting_on="Background task")),
                  dashboard.validate_event(event("status.updated", time="2026-01-15T14:05:00Z",
                                                 activity="need an answer", waiting_on="user"))]
        a = dashboard.aggregate(events)["assessments"][0]
        self.assertEqual((a["status"]["activity"], a["status"]["waiting_on"]), ("need an answer", "user"))
        with self.assertRaises(dashboard.InvalidEvent):
            dashboard.validate_event(event("status.updated", activity="x", waiting_on="lunch"))
        with self.assertRaises(dashboard.InvalidEvent):
            dashboard.validate_event(event("status.updated"))

    def test_waiting_on_defaults_to_nothing(self):
        a = dashboard.aggregate([dashboard.validate_event(event("status.updated", activity="checking"))])["assessments"][0]
        self.assertEqual(a["status"]["waiting_on"], "nothing")


class KickoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name) / "data"
        self.reports = Path(self.tmp.name) / "reports"
        self.run = self.reports / "run-1"
        self.run.mkdir(parents=True)
        (self.run / "events.jsonl").write_text(
            json.dumps(event("assessment.started", aid="run-1", skill="full-assessment", target="home")) + "\n"
            + json.dumps(event("kickoff.answered", aid="run-1", environment="Home", discovery_level=0)) + "\n")
        self.server = dashboard.make_server("127.0.0.1", 0, self.data, "test-token", reports_dir=self.reports)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def post(self, body):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("POST", "/api/kickoff", body=json.dumps(body).encode(), headers={
            "Host": f"127.0.0.1:{self.port}", "Authorization": "Bearer test-token",
            "Content-Type": "application/json"})
        response = conn.getresponse()
        payload = response.read()
        conn.close()
        return response.status, payload

    def state(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/api/state", headers={"Host": f"127.0.0.1:{self.port}",
                                                   "Authorization": "Bearer test-token"})
        state = json.loads(conn.getresponse().read())
        conn.close()
        return state

    def test_chat_answers_show_with_their_source(self):
        state = self.state()
        kickoff = state["assessments"][0]["kickoff"]
        self.assertEqual(kickoff["environment"]["value"], "home")
        self.assertEqual(kickoff["discovery_level"], {"value": "0", "source": "chat", "time": "2026-01-15T14:00:00Z"})
        self.assertEqual(state["dashboard_access"], "local")
        self.assertIn("discovery_level", [f["key"] for f in state["kickoff_fields"]])

    def test_every_kickoff_question_has_a_description(self):
        for field in self.state()["kickoff_fields"]:
            self.assertTrue(field["description"].strip(), field["key"])

    def test_dashboard_answers_go_to_the_run_folder_and_win_when_newer(self):
        self.state()  # the dashboard learns where the run lives by reading it
        status, _ = self.post({"assessment_id": "run-1", "answers": {"discovery_level": "1", "pace": "phases",
                                                                     "goal": "", "bogus": "x"}})
        self.assertEqual(status, 202)
        written = self.run / "events-dashboard.jsonl"
        self.assertEqual(written.stat().st_mode & 0o777, 0o600)
        line = json.loads(written.read_text())
        self.assertEqual(line["data"], {"source": "dashboard", "discovery_level": "1", "pace": "phases"})
        kickoff = self.state()["assessments"][0]["kickoff"]
        self.assertEqual((kickoff["discovery_level"]["value"], kickoff["discovery_level"]["source"]), ("1", "dashboard"))
        self.assertEqual(kickoff["environment"]["source"], "chat")
        self.assertNotIn("goal", kickoff)

    def test_dashboard_answers_are_validated(self):
        self.state()
        for answers in ({"discovery_level": "3"}, {"agents": "0"}, {"access_available": "password: hunter22"}, {}):
            with self.subTest(answers=answers):
                status, body = self.post({"assessment_id": "run-1", "answers": answers})
                self.assertEqual(status, 400)
                self.assertNotIn(b"hunter22", body)
        self.assertEqual(self.post({"assessment_id": "nope", "answers": {"pace": "phases"}})[0], 404)
        self.assertFalse((self.run / "events-dashboard.jsonl").exists())

    def test_completed_runs_are_read_only(self):
        with open(self.run / "events.jsonl", "a") as fh:
            fh.write(json.dumps(event("assessment.completed", aid="run-1")) + "\n")
        self.state()
        self.assertEqual(self.post({"assessment_id": "run-1", "answers": {"pace": "phases"}})[0], 404)

    def test_lan_server_accepts_its_lan_names(self):
        server = dashboard.make_server("0.0.0.0", 0, self.data, "t", extra_hosts=["192.0.2.10"])
        try:
            self.assertEqual(server.access, "lan")
            self.assertIn("192.0.2.10", server.allowed_hosts)
        finally:
            server.server_close()
        self.assertTrue(all(not n.startswith("127.") for n in dashboard.lan_names()))


if __name__ == "__main__":
    unittest.main()
