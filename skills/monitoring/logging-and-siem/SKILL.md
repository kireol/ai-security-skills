---
name: logging-and-siem
description: >-
  Security assessment, hardening, remediation, and incident response for log collection, SIEM, and
  automated-blocking tools: Wazuh (manager, indexer, dashboard, agents, active response), Graylog,
  Elasticsearch/ELK and OpenSearch, CrowdSec (Local API, bouncers, console), and Fail2ban. Also checks
  whether anything is being logged at all, retention, and log integrity. Use when auditing a log or SIEM
  stack, deciding whether logs would survive and reveal an attack, reviewing default accounts, agent
  enrollment, exposed search clusters, or automatic ban rules, or when a logging system may have been
  tampered with.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Wazuh 4.x and later, Graylog, Elasticsearch/Kibana 8.x and later, OpenSearch 2.x/3.x, CrowdSec Security Engine, Fail2ban (verify the live version of each)"
  audience: "home, work, homelab"
  finding_prefix: "SIEM"
  modes: "discover, recommend, remediate, respond"
---

# Logging and SIEM Security

Act as a careful, evidence-driven detection and logging engineer. Logs are how anyone finds out what
happened, so the first questions are plain: **is anything being logged, does it leave the host, how long
is it kept, and could an attacker erase or forge it?** The second set is about the logging stack itself:
a SIEM holds the most sensitive data in the network (authentication events, command lines, sometimes
secrets that leaked into logs), its agents often run as root or SYSTEM, and its automated responses can
block or run things across the fleet. Identify, explain, prioritize, remediate (only when authorized),
and verify weaknesses in both.

## How to use this skill

This skill holds only logging- and SIEM-specific guidance. It builds on the shared core, which always
applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Logging-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

Related skills: per-host logging and Fail2ban on a single server are also covered by
[linux](../../operating-systems/linux/SKILL.md), [windows](../../operating-systems/windows/SKILL.md), and
[macos](../../operating-systems/macos/SKILL.md); CrowdSec on a firewall by
[opnsense](../../network/opnsense/SKILL.md); containers by [docker](../../containers/docker/SKILL.md); the
reverse proxy that most of these protect by [web-servers](../../web/web-servers/SKILL.md); and metrics
monitoring by [monitoring](../monitoring/SKILL.md). Grafana and Loki front ends follow
[self-hosted-web-apps](../../web-apps/self-hosted-web-apps/SKILL.md).

## Logging-specific principles

- **No logs is the most common finding.** In home and small environments the usual state is "each device
  keeps a few days of logs locally and nobody reads them". Assess coverage before tuning anything.
- **Logs on the compromised host are not evidence you can rely on.** An attacker with admin rights can
  delete or edit them. Value comes from copies sent off the host promptly to a place the host's
  credentials can't change.
- **A search cluster with security off is a data breach waiting to happen.** Exposed Elasticsearch and
  OpenSearch clusters are routinely found and wiped or ransomed. Check authentication and binding first.
- **Logs contain secrets.** Tokens in URLs, passwords typed into the wrong field, API keys in debug
  output, and personal data all end up in logs. Treat log stores and exports as sensitive, and never
  paste raw log lines with secrets into a report.
- **Automatic responses are change automation.** Wazuh active response, CrowdSec bouncers, and Fail2ban
  actions block addresses or run scripts without a human. A forged log line or a bad rule can lock the
  owner out or be turned against them. Assess what they can do and who can feed them input.
- **Agents are privileged.** SIEM agents read every log and often run as root or SYSTEM; some can run
  commands pushed from the manager. The manager's admin access is fleet-wide access.
- **Time matters.** Without synchronized clocks, events from different systems can't be correlated.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Local logs only** | journald, syslog files, Windows Event Log, appliance log pages; no forwarding configured. | Domain A (coverage) and H (integrity) are the main findings. Nothing else applies until a collector exists. |
| **Central syslog** (rsyslog, syslog-ng, a NAS log server) | Hosts forward to UDP/TCP 514 or TLS 6514 on one server. | Check transport (UDP plain text, TCP, TLS), who can write to the collector, and retention. |
| **Wazuh** (manager, indexer, dashboard; all-in-one or distributed; packages, OVA, or Docker) | Agents connect to 1514/TCP; enrollment on 1515; API on 55000; indexer on 9200; dashboard on 443. | Indexer is OpenSearch-based and dashboard is OpenSearch Dashboards-based, so domain D applies. Active response and centralized agent configuration create an execution surface. File paths differ between major versions (for example `/var/ossec` on 4.x); verify. |
| **Graylog** (server, MongoDB, OpenSearch or Graylog Data Node) | Web UI and API on 9000; inputs such as GELF on 12201 and syslog. | Initial admin set from configuration; inputs listen only once created, and may accept data from anyone. |
| **Elastic Stack** (Elasticsearch, Kibana, Logstash, Beats, Elastic Agent and Fleet) | 9200 (HTTP), 9300 (transport), Kibana 5601, Logstash Beats input 5044, Fleet Server 8220. | Security is on by default from 8.0; older or deliberately reconfigured clusters may have it off. Fleet can push integrations to agents. |
| **OpenSearch** (OpenSearch and OpenSearch Dashboards) | 9200, 9300, Dashboards 5601. | Security plugin can be disabled; demo configuration ships publicly known certificates. |
| **CrowdSec** (Security Engine, Local API, bouncers, optional Console) | `cscli` present; LAPI on 8080 (local by default); metrics on 6060; bouncers on firewalls, proxies, or hosts. | Decisions from the LAPI are enforced by every bouncer. Console enrollment links the engine to a CrowdSec account. |
| **Fail2ban** | `fail2ban-client` present; `jail.local` or `jail.d/`. | Per-host; bans are firewall rules on that host. |
| **Hosted SIEM or log service** | Agents or forwarders sending to a cloud endpoint. | Assess the account (MFA, members, API keys), what data leaves, and retention terms. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **Wazuh:** agents connect to the manager on 1514/TCP; enrollment service on 1515/TCP; cluster daemon on
  1516/TCP; server API on 55000/TCP (HTTPS); Wazuh indexer on 9200; Wazuh dashboard on 443 with a login
  page naming Wazuh.
- **Elasticsearch / OpenSearch:** HTTP API on 9200 returning a JSON banner with `cluster_name` and a
  version block (Elasticsearch's tagline is "You Know, for Search"; OpenSearch reports a `distribution`
  of `opensearch`), or a 401 with a `WWW-Authenticate` header if security is on; transport on 9300.
  **Kibana** and **OpenSearch Dashboards** on 5601 with matching page titles.
- **Graylog:** web UI and REST API on 9000 with a page titled "Graylog"; GELF inputs commonly on 12201
  (TCP/UDP); syslog inputs on 514 or 1514.
- **Logstash:** Beats input on 5044; monitoring API on 9600 (local by default).
- **CrowdSec:** Local API on 8080 and Prometheus metrics on 6060, both bound to localhost in the default
  configuration; a host serving `/v1/decisions` on 8080 is a LAPI.
- **Syslog collectors:** 514/UDP or TCP, 6514/TCP (syslog over TLS).
- **Fail2ban** has no network listener; recognize it from the host (process, `fail2ban-client`).
- MAC address vendors don't help: these run on general-purpose servers, VMs, and containers.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the product's UI, documented read-only APIs, and configuration files read on the host. These are
*candidate* read-only commands, **not yet verified** for every version; check each exists first.

```sh
# Any host: what is logged and where it goes
journalctl --disk-usage; journalctl --list-boots | tail -3           # local retention
grep -rE '^\s*[^#].*@' /etc/rsyslog.conf /etc/rsyslog.d/ 2>&1         # rsyslog forwarding targets
timedatectl                                                           # clock sync

# Elasticsearch / OpenSearch (no credentials: does it answer?)
curl -s -o /dev/null -w '%{http_code}\n' http://<host>:9200/          # 200 = open without auth; 401 = auth on
curl -sk -o /dev/null -w '%{http_code}\n' https://<host>:9200/

# Wazuh (on the manager; paths differ by version)
/var/ossec/bin/wazuh-control info                                     # version (4.x path)
/var/ossec/bin/agent_control -l                                       # agents and status (4.x path)

# CrowdSec (on the engine host)
cscli version; cscli machines list; cscli bouncers list               # who talks to the LAPI
cscli decisions list --limit 20; cscli console status                 # current bans; console link

# Fail2ban
fail2ban-client status; fail2ban-client status <jail>
fail2ban-client get <jail> ignoreip; fail2ban-client get <jail> bantime
```

- **Authenticated queries need approval and care.** Listing indices, users, or snapshot repositories with
  an admin credential is read-only, but search results contain sensitive data. Query metadata (index
  names, sizes, dates, user and role names), not documents, unless the user asks.
- Configuration files contain secrets: Wazuh `authd.pass` and API credentials, Graylog
  `password_secret` and `root_password_sha2`, Elasticsearch keystores, OpenSearch `internal_users.yml`
  (hashes), CrowdSec `local_api_credentials.yaml` and bouncer API keys. Read for structure; never print
  values.
- **Never** during Discover: log in with default or guessed credentials; enroll or remove agents,
  machines, or bouncers; add or delete decisions or bans; trigger active responses; create inputs; delete
  or close indices; register or delete snapshot repositories; send test events into the SIEM; or run
  `cscli console enroll`.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Coverage: is anything being logged?

- For each important system (firewall, router, NAS, hypervisor, DNS filter, reverse proxy, identity
  provider, servers, Windows and macOS clients), where its logs go: local only, a central collector, or a
  SIEM.
- Which event types are captured: authentication success and failure, admin actions and configuration
  changes, new accounts and group changes, process and service creation, remote-access sessions,
  firewall allows and denies, DNS queries, proxy access logs, backup job results.
- Gaps that matter most: no logs from the firewall or reverse proxy (the edge), no authentication logs
  from the identity provider or NAS, no Windows Security log forwarding, no remote-access logs.
- Whether anyone reviews anything: alerts, a dashboard, a weekly look. Logs no one reads are evidence for
  later, not detection.
- Time synchronization on every source and the collector.

#### B. Retention and capacity

- How long each store keeps data (journald limits, rotation, index lifecycle policies in
  Elasticsearch/OpenSearch, Graylog index set rotation and retention, Wazuh indexer retention).
- Whether retention covers a realistic detection delay (weeks to months, not days). Legal or employer
  requirements for work environments.
- Disk space and what happens when it fills: dropping new events, deleting oldest, or stopping. A full
  disk is an easy way to blind a SIEM.
- Archives: cold storage or snapshots of old indices, and whether they're readable later.

#### C. Wazuh

- Versions of manager, indexer, dashboard, and agents vs. supported releases and Wazuh security
  advisories.
- **Default and initial passwords:** the installation assistant generates passwords for indexer users and
  API users; the vendor Docker deployment documents a default dashboard login (`admin` /
  `SecretPassword`) and default indexer and API credentials in its compose file. Ask whether these were
  changed with the vendor's password tool; check where the installer's password file was left. Never test
  by logging in.
- **Server API** (55000): who can reach it; API users (`wazuh`, `wazuh-wui`, and any added) and their
  roles; whether RBAC limits users.
- **Agent enrollment:** whether password authentication (`use_password` in the `<auth>` section) is on,
  where `authd.pass` lives and its permissions, and whether 1515 is reachable from untrusted networks.
  Without an enrollment password, anyone who can reach 1515 may be able to enroll an agent (verify the
  installed version's default). Agent-manager certificate verification options where used.
- **Active response:** which commands are enabled, which rules trigger them, where they run (the agent,
  the manager, all agents), and timeouts. Custom active-response scripts and who can write to their
  directory. A response triggered by attacker-controllable log content (for example a web request) is
  input the attacker chooses.
- **Centralized agent configuration** (`agent.conf` pushed from the manager): whether remote command
  execution from shared configuration is enabled on agents (it is disabled by default through local
  internal options; verify for the installed version). If enabled, the manager can run commands on every
  agent in the group.
- Dashboard users, roles, and tenants; SSO; who has the admin role.
- File integrity monitoring and vulnerability detection: enabled where wanted, and whether alerts reach
  someone.

#### D. Elasticsearch, Kibana, and OpenSearch (including the Wazuh indexer)

- **Is security enabled?** Elasticsearch 8.x enables authentication and TLS by default at first start
  (it prints an `elastic` password and a Kibana enrollment token). A cluster configured with
  `xpack.security.enabled: false`, an old 7.x cluster, or OpenSearch with the security plugin disabled
  (`plugins.security.disabled: true`) has no authentication at all.
- **Binding and exposure:** `network.host` and published container ports; 9200 and 9300 must not be
  reachable from untrusted segments, and never from the internet. The transport port (9300) should be
  limited to cluster members.
- **OpenSearch demo configuration:** since 2.12 a custom initial admin password is required, but the
  demo configuration still installs demo TLS certificates that are public. A cluster still using demo
  certificates, or upgraded from before 2.12 with the old default admin password, is a finding.
- **Built-in and reserved users:** `elastic` (superuser) used as the daily or application account;
  `kibana_system` and similar service users; OpenSearch `admin` and other reserved users in
  `internal_users.yml`. Anonymous access (`xpack.security.authc.anonymous` or OpenSearch anonymous auth)
  enabled.
- **Roles and API keys:** applications and shippers using superuser credentials instead of a role with
  only write access to their indices; API keys without expiry.
- **Snapshot repositories:** where snapshots go (shared filesystem `path.repo`, S3, NAS); who can
  register or delete repositories and snapshots; whether the cluster's credentials can delete every
  snapshot copy; repository credentials stored in the keystore, not in settings.
- Kibana or Dashboards: exposure, authentication provider, spaces or tenants, saved objects with
  embedded credentials (connectors, alerting actions).
- **Fleet and Elastic Agent** where used: Fleet Server exposure, enrollment tokens (existence and scope,
  never values), and which integrations can run commands or collect sensitive data on agents.

#### E. Graylog

- Version vs. supported releases and Graylog security notices.
- **Initial admin:** set from `root_username` and `root_password_sha2` in `server.conf` (the vendor
  documentation states this root password can't be changed in the web UI). Example and community compose
  files often ship a hash of a well-known password; check whether the hash is a published example. Newer
  versions add a preflight setup step; verify how its initial credentials are generated and whether it
  was completed.
- `password_secret` set to a long random value, unique to this deployment.
- `http_bind_address` (vendor default binds to localhost on 9000) and how the UI is published; TLS on the
  UI or at the proxy.
- **Inputs:** which inputs exist, what they listen on, and whether any accepts data from any source.
  Unauthenticated GELF or syslog inputs reachable from untrusted segments let anyone inject or flood
  events. TLS and client certificates where supported.
- Users, roles, and API tokens; LDAP or SSO; streams and their permissions.
- MongoDB and the OpenSearch or Data Node backend: authentication and binding.

#### F. CrowdSec

- **Local API (LAPI):** listen address (`listen_uri`; localhost by default) and who can reach it. When
  bouncers or engines on other hosts use it, it must listen on the network; then use TLS.
- **Machines** (`cscli machines list`): each registered log processor, whether it's validated, and
  whether any are unexpected. Machines can create and delete decisions; an attacker with machine
  credentials can unban themselves or ban the owner.
- **Bouncers** (`cscli bouncers list`): each remediation component, its last pull time, and whether any
  are stale or unknown. Bouncer API keys can only read decisions, but stale ones should be removed.
- **Console enrollment** (`cscli console status`): whether the engine is linked to a CrowdSec Console
  account, which data sharing and management options are on, and the account's MFA. A console that can
  push decisions or blocklists to the engine is part of the trust boundary.
- **Scenarios, parsers, collections, and the AppSec component:** installed from the hub and updated;
  custom ones reviewed; acquisition files actually point at the logs that matter (a reverse proxy's log
  path inside a container is a common miss).
- **Allowlists:** the owner's management addresses and VPN range allowlisted so a forged attack can't lock
  them out; but not so broad that whole segments are exempt.
- Bouncer placement: a bouncer on the firewall or reverse proxy blocks at the edge; a host-only bouncer
  protects only that host.

#### G. Fail2ban

- Which jails are enabled and whether each watches a log that exists and receives events (a jail on a
  log path that's empty, or on a file when the service logs to journald, bans nothing). `backend`
  matches the system.
- `maxretry`, `findtime`, `bantime`, and incremental bans (`bantime.increment`) where supported.
- `ignoreip`: includes the owner's management addresses; doesn't include whole untrusted segments.
- `banaction` matches the firewall in use (iptables, nftables, firewalld, ufw). **Containers:** bans in the
  host's input chain may not apply to traffic for published Docker ports, which is forwarded rather than
  delivered locally; Docker documents the `DOCKER-USER` chain for host-level filtering of container
  traffic. Verify that bans actually block traffic to the protected service.
- Jails for services behind a reverse proxy see the proxy's address unless the real client address is
  logged; banning the proxy blocks everyone.
- Whether bans and unbans are logged and visible to someone.

#### H. Log integrity and transport

- Forwarding happens promptly (seconds to minutes), not in a nightly batch the attacker can stop.
- Transport: plain UDP syslog is spoofable and readable on the path; prefer TCP with TLS, or the agent's
  encrypted channel.
- The collector's write path: can every source host also delete or rewrite stored logs? Sources should
  only append; administrators of source hosts should not be administrators of the log store.
- Immutable or append-only storage, write-once snapshots, or a second copy outside the SIEM's admin
  boundary for important logs.
- Integrity features where available (journald sealing with `--setup-keys`, signed or hashed archives,
  index snapshots in a protected repository).
- Who can delete indices, change retention, disable inputs, or stop agents, and whether those actions are
  themselves logged and alerted.

#### I. Platform, access, and backups of the logging stack

- Host and container hardening for the SIEM servers (assess with the OS and Docker skills): published
  ports, run-as user, Docker socket mounts in log shippers.
- Exposure of every UI and API (dashboards, 55000, 9000, 5601, 9200) to untrusted segments or the
  internet; MFA or SSO on admin accounts ([mfa](../../identity/mfa/SKILL.md)).
- Backups of configuration (rules, decoders, pipelines, users) and, where needed, data; restore tested.
- Agents' versions and health: agents that stopped reporting are blind spots; alerts for "agent
  disconnected".

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Log shippers and agents** that use current credentials, certificates, or unauthenticated inputs:
  enabling authentication or TLS stops ingestion until each one is updated.
- **Dashboards and integrations** (Grafana, Kibana saved objects, scripts, alerting connectors) that use
  a superuser account.
- **Bouncers and firewall integrations** that depend on the LAPI address and keys.
- **Owner access:** ban rules and active responses can lock the owner out. Check allowlists before
  tightening thresholds.
- **Disk and performance:** turning on more logging or longer retention needs space; plan capacity.
- **Privacy:** collecting more (DNS queries, proxy logs, endpoint process data) captures household or
  staff activity; confirm the user wants that and who may read it.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No central logging | Forward edge (firewall, proxy), identity, NAS, and server auth logs to one collector off those hosts. | Needs a host and disk; start with the edge and authentication. |
| Search cluster without authentication | Bind to the management network immediately; enable security (users, roles, TLS) per vendor procedure. | Every shipper and dashboard needs credentials; plan a window. |
| 9200/5601/55000/9000 reachable from untrusted segments or internet | Remove routes; host-firewall to the management segment; VPN or authenticated proxy for remote use. | Remote viewers need a new path. |
| Default or example passwords (Wazuh Docker defaults, Graylog example hash, old OpenSearch default) | Change with the vendor's password tool or procedure; rotate dependent service users. | Components using the old passwords must be updated together. |
| OpenSearch demo certificates | Replace with the deployment's own CA and node certificates. | Cluster restart; clients must trust the new CA. |
| Superuser used by shippers or apps | Create a role with write access to specific indices only; API keys with expiry. | Each shipper's config changes. |
| Wazuh enrollment without password, 1515 exposed | Enable password authentication, restrict 1515 to agent segments, rotate the password after enrollment campaigns. | New agents need the password at install. |
| Active response on attacker-influenced events | Limit to well-tested rules, use timeouts, allowlist management addresses; avoid destructive scripts. | Fewer automatic blocks. |
| Remote commands via centralized config enabled | Disable unless needed; if needed, limit to specific agent groups and audit changes. | Features relying on it stop. |
| Unauthenticated Graylog or syslog inputs on the LAN | Restrict by firewall to known sources; use TLS inputs with client certificates where supported. | Sources not updated stop sending. |
| CrowdSec LAPI on the network without TLS; stale machines or bouncers | Enable TLS, remove stale entries, validate only known machines. | Remote components need new config. |
| Fail2ban jail not effective (wrong log, wrong chain) | Fix the log path or backend; use a ban action that covers container traffic; test with a controlled source. | Brief testing effort. |
| Short retention | Extend to cover realistic detection delay, with capacity planned; archive to cold storage. | Disk cost. |
| Logs deletable from source hosts | Append-only forwarding; separate admin of the log store; immutable or offline copy. | More setup; separate credentials to manage. |
| Plain UDP syslog across segments | TCP with TLS, or the agent's encrypted transport. | Some devices only support UDP; isolate those paths instead. |
| No alerts on log pipeline failures | Alert on agent disconnects, ingestion drops, and disk thresholds. | Some noise to tune. |

Hiding ports or renaming indices is supplementary only. Never recommend it as the main fix for an open
cluster.

Group the plan: immediate containment (if any) → urgent fixes (open search clusters, internet-exposed
SIEM UIs or APIs, default credentials) → high-priority hardening (coverage of edge and identity logs,
enrollment and input authentication, off-host forwarding) → routine maintenance (retention, updates,
stale agents) → optional defense in depth (immutability, integrity sealing). Then ask for approval (core:
modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Logging specifics:

- **Back up configuration first:** Wazuh `ossec.conf`, rules, decoders, and `agent.conf`; Graylog
  `server.conf` and content packs; Elasticsearch/OpenSearch security configuration (for OpenSearch, the
  security index via the vendor's admin tool); CrowdSec `config.yaml`, acquisitions, and profiles;
  Fail2ban `jail.local` and `jail.d/`.
- **Enabling security on a running cluster** is C2: follow the vendor's procedure for the exact version,
  set credentials for every shipper and dashboard, and expect a restart.
- **Password and certificate changes** use the vendor's tools (Wazuh's password tool, `elasticsearch-reset-password`,
  OpenSearch `securityadmin`). The user chooses and stores new passwords.
- **Ban and response rules:** confirm allowlists contain the owner's management path before lowering
  thresholds or enabling new active responses. Keep a second session open.
- **Inputs and transport changes in batches:** move a few sources to the new authenticated or TLS input,
  confirm ingestion, then the rest; close the old input last.
- **Retention changes:** shortening retention deletes data, which is **C3**. Lengthening it is C1 if capacity
  allows.
- **Updates:** read release notes; for Wazuh, Elasticsearch, and OpenSearch, upgrade components in the
  vendor's documented order and keep agents within the supported version skew.

After each change, follow the core "after a change" steps: confirm events still arrive from every
affected source, alerts and bans still work (with a controlled test the user approves), the closed path
is closed, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Logging in with default or guessed credentials, even to confirm a finding.
- Deleting or closing indices, deleting snapshots, or shortening retention without explicit approval and
  a verified copy of anything needed for an investigation.
- Clearing logs, decisions, or ban lists on a system that may be under investigation.
- Injecting test attacks or forged log lines into production to "test detection" without explicit
  approval and a planned, controlled source.
- Enabling remote command execution or new active-response scripts as part of remediation.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the logging-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### SIEM-001: Log search cluster answers without authentication on the whole LAN

**Confidence:** Confirmed
**Priority:** P2. Anyone on the LAN can read every stored event (authentication logs, proxy logs with
query strings) and delete all indices. No port forward or tunnel route reaches it; if one did, this
would be P1, since exposed clusters are routinely wiped by automated attacks.
**State:** Open
**Component:** OpenSearch cluster (single node, version as reported by the API) used as the backend of a
log stack, running in a container
**Evidence:** Observed 2026-04-02: `curl http://192.0.2.30:9200/` from a LAN workstation returned HTTP 200
with the cluster banner; no credentials sent. The compose file sets `plugins.security.disabled=true` and
publishes `9200:9200` on all interfaces. The router has no forward for 9200 (observed in its NAT table).
OpenSearch documentation describes the security plugin as providing authentication, authorization, and
TLS (vendor-documented).
**Expected secure state:** security plugin enabled with the deployment's own certificates and a unique
admin password; port 9200 published only to the log stack's internal network or the management segment.
**Exposure and prerequisites:** any device on `192.0.2.0/24`, including IoT devices; no credentials.
**Dependencies / blast radius:** the log ingester and the dashboard container connect to the cluster
without credentials; both need users and the CA certificate.
**Recommended remediation:** first (immediate), stop publishing 9200 on the host and reach it only on the
compose network. Then, in a window, enable the security plugin with generated certificates, create a
writer role for the ingester and a read role for the dashboard, and set the admin password with the
vendor procedure.
**Operation class:** C1 for the port change; C2 for enabling security (cluster restart, clients
reconfigured).
**Approval required:** Yes.
**Verification:** from a LAN workstation, 9200 refuses connections; from the compose network, a request
without credentials returns 401; the ingester and dashboard work with their new users; new events
appear.
**Rollback:** restore the captured compose file and cluster configuration (keep the port restriction
even if enabling security is rolled back).

---

## Version history

- **1.0** (2026-10-31): Initial version.
