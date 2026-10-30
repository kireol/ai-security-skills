# Core: Modes and Authorization

Every skill in this collection works in four modes. This document defines what each mode allows, how the
agent moves between them, and what authorization each kind of action needs. Product skills add
product-specific checks and steps but never relax these rules.

## The four modes

| Mode | Purpose | May change the system? | Entered when |
|---|---|---|---|
| **Discover** | Inventory the system and report weaknesses with evidence. | No. Read-only operations only. | The engagement starts. Always first. |
| **Recommend** | Propose specific fixes, with consequences, dependencies, verification, and rollback. | No. | Discover has produced findings. No approval needed. |
| **Remediate** | Apply approved changes one at a time and verify each one. | Yes, within the authorization granted. | The user approves specific changes from a Recommend plan, or grants a standing authorization. |
| **Respond** (incident response) | Contain harm, preserve evidence, scope, recover, and prevent recurrence. | Only with approval, except advice the user carries out manually. | Any indicator of compromise appears, in any mode, or the user reports one. |

### Transitions

- **Discover → Recommend:** automatic. Recommendations are advice and change nothing.
- **Recommend → Remediate:** only after explicit approval of the specific changes, or under a standing
  authorization that covers them (see below). Approving a plan approves the changes listed in it, not
  similar changes discovered later.
- **Remediate → Discover:** after each change, re-read the changed state (verification is a Discover
  activity). If verification fails, stop and return to Recommend with the new evidence. Never chain
  speculative fixes.
- **Any mode → Respond:** immediately, on a P0 indicator (see
  [vulnerability-triage.md](vulnerability-triage.md)) or when the user says they think they've been
  compromised. Pause all routine hardening, upgrades, and cleanup.
- **Respond → normal modes:** only when the user agrees the incident is closed, using the exit
  criteria in [incident-response.md](incident-response.md).

The agent states its current mode whenever it changes, so the user always knows whether it may act.

## Operation classes

Classify every operation **before** invoking it. When unsure, use the higher class.

| Class | Definition | Examples | Authorization |
|---|---|---|---|
| **R: Read-only** | Collects state without changing configuration or data. Verify the specific tool really is read-only. | Version inventory, listing users/services, reading logs, checking backup status. | Allowed within the agreed scope. |
| **C1: Reversible change** | Changes a setting that can be restored from a captured prior value, with no expected outage. | Toggling a non-critical option, tightening a single permission. | Explicit approval, or a standing authorization covering it. |
| **C2: Disruptive change** | May interrupt access, authentication, network paths, services, backups, or clients. | Firewall/router rules, SSH/MFA/account changes, service restarts, package or major upgrades, certificate/DNS changes, reboots. | Fresh, specific approval each time, a tested fallback path, and a maintenance window where appropriate. |
| **C3: Destructive / irreversible** | Deletes data or recovery points, alters storage state, or cannot be undone. | Deleting data, snapshots, or backups; wiping/resetting; storage or RAID operations; removing packages together with their data. | Explicit, specific, fresh approval **and** a verified recovery plan. Some C3 operations must be referred to a specialist and never automated (each skill lists them as hard stops). |

## Standing authorization

A standing authorization lets the user pre-approve a bounded class of changes so the agent doesn't ask
each time. It is valid only if the user states all of these fields:

```
STANDING AUTHORIZATION
Target:          <exact system identity, as confirmed in Discover>
Action classes:  C1            (C2 only if each action type is named below; C3 never)
Allowed actions: <e.g. "apply vendor security updates to installed packages, excluding major versions">
Excluded:        <anything explicitly out of scope>
Expires:         <date/time, or "end of this session">
Granted by:      <the user, in this conversation>
```

Rules:

- A standing authorization never covers C3 actions.
- C2 actions are covered only if the action type is named explicitly (for example, "restart the
  media-server container"), and even then the agent announces each action before taking it.
- It expires at the stated time, at the end of the session, or when the user revokes it, whichever comes
  first. It does not carry over to a different target system.
- During incident response, an **emergency standing authorization** may list specific containment actions
  (for example, "disable the public port forward to the NAS"). It must be just as specific; "do whatever is
  needed" is not valid.

## Rules that apply in every mode

- **Read-only by default.** Begin with Discover. Do not change settings, install software, reboot, delete
  files, rotate credentials, or modify firewall rules without the required authorization.
- **One logical change at a time**, or a small batch that can be reversed together. Do not combine
  unrelated firewall, authentication, network, and update changes into one untestable operation.
- **Capture before change.** Record the current value of anything you change, so it can be restored.
- **Keep a way back in.** When changing network, firewall, VPN, SSH, authentication, DNS, or certificates,
  keep an active management session and a tested fallback path. Never disable the only administrator,
  authentication method, network path, or backup before its replacement is verified.
- **Stop on surprise.** If an action behaves unexpectedly, stop, preserve evidence, and roll back if safe.
- **Urgent manual advice is never delayed.** During an incident, tell the user about urgent manual
  containment steps immediately, even while waiting for approval for agent-performed actions.
- **Never autonomously** wipe, factory-reset, reinitialize, format, rebuild storage, delete
  snapshots/backups, or overwrite affected data.
