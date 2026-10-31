# Automation Platforms: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only steps specific to n8n and Node-RED.

An attacker with editor access to an automation platform has, at minimum, code execution as the
platform's user and every token it stores. Scope the response to **every service the platform holds
credentials for**, not just the platform.

## Triage and containment

- **Indicators:** workflows or flows nobody created, or existing ones changed (new nodes appended,
  especially Code/Function, Execute Command/exec, HTTP request to unfamiliar hosts, or file writes); new
  webhooks; new users, API keys, or an owner account you didn't set up; community nodes or palette
  modules nobody installed; `settings.js` or environment changed (authentication removed, node
  exclusions emptied, env access unblocked); n8n executions at odd times or from unfamiliar webhook
  callers; outbound connections from the platform to unknown addresses; new processes, cron entries, or
  SSH keys on the host; unexpected actions at connected services (mail sent, files deleted, smart-home
  devices operated).
- **Cut inbound paths first:** remove the port forward, proxy route, or tunnel for the editor *and* the
  webhook paths.
- **Stop the platform without deleting state:** `docker stop` the container (or stop the service, or the
  Home Assistant add-on). Stopping halts scheduled and polling triggers that may be exfiltrating data.
  Before stopping flows that control physical devices (heating, locks, pumps), agree with the user how
  those devices will be put in a safe state.
- **Revoke the most dangerous tokens early, from a clean device:** mail, cloud storage, password-manager
  or secrets integrations, payment or AI-provider keys, and the Home Assistant token. Waiting for full
  scoping lets an attacker keep using them.
- **If exec, Execute Command, Code with `child_process`, or the Docker socket was available:** treat the
  host or container host as compromised (switch to that host's skill and the core playbook).

## Evidence to preserve (platform-specific)

Collect before changing anything. These files contain secrets; store them securely and don't share them.

- **n8n:** the data folder (database or SQLite file, settings file with the encryption key) copied with
  the container stopped; Postgres dump if used; execution history (inputs and outputs of recent runs
  show what data left); the workflow list with modification times; `n8n audit` output; the compose file
  and environment; container logs.
- **Node-RED:** the whole user directory (`flows*.json`, `flows*_cred.json`, `settings.js`,
  `package.json`, `node_modules` listing, any runtime config file holding the generated key); logs
  (`journalctl` for the service, `docker logs`, or the add-on log); the Home Assistant add-on
  configuration including `init_commands`, `system_packages`, and `npm_packages`.
- Reverse-proxy and tunnel logs for the editor and webhook paths.
- `docker inspect`, `docker diff`, and image digest for the platform container; host process list,
  crontabs, and authorized SSH keys if command execution was possible.
- Compare current flows with the last known-good export or git history to find exactly what changed.

## Scope checks specific to automation platforms

- **Every credential the platform held:** check each service's audit or sign-in logs for use since the
  earliest plausible compromise, from unfamiliar addresses or at unusual volume. Mail accounts: check
  forwarding rules, app passwords, and OAuth grants.
- **Secrets outside the credentials store:** tokens in Function/Code source, node properties, environment
  variables, and execution data are exposed too.
- **Home Assistant and MQTT:** automations or entities changed through the platform's token; retained
  MQTT messages or ACLs changed (use the home-assistant and mqtt skills).
- **The host and LAN:** anything reachable from the platform's network position (SSRF targets such as
  router and NAS admin pages, cloud metadata endpoints).
- **Queue-mode workers and Redis**, and task-runner containers.
- **Git repositories** used for flow or workflow source control.
- **Community node or palette package supply chain:** if a malicious package is suspected, check other
  instances that installed the same package and report it to the vendor.

## Eradication and recovery

- Rebuild from a clean, current official image or package, not by deleting suspicious flows in place.
- Restore flows or workflows from a known-good export or backup made before the earliest plausible
  compromise; review every Code/Function and command node before importing. Don't reinstall community
  nodes or palette modules until each is reviewed.
- **Rotate everything:** every stored credential (create new tokens at each service, revoke old ones);
  the n8n encryption key or Node-RED `credentialSecret` (set a new key on the rebuilt instance and
  re-enter credentials rather than carrying over the old encrypted store with the old key); user
  passwords and API keys; webhook authentication secrets; database and Redis passwords.
- Before reopening: editor authentication enforced with MFA or behind an MFA auth proxy; editor not on
  the internet; webhooks authenticated; Execute Command/exec excluded unless required; env and file
  access restricted; community packages restricted; running unprivileged without the Docker socket;
  current version; the initial access path closed.

## Quick checklist tailored for automation platforms

Start with the core quick checklist, plus:

- [ ] Remove public routes to the editor and webhooks; stop (don't delete) the platform, after agreeing
      how physical devices it controls will be left safe.
- [ ] From a clean device, revoke the highest-value tokens it held (mail, cloud storage, Home Assistant,
      paid APIs).
- [ ] Copy the data folder or user directory, execution history, and logs off the host.
- [ ] Diff flows against the last known-good copy; list new nodes, webhooks, users, and packages.
- [ ] If command execution was possible, treat the host as compromised.
- [ ] Rebuild clean, re-enter rotated credentials under a new key, then reopen with authentication.
