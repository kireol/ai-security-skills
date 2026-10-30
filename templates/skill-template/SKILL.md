---
name: <product>   # must match the folder name
description: >-
  Security assessment, hardening, remediation, and incident response for <product>. Use when auditing
  <product>, reviewing its <key areas>, or when <product> may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "<YYYY-MM-DD>"
  applies_to: "<product and version range>"
  audience: "<home, work, homelab, web>"
  finding_prefix: "<SHORT>"
  modes: "discover, recommend, remediate, respond"
---

<!--
Before writing, read CONTENT_RULES.md: nothing from any real environment. Use RFC documentation
addresses (192.0.2.0/24, 2001:db8::/32), example.com, and <placeholders>. Keep only product-specific
content here; anything generic belongs in core/. Delete these comments when done.
Copy this folder to skills/<domain>/<product>/ and run scripts/check-content.sh before committing.
-->

# <Product> Security

<One paragraph: the role the agent takes and what it protects against.>

## How to use this skill

This skill holds only <product>-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

<Product>-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

## <Product>-specific principles

<Facts about this product that change how the agent must behave, e.g. "configuration is regenerated on
reboot, so edits to X don't persist".>

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| <e.g. appliance vs. container vs. VM> | | |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- <Vendor-default ports and what answers on them (page titles, banners, certificate names).>
- <mDNS/DNS-SD, SSDP, or other discovery announcements.>
- <MAC address vendors, noting when they don't apply (virtual or rebadged hardware).>

---

## Discover

All operations in this mode are class **R**. Mark anything you can't inspect **Not assessed**.

### Baseline commands

<Candidate read-only commands, each labeled vendor-documented / observed / not yet verified.>

### Assessment domains

<Lettered domains. Each must end with a status in the report. Typical set: platform and lifecycle;
identity and administration; network exposure and remote access; protocols and encryption; add-ons /
plugins / containers; scheduled tasks and persistence surfaces; data protection and backups; monitoring
and logging; physical and availability.>

#### A. <Domain>

- <Check>

---

## Recommend

No changes are made in this mode.

### Dependency and blast-radius check (required)

<What commonly depends on this product's configuration and breaks when it changes.>

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| | | |

---

## Remediate

Apply only approved changes, one at a time, following the core rules. <Product> specifics:

- <Supported change methods; lockout risks; update cautions.>

### Hard stops (refer to a specialist; never automate)

- <Operations that must never be performed as security remediation.>

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the <product>-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### <SHORT>-001: <title>

<A complete, invented finding using the core template and documentation addresses only.>

---

## Version history

- **1.0** (<YYYY-MM-DD>): Initial version.
