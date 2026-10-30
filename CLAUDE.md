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

Run before every commit and review every hit:

```sh
scripts/check-content.sh            # whole repo
scripts/check-content.sh skills/x   # one path
```

`.private-denylist` (git-ignored) holds the owner's identifiers for this check. Never commit it, and never
copy its contents into a tracked file.

## Layout and conventions

- `skills/<domain>/<product>/SKILL.md` is one skill. Domains are technology areas (`network`, `storage`,
  `operating-systems`, `surveillance`, `web`, …), not audiences. Audience (home/work/homelab) goes in
  frontmatter.
- Planned (not yet built): `core/` holds the generic rules shared by every skill (modes and authorization,
  operating principles, CVE/KEV triage and the P0–P4 scale, evidence labels and output format, the tool-use
  contract, generic incident response). `templates/skill-template/` is the skeleton for new skills. `dist/`
  holds generated standalone bundles (core + skill) for people who want a single file.
- A skill should contain only product-specific content and reference `core/` for the rest.
- Versions live in frontmatter and the skill's version-history section, never in filenames.
- Don't add static CVE or version tables, or executable storage/RAID/filesystem repair procedures. Skills
  must tell the agent to verify against live vendor sources.
- Keep skills tool-agnostic (Claude Code, Codex, local LLMs, MCP clients, humans). Scope MCP-server-specific
  guidance to the named server.

## Current state and agreed next steps

`skills/storage/synology-dsm/SKILL.md` (v3.1) is the reference skill. It predates the template. The agreed
restructuring:

1. Extract the generic sections into `core/`, leaving roughly 250 lines of DSM-specific content.
2. Organize each skill around the four modes, with explicit mode-transition and authorization rules,
   including a defined format for "standing authorization".
3. Remove internal duplication: the hardening baseline vs domains C/D/E, the triple container checklist in
   domain F, domains I vs J, references in §10 vs §16, and the finding fields in §6 vs §11.
4. Add frontmatter (`name`, `description`, `version`, `last_reviewed`, `applies_to`, `audience`, `modes`).
5. Add a "Deployment variants" section (for example, DSM on non-Synology hardware under a hypervisor), a
   dependency/blast-radius step before recommendations, machine-readable findings with per-skill ID
   prefixes, one invented worked example, and DSM Task Scheduler root scripts as a Discover check.
6. Split incident response and references into `incident-response.md` and `references.md`.
