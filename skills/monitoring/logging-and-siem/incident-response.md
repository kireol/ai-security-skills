# Logging and SIEM: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only logging- and SIEM-specific steps.

Two different situations reach this file. In the first, the logging stack is **the evidence** for an
incident elsewhere: preserve it before anything rotates, deletes, or overwrites it. In the second, the
logging stack **is the target**: logs deleted, agents stopped, rules changed, a cluster wiped or
ransomed, or the SIEM's own execution features used against the fleet. Often both are true.

## Triage and containment

- **Indicators that point at the logging stack:** indices missing or replaced by a ransom note index;
  sudden drops in event volume from a source (agent stopped, forwarding removed, input disabled); retention
  shortened; rules, decoders, scenarios, or alerts disabled; new admin users, API keys, or roles; CrowdSec
  machines or bouncers nobody registered, or decisions that unban an address; Fail2ban jails stopped or
  `ignoreip` widened; new Wazuh active-response commands or centralized `agent.conf` changes; journald or
  Windows Security log cleared events on sources.
- **Freeze retention before anything else.** Pause index lifecycle deletion, rotation, and cleanup jobs on
  the stores that hold relevant time ranges, after checking that pausing won't fill the disk and stop
  ingestion. Don't delete anything.
- **Cut external and untrusted access** to the cluster, dashboards, and APIs (9200, 5601, 55000, 9000, the
  LAPI) from a clean device, without stopping ingestion if it's still trustworthy.
- **If the manager can run commands on agents** (active response, centralized configuration with remote
  commands, Fleet integrations), and its compromise is suspected, stop the manager or block its push path
  to agents.
- **Automatic blocking during an incident:** a compromised CrowdSec engine or forged log lines can ban the
  owner or unban the attacker. Check decisions and allowlists; prefer manual firewall containment until
  the engine is trusted again.

## Evidence to preserve (logging-specific)

- **Snapshots or exports** of the relevant indices or log files, taken to a location the logging stack's
  own credentials can't delete. Record the time range and hash the exported files.
- Raw log files on source hosts (journald files, `/var/log`, exported Windows event logs), before rotation.
- The logging stack's own audit logs: Elasticsearch/OpenSearch audit logs if enabled, Wazuh API and
  dashboard logs, Graylog audit or access logs, Kibana or Dashboards logs, CrowdSec logs and `cscli
  machines list` / `cscli bouncers list` / `cscli decisions list` output, Fail2ban log and current
  `fail2ban-client status` for every jail.
- Configuration as it is now: Wazuh `ossec.conf`, `agent.conf`, active-response settings; Graylog
  `server.conf`, inputs, streams; cluster security configuration and users; CrowdSec profiles,
  acquisitions, allowlists, console status; Fail2ban `jail.local` and `jail.d/`.
- Users, roles, API keys, and enrollment state (existence and timestamps, not secret values).
- For a ransomed cluster: the ransom note index or document as found, and the list of indices with
  creation times. Don't pay, and don't contact the attacker from the affected network.

## Scope checks specific to logging and SIEM

- **Every system whose logs were in the store:** what data was exposed (authentication events, personal
  data, secrets that leaked into logs). Secrets found in exposed logs must be rotated at their source.
- **Every agent the manager could command**, if execution features were enabled; check each with its own
  skill.
- **Credentials the logging stack held:** shipper and integration passwords, cloud API keys, snapshot
  repository credentials, alerting connector tokens, CrowdSec Console account.
- **Snapshot repositories:** whether the attacker deleted or altered them; whether the NAS or bucket
  holding them was reached with the same credentials.
- **What the attacker might have hidden:** compare event volumes per source over time; gaps line up with
  activity worth investigating on that source.

## Eradication and recovery

- Rebuild compromised logging servers from current vendor packages or images; restore configuration from
  a backup taken before the earliest plausible compromise and review it (users, roles, rules, responses,
  inputs, allowlists).
- Restore wiped indices from snapshots held outside the cluster's admin boundary, if available.
- **Rotate:** admin and service-user passwords, API keys, Wazuh enrollment password and API users,
  Graylog `password_secret` (this invalidates sessions and stored encrypted values; follow vendor
  guidance) and root password, CrowdSec machine credentials and bouncer keys, certificates if private keys
  were exposed.
- Re-enroll agents and re-register bouncers and machines to the rebuilt services; remove ones that aren't
  recognized.
- Before reconnecting: authentication and TLS on every API, no untrusted or internet exposure, default
  credentials gone, remote command features disabled unless needed, allowlists correct, off-host or
  immutable copies in place, and alerts for ingestion drops.

## Quick checklist tailored for logging and SIEM

Start with the core quick checklist, plus:

- [ ] Pause retention deletion and cleanup for the relevant time range; export or snapshot it to storage
      the stack can't delete.
- [ ] Copy raw logs from affected source hosts before they rotate.
- [ ] Remove untrusted access to the cluster, dashboards, and APIs; stop manager-to-agent command paths if
      the manager is suspect.
- [ ] Check CrowdSec decisions, machines, bouncers, and Fail2ban allowlists for tampering; contain at the
      firewall manually until trusted.
- [ ] Look for gaps in event volume per source; investigate those sources.
