---
name: openmediavault
description: >-
  Security assessment, hardening, remediation, and incident response for openmediavault (OMV) NAS systems
  on Debian, including installs on single-board computers and virtual machines. Use when auditing an OMV
  server, reviewing its Workbench web UI and admin account, users and groups, shared folders and SMB/NFS
  exports, SSH, firewall, updates, omv-extras plugins, the compose (Docker) plugin, or the underlying
  Debian host, or when an OMV server may have been compromised or hit by ransomware.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "openmediavault 8.x (Synchrony, Debian 13); 7.x (Sandworm, Debian 12) is end of life since 2026-06 (verify the live version)"
  audience: "home, homelab, work"
  finding_prefix: "OMV"
  modes: "discover, recommend, remediate, respond"
---

# openmediavault Security

Act as a careful, evidence-driven openmediavault security engineer. Identify, explain, prioritize,
remediate (only when authorized), and verify weaknesses that could expose the NAS, its shares, its
containers, or the Debian host beneath it to compromise, ransomware, unauthorized access, service
disruption, or data loss. OMV is a management layer on top of Debian, so an assessment covers both: the
OMV configuration and the operating system it controls.

## How to use this skill

This skill holds only OMV-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

OMV-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation and
advisories are in [references.md](references.md).

Related skills: the Debian host is assessed with [Linux](../../operating-systems/linux/SKILL.md) (but read
the principles below about what OMV owns); containers with [Docker](../../containers/docker/SKILL.md);
ZFS or Btrfs pools with [ZFS and Ceph](../zfs-and-ceph/SKILL.md); backups with
[backup tools](../backup-tools/SKILL.md); remote access through tunnels with
[tunnels](../../edge/tunnels/SKILL.md); a reverse proxy in front of the Workbench or apps with
[web servers](../../web/web-servers/SKILL.md); OMV running as a VM with
[Proxmox VE](../../virtualization/proxmox-ve/SKILL.md). For an appliance comparison, see
[Synology DSM](../synology-dsm/SKILL.md).

## OMV-specific principles

- **OMV owns the services it manages.** Its configuration database (`/etc/openmediavault/config.xml`) is the
  source of truth, and `omv-salt` regenerates the configuration of the services it manages (Samba, NFS,
  nginx, SSH, networking with systemd-networkd, monit, chrony, the firewall, and others). Hand edits to those
  files are overwritten the next time a setting is saved. Make changes in the Workbench, or through
  vendor-documented environment variables and extra-options fields.
- **The underlying Debian host is in scope.** Kernel, Debian security updates, local accounts, SSH keys,
  cron, systemd units, and any software installed outside OMV are part of the attack surface. Use the Linux
  skill for them, but don't apply generic Linux hardening that edits OMV-managed files.
- **Don't treat OMV like general-purpose Debian.** The vendor warns against mixing in Backports, Testing,
  or other distributions, installing Apache, upgrading APT-installed Python packages with pip, and
  installing a desktop environment. Prefer containers for extra software.
- **The Workbench admin is not root, but is root-equivalent.** The built-in `admin` web user (and anyone in
  the `openmediavault-admin` group) can configure services, scheduled jobs, and plugins that run as root.
- **omv-extras is a separate, community project.** It adds repositories and plugins (including the compose
  plugin for Docker) maintained outside the core OMV project. Each plugin is root-level code from that
  repository.
- **Storage repair is a separate discipline.** See the hard stops under Remediate.

## Deployment variants

Identify the variant in Discover. It changes which rules apply.

| Variant | How to recognize it | What changes |
|---|---|---|
| **ISO install on dedicated hardware (AMD64)** | OMV installed from the vendor ISO; OMV is the only role of the host. | All guidance applies as written. |
| **Installed on an existing Debian system** (common on ARM single-board computers) | OMV added to a Debian install, often by a community install script; leftover packages or users from the original image. | Review what was on the host before OMV (default image users, desktop packages, other services). On ARM images the vendor notes that the root password may match the admin password; check both. SD-card boot media wear out and are easy to remove physically. |
| **Virtual machine** (Proxmox VE or another hypervisor) | Virtual NICs and disks; hypervisor guest tools. | The **hypervisor is part of the trust boundary**. Passed-through disks or controllers are usually excluded from VM snapshots and backups, and disk health may need reading on the hypervisor. OMV in LXC or other containers is unsupported by the vendor. |
| **Unsupported or end-of-life release** | OMV 7.x or older (check `dpkg -l openmediavault` and the Debian release). | Treat the platform as unsupported (core: triage end-of-life rule). Plan an upgrade with `omv-release-upgrade` per vendor documentation, after a verified backup. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Workbench web UI served by nginx on HTTP port 80 by default, and HTTPS port 443 when SSL is enabled
  (changeable under System → Workbench). The login page and page title show openmediavault branding.
- SSH on TCP 22 with a Debian OpenSSH banner (root login allowed by default on new installs,
  vendor-documented). SMB on TCP 445, NFS on TCP/UDP 2049 and 111, FTP on TCP 21, and rsync on TCP 873 when
  those services are enabled.
- mDNS/DNS-SD (Avahi): OMV announces enabled services automatically, including the Workbench, SSH, SMB, NFS,
  FTP, and rsync, usually under the host name. Plugins may add announcements. This can't be disabled
  globally (vendor-documented).
- WS-Discovery or NetBIOS names from Samba matching the host name.
- **MAC vendors:** OMV runs on generic hardware, so the MAC shows the NIC or board maker (for example a
  single-board-computer vendor) or the hypervisor's prefix. No OMV-specific OUI exists.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands (SSH, if available)

Prefer the Workbench for OMV settings. If a shell is available, these are *candidate* read-only commands,
**not yet verified** on every release. Check each exists first. Reading the configuration database can
expose credentials (SMTP, plugin secrets, LDAP); record that they exist, never their values.

```sh
dpkg -l openmediavault | tail -1        # OMV version
cat /etc/debian_version; uname -a       # Debian release and kernel
omv-confdbadm read conf.system.network.dns   # example read of one config key (not yet verified on 8.x)
omv-env list                            # OMV environment variables that override defaults
apt-cache policy | grep -E 'http|release'    # configured package repositories
ls /etc/apt/sources.list.d/             # OMV, omv-extras, Docker, and any third-party repos
dpkg -l | grep openmediavault-          # installed plugins
ss -tulpn                               # listening ports and owning processes
iptables-save; ip6tables-save           # effective firewall rules (read only)
cat /etc/exports                        # effective NFS exports (generated by OMV)
testparm -s                             # effective Samba configuration (generated by OMV)
docker ps -a --format '{{.Names}} {{.Image}} {{.Ports}}'
cat /proc/mdstat; lsblk -f              # storage layers (read only; never act on them here)
```

- `omv-salt deploy run …` **changes** service configuration. It is not a read operation; never run it in
  Discover.
- `omv-firstaid` contains reset actions (including the Workbench admin password); use it only in Remediate.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, OMV release, and Debian base

- OMV major version, codename, and Debian base; whether that release is supported (check the vendor's
  releases page; OMV 7 reached end of life in 2026-06).
- Installed OMV and plugin package versions vs. current; pending updates (System → Update Management, or
  `apt list --upgradable`).
- Debian security updates: are they applied promptly? OMV documents a daily update check with automatic
  installation of security updates; confirm on the live system what is actually configured and when
  updates last installed.
- Mixed or unexpected repositories (Backports, Testing, Ubuntu, other third-party sources) and pinning.
- Vulnerabilities in OMV itself and in the Debian packages it relies on (nginx, PHP, Samba, OpenSSH, kernel),
  validated against installed versions (core: triage). OMV's GitHub security page and Debian security
  advisories are the main sources.
- Software installed directly on the host outside OMV (and outside containers): needed? maintained?

#### B. Workbench administration and accounts

- Has the default Workbench password for `admin` been changed? An unchanged vendor-default password on a
  reachable Workbench is critical.
- Members of the `openmediavault-admin` group; separation between admin and everyday accounts.
- Workbench HTTPS: enabled and forced, certificate validity and hostname, and the session timeout. HTTP-only
  administration on a network with untrusted devices exposes the admin password.
- MFA: the Workbench has no built-in second factor as far as the vendor documentation shows (verify on the
  live version). Where MFA is needed, it has to come from the access path (VPN, an authenticating reverse
  proxy or tunnel).
- Users: one per person or service, strong unique passwords, shells set to `nologin` where console access
  isn't needed, **Disallow account modification** where appropriate, stale accounts removed.
- Users created outside OMV (with `useradd`, by images or install scripts) and their shells, groups, and
  `sudo` rights. Default users left from an SBC image are a common finding.
- Root password strength, and whether it matches the admin password (on ARM images it may by default).
- SSH authorized keys for root and every user (existence and comment only).
- Notification (SMTP) credentials and other service accounts: existence and scope only.

#### C. Network exposure, SSH, and remote access

- Every path in: router port forwards (Workbench 80/443, SSH, SMB, NFS, FTP), UPnP/NAT-PMP mappings created
  by containers or other devices, IPv6 reachability, DDNS, VPN plugins (for example WireGuard), tunnels, and
  reverse proxies. Check the router, not just OMV.
- The Workbench should never be reachable from the internet; use a VPN or an authenticated tunnel.
- **SSH (Services → SSH):** enabled only if needed; **permit root login** disabled (the vendor enables it by
  default and recommends disabling it after install); password authentication disabled where keys are in
  use; TCP forwarding off unless needed; extra options reviewed. Only members of the `_ssh` group can use
  SSH (vendor-documented); review that group.
- **Firewall (Network → Firewall):** whether rules exist, whether they cover IPv4 and IPv6, and whether the
  effective `iptables-save` output matches the Workbench. OMV manages only the filter table's INPUT and
  OUTPUT chains; Docker adds its own rules that can bypass host INPUT rules for published container ports.
- Listening ports from `ss`, each mapped to an OMV service, a plugin, a container, or something installed
  outside OMV.
- Zeroconf announcements of services that shouldn't be advertised on untrusted networks (per-service
  environment variables can turn them off).
- External exposure checks only within an authorized scope (core: tool-use contract).

#### D. Shared folders, SMB, NFS, and other file services

- Shared folders: underlying filesystem and path, POSIX ownership and mode (vendor default `2775`
  `root:users`), and ACLs. Effective access needs both the share **privileges** (per user/group) and the
  filesystem permissions; check both.
- Shared folders created on the OS drive (via the sharerootfs plugin) and whether they expose system paths.
- **SMB:** per-share **Public** setting (No, Guests allowed, Only guests). "Guests allowed" with no
  permissions set can give anyone write access (vendor-documented). Also: read-only, browseable, recycle bin,
  home directories, minimum protocol and other global or extra options, and very old clients that force
  legacy protocol support.
- **NFS:** each export's client (single host, network, or wildcard), read/write vs. read-only, and extra
  options. Watch for exports writable by a whole subnet, `no_root_squash`, `insecure`, and the default NFSv4
  pseudo-root. NFS has no user authentication without Kerberos (vendor-documented).
- FTP, rsync server modules, and WebDAV or file-browser plugins: needed? authenticated? exposed?
- Secrets stored on shares (container `appdata`, `.env` files, database dumps, keys).

#### E. omv-extras, plugins, and supply chain

- Is omv-extras installed? Which repositories does it enable (main, Docker, testing, others)? Testing or
  beta repositories on a production NAS are a finding to weigh.
- Every plugin: name, source (core OMV or omv-extras), version, maintained for this OMV release, and
  whether it's needed. Plugins that add a web terminal, file manager, VPN, KVM, or a listening port widen
  the attack surface most.
- How omv-extras (and any install script) was installed: downloaded scripts piped to a root shell should
  have come from the project's documented source over HTTPS.
- Any `.deb` files installed manually or repositories added by hand.

#### F. Compose plugin and containers

Treat each container as an independently exposed workload with a path into the shares. Assess them in
depth with the [Docker skill](../../containers/docker/SKILL.md). OMV-specific checks:

- Compose files and the **global environment file**: secrets present (database passwords, API keys), who can
  read the appdata folder that holds the plugin's copies, and whether example default credentials from
  published compose files were changed.
- Container user (PUID/PGID): the omv-extras guide says never to map containers to root (UID 0) or the
  `admin` user, and never to add the container user to the `docker` group (root-equivalent).
- Volumes: whole data disks or shared-folder parents mounted read/write, system paths, and the Docker
  socket (root-equivalent control of the host, even when mounted `:ro`).
- `privileged`, host networking, added capabilities and devices.
- Published ports, including containers that take ports 80/443 after the Workbench was moved, and whether
  they bypass the OMV firewall.
- Image sources, tags or digests, the plugin's scheduled update and backup jobs, and rollback.
- Docker storage location (default on the OS filesystem) and whether a full disk could take down the
  system.

#### G. Scheduled jobs and persistence surfaces

- **Scheduled Tasks** (System → Scheduled Tasks): command, run-as user (often root), schedule, and who can
  write any script it calls. A root job calling a script on a share others can write to is a privilege-
  escalation path.
- Plugin scheduled jobs (compose backups and updates, rsync jobs, snapshot jobs).
- Host-level persistence outside OMV: crontabs, systemd units and timers, `/etc/rc.local`-style scripts,
  and SSH keys added outside the Workbench.

#### H. Data protection and ransomware resilience

- Filesystems (ext4, XFS, Btrfs, ZFS via plugin, mergerfs, RAID via mdadm) and which support snapshots.
- Snapshot jobs and retention where available, and who can delete them.
- Backups of shared folders, container data, and the OS drive (plugins or external tools): destination,
  schedule, last success, retention, encryption, and key storage (see [backup tools](../backup-tools/SKILL.md)).
- A copy of `config.xml` (or a plugin-based configuration backup) stored off the server; it holds the
  system's configuration and may hold credentials, so protect it.
- **Independence:** can root on this host (or a container with broad mounts) delete every backup copy? At
  least one copy should be outside the server's administrative boundary, offline or immutable.
- Restore testing for data and for rebuilding the OS drive.
- Disk encryption (LUKS plugin): where keys or passphrases live, and whether they unlock automatically.

#### I. Monitoring and logging

- Notifications configured (System → Notification) for SMART, filesystem, monit, and update events.
- Logs: journald persistence and retention, Workbench and nginx logs, SSH authentication logs; forwarding to
  another host so an attacker can't erase all evidence.
- Time and NTP (chrony) correct.

#### J. Storage health, physical, and availability

- SMART status, RAID state, filesystem errors, free space, and OS drive health (SD cards and USB sticks
  wear out). Record only; see hard stops.
- UPS integration (if a plugin is used) and clean shutdown.
- Physical access to the server and its boot media.
- How management access is regained if firewall, SSH, or Workbench port/SSL changes fail: local console,
  `omv-firstaid`, and a known recovery procedure.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state. On OMV, common hidden dependencies
are:

- **SMB/NFS clients** (workstations, media players, hypervisors, backup jobs) using guest access or broad
  exports.
- **Containers** whose PUID/PGID and volume paths assume current ownership and permissions. Recursive
  permission resets (including plugin-provided reset tools) can break every app.
- **Scripts and automation** that log in over SSH as root or with passwords.
- **Remote users** relying on a port forward, VPN plugin, or reverse proxy.
- **Plugins** that depend on other plugins (for example the compose plugin depends on sharerootfs).
- **Hypervisor** (virtualized OMV): host networking changes can affect the VM's reachability.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Default `admin` password | Change it now to a strong, unique password. | Saved logins and integrations need the new password. |
| Workbench over HTTP | Enable HTTPS and force it; use a trusted certificate where possible. | Workbench restarts; bookmarks and port forwards change. |
| Workbench exposed to internet | Remove the forward; use a VPN or an authenticated tunnel. | Remote admins need a new path first. |
| Root SSH login | Disable after creating and testing a named user in `_ssh` and `sudo` with a key. | Automation logging in as root breaks. |
| SSH passwords | Keys only; restrict sources at the firewall or VPN. | Clients without keys lose access. |
| Firewall | Add allow rules for the management path first, then narrow; cover IPv6. | Wrong order locks out the Workbench and SSH; test with a fallback. |
| Guest SMB shares | Set Public to No and grant named users; keep guest only for non-sensitive read-only data. | Clients need credentials. |
| Broad NFS export | Restrict the client to specific hosts; keep `root_squash`; remove `insecure` unless needed. | Plan per client. |
| Unneeded plugins / testing repos | Remove; disable testing repositories. | Check dependents and whether removal deletes data. |
| Containers | Non-root PUID, narrow volumes, no socket mount or `privileged`, secrets out of compose files. | Some images need specific access; test each. |
| EOL OMV release | Upgrade to the supported release with the vendor procedure. | Downtime, plugin compatibility checks, and a full backup first. |
| Backups | Add an independent offline or immutable copy; back up `config.xml`; test a restore. | Cost, capacity, and time. |
| Logging | Forward logs off the host; enable notifications. | Needs a receiving host. |

Changing the SSH or Workbench port is supplementary only. Never recommend it as the main fix.

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. OMV specifics:

- **Use the Workbench, OMV environment variables, and extra-options fields.** Don't hand-edit files OMV
  generates (`/etc/samba/smb.conf`, `/etc/exports`, `/etc/ssh/sshd_config`, nginx's OMV site, network
  files); the next save overwrites them. Settings saved in the Workbench take effect when the pending
  changes are applied.
- **Save `config.xml` first.** Copy it off the host (it may contain secrets) before any change set.
- **Admin access:** never lock out the only admin path. Before disabling root SSH, log in over SSH with the
  replacement user and confirm `sudo` works in a separate session.
- **Firewall:** capture `iptables-save`/`ip6tables-save` first, add the management allow rules before any
  reject rule, and keep a fallback. The vendor suggests a temporary scheduled flush of the INPUT chain while
  testing; if used, remove it afterward and record that it existed.
- **Updates:** use System → Update Management or `omv-upgrade`; for a major release, `omv-release-upgrade`
  per vendor documentation after a verified backup and plugin compatibility check. Don't upgrade through
  plain `apt dist-upgrade` to a new Debian release. Updates that restart services are **C2**.
- **Plugins:** before removing one, check dependents and whether data is removed (**C3** if so).
- **Containers:** back up appdata and compose files, record image digests, change one stack at a time.
- **Permissions:** no recursive ownership or permission resets on shared folders without confirming which
  containers and clients depend on them.
- **Recovery:** `omv-firstaid` can reset the Workbench admin password and network settings from the
  console; know how to reach the console before changing network or Workbench settings.

After each change, follow the core "after a change" steps, and re-run the affected Discover checks.

### Hard stops (refer to a specialist; never automate)

If a RAID array is degraded or rebuilding, a filesystem is read-only, unmountable, or reporting I/O errors,
or a pool reports errors, **stop all hardening, plugin changes, and upgrades**, preserve evidence, and
recommend storage-recovery help. Never, as security remediation:

- Run `mdadm --create`, `mdadm --assemble --force`, `fsck` with repair options, `xfs_repair`,
  `btrfs check --repair`, or ZFS pool repair, import, or destroy operations.
- Wipe, format, or recreate a disk, filesystem, or RAID from the Workbench.
- Delete shared folders, filesystems, or snapshots as a cleanup step.
- Experiment with mount options or mergerfs policies on data disks.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the OMV-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### OMV-001: Root SSH login with passwords allowed, and the Workbench admin still using the default password

**Confidence:** Confirmed
**Priority:** P1. The Workbench admin password is the vendor default and SSH accepts root passwords, so
anyone on the LAN (including a compromised IoT device) can take full control of the NAS and its data.
**State:** Open
**Component:** openmediavault 8.x on Debian 13, Workbench and Services → SSH
**Evidence:** Observed 2026-10-31: the Workbench at `http://192.0.2.30/` accepted the vendor-default
credentials for `admin` during an authorized check; Services → SSH shows Permit root login = enabled and
Password authentication = enabled; `ss -tulpn` shows sshd and nginx listening on all addresses. No firewall
rules configured.
**Expected secure state:** default admin password changed; root SSH login disabled after creating a named
user in `_ssh` and `sudo`; key authentication for SSH (openmediavault installation and SSH documentation).
**Exposure and prerequisites:** any host on `192.0.2.0/24` with a browser or SSH client. No prior
credentials needed for the Workbench.
**Dependencies / blast radius:** a backup script on another host logs in over SSH as root with a password;
it must move to a key-based named user first.
**Recommended remediation:** change the admin password immediately (C1); then create a named user with an
SSH key in `_ssh` and `sudo`, move the backup script to it, disable root login and password authentication
(C2); then enable and force HTTPS for the Workbench.
**Operation class:** C1 for the password change; C2 for the SSH and HTTPS changes.
**Approval required:** Yes. The SSH change is disruptive to the backup script.
**Verification:** the default password is rejected; `ssh root@192.0.2.30` is refused; the named user logs in
with its key and `sudo` works; the backup script's next run succeeds; the Workbench redirects to HTTPS.
**Rollback:** re-enable root login in Services → SSH from the Workbench (not recommended), or use
`omv-firstaid` from the console if the Workbench becomes unreachable.

---

## Version history

- **1.0** (2026-10-31): Initial version.
