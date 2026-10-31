---
name: truenas
description: >-
  Security assessment, hardening, remediation, and incident response for TrueNAS (Community Edition,
  formerly SCALE, and Enterprise), with notes for legacy TrueNAS CORE. Use when auditing a TrueNAS system,
  reviewing its admin accounts and API keys, web UI and SSH exposure, SMB/NFS/iSCSI shares, apps and VMs,
  ZFS dataset encryption, snapshots, replication, or backups, or when a TrueNAS system may have been
  compromised or its data encrypted or destroyed.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "TrueNAS Community Edition and Enterprise 24.10 and later (25.x current; verify the live release and train); legacy TrueNAS CORE 13.x noted"
  audience: "home, work, homelab"
  finding_prefix: "TNAS"
  modes: "discover, recommend, remediate, respond"
---

# TrueNAS Security

Act as a careful, evidence-driven TrueNAS security engineer. Identify, explain, prioritize, remediate
(only when authorized), and verify weaknesses that could expose the system or its data to compromise,
ransomware, unauthorized access, service disruption, or data loss. On TrueNAS, the biggest risks are
usually not the base OS but who can reach the admin UI and API, what the shares and apps allow, and
whether snapshots and replicas would survive an attacker who gains admin rights.

## How to use this skill

This skill holds only TrueNAS-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

TrueNAS-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md). Related skills:
[ZFS and Ceph](../zfs-and-ceph/SKILL.md) (pool, dataset, snapshot, and replication concepts),
[backup tools](../backup-tools/SKILL.md), [Docker](../../containers/docker/SKILL.md) (TrueNAS apps run on
Docker in current releases), [Proxmox VE](../../virtualization/proxmox-ve/SKILL.md) (virtualized TrueNAS,
or Proxmox as a storage client), [Synology DSM](../synology-dsm/SKILL.md) (a comparable NAS platform),
[web servers](../../web/web-servers/SKILL.md) (reverse proxies in front of apps),
[Cloudflare](../../edge/cloudflare/SKILL.md) and [tunnels](../../edge/tunnels/SKILL.md) (remote-access
alternatives to port forwarding).

## TrueNAS-specific principles

- **TrueNAS is an appliance, not a general-purpose distribution.** The base image is managed by the
  vendor; the package manager is disabled by default and changes to the base system are unsupported and
  lost on update. Configuration lives in the middleware's database, not in `/etc`. Make and read changes
  through the web UI, the TrueNAS CLI, or the documented API.
- **The admin UI and API are the same power.** Anyone who can authenticate to the web UI or the API (with
  a password or an API key) can delete datasets, snapshots, and replication targets. Treat API keys like
  admin passwords.
- **Snapshots are on the same pool.** An attacker with admin rights can destroy them. Ransomware
  resilience depends on a copy outside this system's administrative boundary.
- **Pool upgrades and encryption keys are one-way doors.** Upgrading ZFS pool feature flags can't be
  undone and can break replication to older systems. Losing a dataset's encryption key or passphrase loses
  the data. Treat both as **C3**.
- **Storage repair is a separate discipline.** A security engagement never authorizes pool recovery,
  forced imports, or vdev changes. See the hard stops under Remediate.

## Deployment variants

Identify the variant in Discover. It changes which rules apply.

| Variant | How to recognize it | What changes |
|---|---|---|
| **TrueNAS Community Edition** (Linux-based; called SCALE before 25.04), on user-built hardware | Version string with a year-based number (24.10, 25.04, 25.10, …); Debian-based; Apps and Virtualization menus. | All guidance applies as written. Check the release is one TrueNAS still maintains (vendor software-status page). |
| **TrueNAS Enterprise** (iXsystems appliances, possibly HA) | iXsystems hardware and support contract; may have two controllers. | Same software surface, plus vendor support, possibly IPMI/BMC, HA failover, and Enterprise-only features (such as hardening/STIG options; verify). Coordinate changes with the support contract. |
| **TrueNAS CORE 13.x** (FreeBSD-based, legacy) | FreeBSD version string; Jails and Plugins menus. | CORE is no longer developed; 13.0 receives no updates, and 13.3's maintenance status must be checked on the vendor page. Treat an unmaintained release as end of life (core triage) and plan migration. Jails, plugins, and bhyve VMs replace apps and VMs; command names differ. |
| **Virtualized TrueNAS** | Virtual NICs; disks or an HBA passed through from a hypervisor. | The **hypervisor is part of the trust boundary**: hypervisor admins control the NAS. Check that disks are passed through properly (TrueNAS guidance), hypervisor access, and that hypervisor backups aren't mistaken for data backups. |

TrueNAS has changed its release naming (yearly major versions; a release previewed as 26 has been
renumbered as 27). Read the version from the live system and the vendor's software-status page rather
than assuming a name.

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Web UI and API on the vendor-documented default ports, 80 (HTTP) and 443 (HTTPS), with a page title or
  login page naming TrueNAS and a self-signed default certificate naming TrueNAS or iXsystems.
- The default hostname `truenas`, advertised over mDNS (`truenas.local`), and the same name over
  WS-Discovery or NetBIOS when SMB is enabled.
- SMB (445), NFS (111/2049), iSCSI (3260), or SSH (22) alongside the TrueNAS web UI; these are off by
  default and enabled per service.
- A MAC address vendor (OUI) registered to iXsystems only on iXsystems appliances. User-built systems show
  the NIC maker's vendor, and virtualized systems show the hypervisor's.
- IPMI/BMC web interfaces on the same hardware (separate address) on servers and appliances.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands (SSH or the web shell, if available)

Prefer the web UI, the documented API with a read-only or least-privilege account, and read-only MCP
tools. If a shell is available, these are *candidate* read-only commands, **not yet verified** for every
release. Check each exists first.

```sh
cat /etc/version                      # TrueNAS release (not yet verified on every release)
uname -a
midclt call system.info               # middleware query: version, hostname, uptime (read-only call)
zpool status                          # pool health (read only; never act on it here)
zpool list
zfs list -o name,used,avail,encryption,keystatus,mountpoint
zfs list -t snapshot -o name,creation -s creation | tail -n 20
ss -tlnp                              # listening TCP sockets and owning processes
docker ps --format '{{.Names}} {{.Image}} {{.Ports}}'   # apps on releases that use Docker
```

- `midclt call` can also *change* the system. Use only query or info methods during Discover, and never
  pass `create`, `update`, `delete`, or `do_*` methods.
- Don't run `zpool scrub`, `zpool clear`, `zfs destroy`, or any pool or dataset modification in Discover.
- The admin account may need `sudo` for some reads; note when access was limited.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, release, and lifecycle

- Variant, hardware or hypervisor, release and update train, and whether the release is still maintained
  (vendor software-status page). CORE and older Community releases may have stopped receiving fixes.
- Installed release vs. the latest maintenance release on the same train, and TrueNAS security advisories
  and release-note security fixes (core: triage).
- Update notifications and whether updates are applied promptly.
- Boot environments: present, so a failed update can be rolled back (helpful for remediation planning).
- Unsupported modifications: developer mode, manually installed packages, or edits to the base image.

#### B. Administration, accounts, and API keys

- Root account: password login disabled, with a named admin (`truenas_admin` or a custom admin created at
  install on current releases). The vendor plans to remove root access further; verify current behavior.
- Who holds administrator roles; whether restricted roles (read-only or sharing admins, where supported)
  are used for people and automation that don't need full admin.
- Two-factor authentication (TOTP) enabled for administrators and enforced where the release supports it.
- **API keys:** owner, creation date, expiry, last use, and what uses them (Home Assistant, monitoring,
  backup tools, MCP servers). Current releases link keys to a user and require HTTPS; a key sent over
  plain HTTP is revoked automatically. Record existence and scope only, never key values.
- Local users with shell access, SSH keys, or `sudo`; stale users; shared accounts; SMB-only users
  correctly limited to SMB.
- Directory services (Active Directory, LDAP, IPA): which groups become admins or get share access.
- TrueCommand, TrueNAS Connect, or other remote-management links (if present): who can control the system
  through them, and their account MFA (verify feature names on the live release).
- Login and audit history: unfamiliar sources, repeated failures, API key use from unexpected hosts.

#### C. Network exposure and remote access

- Every path in: router port forwards, UPnP (on the router; TrueNAS doesn't create mappings itself),
  IPv4 and IPv6, DDNS, reverse proxies, tunnels, VPNs, and app ports published through any of them.
- Is the web UI or API reachable from the internet or from untrusted VLANs? TrueNAS's guidance is to keep
  management interfaces on private, trusted networks or a VPN.
- Web UI listen addresses: bound to all interfaces or only a management interface? HTTP redirected to
  HTTPS? HSTS? Certificate valid for the name used? Any setting that restricts which client addresses may
  reach the UI (check whether the live release offers one, and how it's configured).
- IPMI/BMC: on an isolated management network, default credentials changed, firmware current, never
  internet-reachable.
- SSH: off unless needed; if on, root and password login disabled, keys only, TCP forwarding off, and
  weak ciphers excluded (vendor security recommendations).
- Listening ports, each mapped to its service or app.
- External exposure checks only within an authorized scope, recording address family, hostname, port,
  time, and limitations.

#### D. Shares and protocols

- **SMB:** SMB1 off (unless a documented legacy need), NTLMv1 off, guest access, share ACLs and
  dataset ACLs (including inherited entries), `everyone@` or broad groups with modify rights, and SMB
  auditing where available. Admin group members can modify or delete share data; check that group.
- **NFS:** every share's authorized networks and hosts (an empty list allows any host), read-only vs.
  read/write, maproot/mapall settings, and NFSv3 vs. NFSv4 with Kerberos where needed. An export writable
  by a whole subnet lets any device on it read or alter everything on the dataset.
- **iSCSI:** authorized initiators and networks (empty means all), CHAP or mutual CHAP for discovery, and a
  dedicated storage network (iSCSI data isn't encrypted).
- WebDAV, FTP, rsync modules, S3-compatible services, and NVMe-oF targets where present: needed? Exposed?
  Authenticated?
- Dataset permissions on app and share data: world-writable modes, broad ACLs on parents.
- Secrets stored on shares (app configs, databases, API keys).

#### E. Apps, containers, and VMs

Apply the [Docker skill](../../containers/docker/SKILL.md) to apps on releases that run them on Docker
(24.10 and later). Earlier Community releases used Kubernetes (k3s) and third-party catalogs that are no
longer supported; their presence is itself a lifecycle finding.

- Installed apps: catalog (official vs. community vs. custom YAML), image and **digest**, version,
  maintained or not, update status.
- Host-path mounts: apps given whole pools, system datasets, or other apps' data, especially read/write.
- Published ports, host networking, `privileged`, added capabilities, devices (GPU, USB), and the Docker
  socket.
- Run-as user and group for each app, and whether app datasets are owned by a dedicated user.
- Secrets in app configuration, environment variables, or logs; default credentials; open registration.
- VMs and system containers (feature names have changed across 24.10, 25.04, and 25.10): network
  placement, VNC/SPICE display devices (vendor guidance is to disable them once configured), and attached
  zvols or host paths. Experimental features shouldn't hold important workloads.

#### F. Scheduled tasks and persistence surfaces

- Cron jobs and init/shutdown scripts configured in the UI: command, user (often root), and the path of
  any script they call. A root task running a script on a dataset others can write to is a
  privilege-escalation path. Vendor guidance discourages custom scripts; passwords in scripts appear in
  debug files.
- SSH authorized keys for every user; `sudo` rights.
- Custom apps or containers added recently; unexpected API keys, users, or replication tasks.

#### G. ZFS data protection, encryption, and replication

See [ZFS and Ceph](../zfs-and-ceph/SKILL.md) for concepts. Platform-level checks:

- **Periodic snapshot tasks:** which datasets, schedule, and retention vs. change rate and how long an
  attack might go unnoticed. Datasets with no snapshots at all.
- **Who can destroy snapshots:** any full admin, any API key with admin rights, and any remote system with
  push credentials. ZFS holds or retention settings on the *target* only help if the source can't
  override them.
- **Replication tasks:** direction (push vs. pull), SSH connection and keypair used, the target's account
  and privileges, whether the target is in the same admin boundary, retention on the target, and
  last-success time. A pull from the backup system with a restricted source account is more resilient
  than a push that lets the source manage the target.
- **Cloud sync and rsync tasks:** destination, credentials stored on the system, versioning or object lock
  at the destination. See [backup tools](../backup-tools/SKILL.md).
- **Independence:** at least one copy outside this system's admin boundary, ideally offline or immutable.
- **Restore testing:** when a snapshot or replica was last restored to a separate location.
- **Dataset encryption:** which datasets are encrypted; key vs. passphrase; where keys are stored
  (system database vs. passphrase entered at unlock); whether exported keys are backed up off-system;
  and whether encrypted replication targets can be unlocked without the source. Encryption protects data
  at rest and on stolen disks, not against ransomware on an unlocked dataset.
- **Configuration backup:** a recent configuration file, with its secret seed (needed to decrypt stored
  credentials and keys), stored securely off-system. The file with seed is itself sensitive.

#### H. Monitoring, logging, and alerts

- Alert services configured (email or another channel) and actually delivering; alerts for pool health,
  SMART, scrub, snapshot, replication, cloud sync, failed logins, and updates.
- Audit logs (24.04 and later): enabled, reviewed, and retained.
- Remote syslog to another host, so an attacker can't erase all evidence; TLS where supported.
- Correct time and NTP.

#### I. Storage health, physical, and availability

- Pool status, vdev layout, degraded or faulted devices, last scrub results, SMART tests, and free space
  (pools near full degrade performance and snapshot retention).
- For virtualized TrueNAS, whether ZFS sees the real disks (HBA passthrough) as the vendor recommends.
- UPS integration and safe shutdown.
- Physical access to the system and to IPMI; console menu settings (the option to show the console
  without a password should be off).
- Recovery documentation and how management access is regained if a network, certificate, or MFA change
  fails.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state. Common hidden dependencies:

- **Hypervisors and servers** using NFS or iSCSI for VM disks or datastores (Proxmox, other hosts).
  Changing authorized hosts, CHAP, or the storage network can stop running VMs.
- **SMB clients** and mapped drives, including backup software that writes to a share.
- **Apps** whose host-path mounts and UIDs rely on current dataset permissions. Recursive ACL or
  permission changes can break every app on a dataset.
- **Replication partners**: the other end's SSH connection, keypair, and account. Changing SSH settings,
  keys, or the admin account can stop replication silently.
- **Integrations using API keys** (home automation, monitoring, dashboards, MCP servers). Revoking or
  rotating a key breaks them.
- **Remote users** relying on a port forward or reverse-proxy route.
- **Hypervisor** (virtualized TrueNAS): network changes can affect reachability.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| UI/API exposed to internet or untrusted VLANs | Remove the forward; bind the UI to a management interface; use a VPN or authenticated tunnel. | Remote admins need a new path first. |
| Root password login | Use a named admin; disable root password login. | Scripts or integrations using root break; find them first. |
| Admin MFA | Enable 2FA for all admins. | Keep recovery access documented offline. |
| API keys | Remove unused keys; give each integration its own key under a least-privilege user; set expiry where supported. | Each integration must be updated with its new key. |
| HTTP UI | Redirect HTTP to HTTPS with a valid certificate. | Clients using HTTP (and any API key sent over it) stop working. |
| SSH | Disable if unneeded; otherwise keys only, no root, no forwarding. | Push replication and automation over SSH may depend on it. |
| SMB1 / NTLMv1 | Disable. | Very old clients lose access. |
| Open NFS / iSCSI | Add authorized hosts or initiators; add CHAP; move to a storage network. | Plan per client; VMs on the datastore may need a maintenance window. |
| App host paths | Narrow to the app's own dataset; use read-only where possible. | App may need data migrated. |
| App privileges | Remove `privileged`, host networking, and the Docker socket unless required. | Some apps need a device or capability; test each. |
| Snapshot coverage | Add periodic snapshots with retention longer than likely detection time. | Pool capacity. |
| Replication / backups | Move to pull-based replication or an immutable or offline copy outside the admin boundary; test a restore. | Cost and setup on the target. |
| Encryption keys | Export keys and the configuration file with seed to secure off-system storage. | The exported material is sensitive; store it like a password vault. |
| Unmaintained release | Update to a maintained release on the same train, or plan migration (CORE). | Major upgrades may change apps and VMs. |
| Logging | Enable audit review and remote syslog; confirm alerts deliver. | Needs a receiving host. |

Non-standard ports and geoblocking are supplementary only, never the main fix.

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. TrueNAS specifics:

- **Use the web UI, the TrueNAS CLI, or the documented API.** Don't edit files under `/etc` or the base
  image; the middleware regenerates them, and updates replace them.
- **Updates:** confirm a recent verified backup and a saved configuration file, read the release notes,
  and check that a boot environment will allow rollback. Treat updates as **C2** (reboot, possible app or
  VM changes). Major-version upgrades can migrate apps or VMs in ways that don't roll back cleanly; read
  the migration notes. Never downgrade as a speculative fix.
- **Don't upgrade pool feature flags** as part of security work. It's **C3** (irreversible) and can break
  replication or import on older systems. If the UI offers it after an update, leave it for a separate,
  approved decision.
- **Admin accounts and 2FA:** never disable the only working administrator. Test the replacement admin
  (and its 2FA) in a separate session first. Keep a console or IPMI path available.
- **Web UI binding and certificates:** changing listen addresses, ports, or the certificate restarts the
  UI and can lock you out. Keep a console or IPMI path, and test from a second session.
- **API keys:** create and deploy the replacement key before revoking the old one, unless containment
  requires immediate revocation.
- **Shares and ACLs:** capture the existing configuration first. Never apply recursive ACL or permission
  changes to a dataset without confirming which apps and clients depend on it.
- **Apps:** back up app data and configuration, record the image digest or app version, and change one app
  at a time. App updates may migrate data irreversibly.
- **Encryption:** changing a dataset's key or passphrase, or switching between them, is **C3** unless the
  new key is exported and verified first. Never lock or unlock datasets used by running apps or VMs
  without planning the outage.

After each change, follow the core "after a change" steps and repeat the affected Discover checks.

### Hard stops (refer to a specialist; never automate)

If a pool is degraded, faulted, suspended, unavailable, or reporting checksum or I/O errors, **stop all
hardening, app changes, and updates**, preserve evidence, and recommend a ZFS-recovery specialist (or
vendor support for Enterprise). Never, as security remediation:

- Run `zpool import -F`, `zpool import -X`, `zpool clear`, `zpool online/offline/replace/detach`,
  `zpool labelclear`, `zfs rollback`, `zfs destroy`, or any pool or dataset recovery command.
- Export, re-import, or "fix" a pool from the UI before the failing layer is identified and a verified
  recovery plan exists.
- Delete snapshots, datasets, zvols, or replication targets to free space or "clean up."
- Change or remove encryption keys on datasets whose key backup hasn't been verified.
- Run `zpool upgrade`.

---

## Respond

On any P0 indicator (unexpected admins or API keys, deleted snapshots or replication targets, mass file
changes or ransom notes on shares, unknown apps or cron jobs, logins from unknown sources), switch to
Respond immediately. Follow the core playbook plus the TrueNAS-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### TNAS-001: Push replication lets the source destroy every backup copy

**Confidence:** Confirmed
**Priority:** P2. If the primary system's admin access is compromised, an attacker can delete all
snapshots locally and on the only replication target, leaving no recovery copy.
**State:** Open
**Component:** Replication task from the primary pool to a second TrueNAS system, TrueNAS 25.x
**Evidence:** Observed 2026-03-04. The replication task on `192.0.2.30` pushes over an SSH connection that
logs into `192.0.2.31` as that system's full administrator. The target's retention policy is "same as
source." No other backup destination is configured. The last restore test is not documented.
**Expected secure state:** at least one copy outside the primary's admin boundary: pull replication from
the target using a restricted account on the source, or an immutable or offline copy (vendor replication
documentation; core backup guidance).
**Exposure and prerequisites:** requires admin access to the primary (stolen credentials, an exposed UI,
or a compromised API key).
**Dependencies / blast radius:** the replication task and its SSH keypair; one app on the target reads
the replicated dataset read-only.
**Recommended remediation:** reconfigure as a pull task on `192.0.2.31` using a restricted user on the
primary; give the target its own retention, longer than the source's; add an offline copy monthly. Test a
restore.
**Operation class:** C2 (replication stops until the new task runs; no data is deleted).
**Approval required:** Yes. Changes the backup path.
**Verification:** new pull task completes; the primary's admin credentials can't log into the target;
snapshots on the target outlive their source copies; a sample restore succeeds.
**Rollback:** re-enable the captured push task and SSH connection.

---

## Version history

- **1.0** (2026-10-31): Initial version.
