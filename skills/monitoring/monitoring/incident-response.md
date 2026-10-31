# Infrastructure Monitoring: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only monitoring-specific steps.

A compromised monitoring server is two problems at once. It is a **stolen map and keyring** (every host,
address, and stored credential), and, where remote commands, scripts, or plugins are enabled, it is a
**fleet-wide execution channel**. It is also the system that would have told you about the attack, so
its silence proves nothing.

## Triage and containment

- **Indicators that point at monitoring:** new admin users, API tokens, or automation users nobody
  created; global scripts, actions, agent plugins, local checks, or MKPs nobody added; `AllowKey` or
  remote-command settings changed on agents; silences or maintenance windows covering many hosts
  without a change ticket; alert rules or notification targets changed or deleted; Pushgateway or
  remote-write data for hosts that don't exist; exporters or agents appearing on hosts nobody
  configured; login history from unknown addresses.
- **Cut the execution channel first.** If remote commands may have been abused, stop the Zabbix server
  (or disable the scripts and actions), stop Checkmk's agent bakery and plugin deployment, or block the
  server-to-agent path at the firewall. Prefer a firewall block or stopping the service over deleting
  anything.
- **Remove external access** to the UIs and APIs (port forwards, proxy routes, tunnels) from a clean
  device.
- **Don't trust the monitoring's own view.** Data, alert history, and "all green" can be forged. Check
  hosts directly.
- **Watch for a planned blind spot.** Bulk silences or maintenance windows created shortly before other
  activity suggest the attacker prepared to act elsewhere. Record them before removing them.

## Evidence to preserve (monitoring-specific)

Collect before changing anything. These artifacts contain credentials: store them securely.

- **Zabbix:** the audit log (frontend Reports → Audit log, or the database table), the users, user
  groups, API tokens, global scripts, actions and their operations, and a database dump. Server and
  agent logs.
- **Checkmk:** the site's audit log of configuration changes, users and automation users, installed
  MKPs, rule sets that deploy agent plugins, a site backup, and `var/log` for the site. Agent plugin and
  local-check directories on affected hosts.
- **Prometheus stack:** startup flags (`/api/v1/status/flags`), configuration files and their history,
  Alertmanager silences (`amtool silence query` or the API) and configuration, Pushgateway contents,
  and service logs. A TSDB snapshot only if the user wants metric history preserved and the admin API
  is already enabled; don't enable it just for this.
- **Netdata:** `netdata.conf`, `stream.conf`, collector and notification configs, the claimed Cloud
  space's member list and audit or activity view, and agent logs.
- Reverse-proxy access logs for the monitoring hostnames.
- On monitored hosts: the agent configuration files, PSK files, and any files under plugin, local-check,
  or script directories, with timestamps.

## Scope checks specific to monitoring

- **Every host the server could run commands on.** If execution was enabled, treat each as potentially
  compromised until its logs and persistence surfaces are checked with its own skill (for example
  [linux](../../operating-systems/linux/SKILL.md) or [windows](../../operating-systems/windows/SKILL.md)).
- **Every credential the monitoring held:** SNMP, IPMI/BMC, database, hypervisor, NAS, cloud, SSH keys,
  notification tokens. Check each target's logs for use since the earliest plausible compromise.
- **Netdata Cloud, Grafana Cloud, or other hosted accounts** linked to the monitoring: members, API
  tokens, and claimed nodes.
- **Systems that trust monitoring data:** automations that act on alerts (autoscaling, Home Assistant,
  scripts that restart services) may have been triggered with forged data.
- **The monitoring server's host**, its database, and any container host it runs on.

## Eradication and recovery

- Rebuild the monitoring server from current vendor packages or images and restore configuration from a
  backup taken before the earliest plausible compromise, or recreate it. Review restored users,
  scripts, actions, plugins, MKPs, and alert rules line by line.
- **Rotate every stored credential** and create new read-only monitoring accounts at each target; revoke
  the old ones. New Zabbix PSKs or certificates, new Checkmk agent registrations, new Netdata streaming
  keys and Cloud claim tokens, new Prometheus basic-auth and bearer credentials, new notification
  tokens.
- Remove unauthorized plugins, local checks, and scripts from agents, then re-register agents to the
  rebuilt server.
- Before reconnecting: named admins with MFA, default accounts disabled, remote commands denied except
  named needs, agent encryption enforced, UIs not reachable from the internet, and the initial access
  path closed.

## Quick checklist tailored for monitoring

Start with the core quick checklist, plus:

- [ ] Block server-to-agent command paths (stop the server or disable scripts and actions) and remove
      public access to the UIs.
- [ ] Export audit logs, user and token lists, scripts, actions, plugins, and silences before changing
      anything.
- [ ] List every host the server could run commands on and every credential it held; check them.
- [ ] Verify host health directly, not through the monitoring dashboards.
- [ ] Rebuild, rotate every stored credential, and re-register agents before trusting it again.
