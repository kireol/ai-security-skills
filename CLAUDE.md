# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

**ai-security-skills**: portable, model- and tool-agnostic AI skill documents (Markdown) for securing home,
work, homelab, and web systems. The prose is the product. There is no build, lint, or test tooling yet,
apart from the content check below. Judge edits on precision, internal consistency, and safety guardrails.
See `README.md` for the catalog and the four modes every skill must cover: **Discover, Recommend,
Remediate, Incident response**.

## The most important rule: no real-environment details

Read `CONTENT_RULES.md` before writing anything. Skills are inspired by the owner's own environment, and
you may have access to private knowledge sources describing it (for example, an MCP knowledge base). Use
them only to decide *which* products and checks to cover. Never copy names, IPs, MACs, hostnames, domains,
paths, credentials, inventories, or findings from them, or from any real system, into this repo. Never
name a private source in a tracked file. Use RFC documentation values
(`192.0.2.0/24`, `2001:db8::/32`, `example.com`) and `<placeholders>` instead.

## Commands

```sh
scripts/check-content.sh            # privacy check, whole repo; review every hit
scripts/check-content.sh skills/x   # one path
scripts/build-dist.py               # rebuild dist/ after changing core/ or skills/
scripts/build-dist.py --check       # exit 1 if dist/ is stale
scripts/lint-skills.py              # structure: files, sections, frontmatter, unique prefixes, links
python3 -m unittest discover -s tools/dashboard                 # dashboard tests
python3 -m unittest tools/dashboard/test_dashboard.py -k Server  # one group of tests
python3 tools/dashboard/dashboard.py serve --open               # run the dashboard locally
python3 tools/dashboard/dashboard.py report <run folder>        # write report.md/report.html, print totals
scripts/assess.sh [--dashboard] [--agent claude|codex|gemini|print]  # asks which AI to use; --stop stops the dashboard
```

Run the content check, the linter, and `build-dist.py --check` before every commit. `.private-denylist` (git-ignored) holds the owner's identifiers for
the content check. Never commit it, and never copy its contents into a tracked file.

## Layout and conventions

- `core/` holds the generic rules every skill builds on: modes and authorization (Discover, Recommend,
  Remediate, Respond; operation classes R/C1/C2/C3; standing authorization), operating principles,
  vulnerability triage (P0–P4), evidence and reporting (finding template, YAML findings), the tool-use
  contract, and the generic Respond playbook. Change core carefully: it affects every skill.
- `skills/<domain>/<product>/` is one skill: `SKILL.md` (frontmatter, then Discover / Recommend /
  Remediate / Respond sections, a worked example, version history), `incident-response.md`, and
  `references.md`. Domains are technology areas (`network`, `storage`, `operating-systems`,
  `surveillance`, `web`, …), not audiences; audience goes in frontmatter.
- Every product skill needs a `## Detection` section (vendor-default ports, banners, discovery
  announcements, MAC vendors). `build-dist.py` extracts it, with the frontmatter, into `dist/catalog.md`,
  which the `full-assessment` skill (`skills/orchestration/`) uses to match discovered devices to skills.
  Orchestration skills are excluded from the catalog and get it bundled instead.
- New skills start from `templates/skill-template/`. `skills/storage/synology-dsm/` is the reference
  example.
- Skills contain only product-specific content and link to core with `../../../core/<file>.md`.
  `build-dist.py` rewrites those links for the bundles.
- Skills may link to each other with relative paths (`../mqtt/SKILL.md`). `build-dist.py` rewrites them
  to sibling-folder links in folder bundles and to `dist/<skill>.md` pointers in single-file bundles.
- `check-content.sh` also flags vendor contact emails and vendor-documented private addresses; leave
  those out and point to the vendor page instead.
- `dist/` is generated and committed, so people can download a skill without building. Never edit it by
  hand.
- Frontmatter follows the Agent Skills format: `name` and `description` at the top level; `version`,
  `last_reviewed`, `applies_to`, `audience`, `finding_prefix`, and `modes` under `metadata`. Bump
  `version` and add a version-history entry on substantive changes. Versions never go in filenames.
- Don't add static CVE or version tables, or executable storage/RAID/filesystem repair procedures. Skills
  must tell the agent to verify against live vendor sources.
- Every assessment records events in a run folder (`~/ai-security-reports/<run-id>/`, never inside this
  repo). `tools/dashboard/report.py` turns a run folder into `report.md` and `report.html`; the closing
  message format (systems, serious = open P0–P2, warnings = open P3, informational = open P4, file paths)
  is defined in `core/evidence-and-reporting.md`. Keep the two in sync.
- `skills/orchestration/` holds skills that coordinate others (`full-assessment`, `skill-request`); the
  linter requires only frontmatter, "How to use this skill", and "Version history" for them.
- `check-content.sh` exempts only the project's own repository address (`kireol/ai-security-skills`)
  from the private denylist.
- `core/reporting-protocol.md` defines the live-event format; `tools/dashboard/dashboard.py` implements it
  (stdlib only, Python 3.9+, so it runs on stock macOS Python). Change both together, and keep its
  security properties: localhost by default, token auth, Host-header check, strict CSP, `textContent`-only
  rendering of event text, and secret screening. Test fixtures that look like secrets must be assembled at
  runtime so `check-content.sh` stays strict.
- Keep skills tool-agnostic (Claude Code, Codex, local LLMs, MCP clients, humans). Scope MCP-server-specific
  guidance to the named server.
