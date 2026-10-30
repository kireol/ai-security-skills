---
name: proxmox-ve
description: >-
  Security assessment, hardening, remediation, and incident response for Proxmox Virtual Environment (single
  hosts and clusters), including the server hardware's BMC (iDRAC, iLO, IPMI). Use when auditing a Proxmox
  VE host or cluster, reviewing its package repositories, web UI and SSH exposure, realms, two-factor
  authentication, users, roles, ACLs, API tokens, firewall, backup jobs and Proxmox Backup Server, storage,
  passthrough, containers, or cluster network, or when a Proxmox VE host or any of its guests may have been
  compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Proxmox VE 9.x on Debian 13; 8.x is end of life since 2026-08 (verify the live version)"
  audience: "home, work, homelab"
  finding_prefix: "PVE"
  modes: "discover, recommend, remediate, respond"
---

# Proxmox VE Security

Act as a careful, evidence-driven virtualization security engineer. The hypervisor is the trust boundary
for every guest on it: whoever controls a Proxmox VE host, its cluster, or its API controls every VM and
container, including any virtualized firewall, NAS, or DNS server, and can read their disks, memory, and
consoles. A bad change here can stop every guest at once, or cut off the agent's own access. Identify,
explain, prioritize, remediate (only when authorized), and verify weaknesses in the host, the cluster, its
management plane, its backups, and the hardware underneath.

## How to use this skill

This skill holds only Proxmox VE-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Proxmox VE-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

## Proxmox VE-specific principles

- **The host is above every guest.** Host root, the `root@pam` account, any user with `Administrator` on
  `/`, and anyone with BMC or physical access can read and change every guest. Rate host findings by the
  most sensitive guest on it: a weakness on a host that runs the network's firewall is a firewall weakness.
- **Know which guests the agent depends on.** If the firewall, DNS, VPN, or the agent's own machine runs as
  a guest here, then host reboots, firewall changes, network changes, and storage problems can cut off the
  agent and the user. Treat any change that could stop those guests as **C2**, and confirm an out-of-band
  path (physical console or BMC) first.
- **`/etc/pve` is a cluster-wide database, not ordinary files.** It is the Proxmox cluster filesystem
  (pmxcfs), replicated to every node. A change there takes effect on all nodes at once. Make changes through
  the web UI, the API, or the documented CLI tools (`pveum`, `pvesm`, `qm`, `pct`, `pvecm`), not by
  hand-editing files.
- **Secrets live under `/etc/pve/priv/`.** It holds the built-in realm's password hashes, TFA data, API
  token secrets, storage passwords, and backup encryption keys. Never print, copy, or upload files from it.
  Read only metadata (names, dates, permissions) and redact.
- **The firewall is off by default.** The datacenter-level firewall is disabled on a new install, and
  enabling it at node or guest level has no effect until it is enabled at datacenter level. Enabling it
  wrongly can lock out the web UI, SSH, and cluster traffic.
- **Backups are the recovery plan for every guest.** No backup job, backups stored only on the same host,
  or backups that an attacker with host root can delete all mean one incident can lose everything.
- **The BMC is a second front door.** iDRAC, iLO, and generic IPMI give power control, a remote console,
  and virtual media below the operating system. Ask the user about BMC credentials and network placement;
  **never** test BMC logins, try default credentials, or run IPMI tools against it.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Single host** | `pvecm status` reports no cluster; one node in the web UI tree. | No corosync; host backups and configuration copies are the only recovery. |
| **Cluster** | Several nodes under Datacenter; `/etc/pve/corosync.conf` exists. | One admin login, ACL, or firewall change affects all nodes. Assess the corosync network, node-to-node SSH, and every node's exposure. A compromise of any node is a compromise of the cluster. |
| **Cluster with Ceph** | Ceph panel populated; Ceph repositories configured. | Ceph public and cluster networks are more surfaces to isolate; storage health is a specialist area (hard stops). |
| **Enterprise repository (subscription)** | `pve-enterprise.sources` enabled; valid subscription in the UI. | Vendor-recommended for production. |
| **No-subscription repository** | `proxmox.sources` with the `pve-no-subscription` component. | Supported for use, but the vendor says it is less tested and not recommended for production. Updates still need to be applied. |
| **Test repository** | `pve-test` component enabled. | Vendor-intended for testing only; a finding on any host that runs real workloads. |
| **Server hardware with a BMC** | Enterprise server; BMC web UI on the network; the user confirms. | The BMC is part of the trust boundary. Check its network placement and firmware with the user. |
| **Proxmox VE nested inside another hypervisor** | Virtual NICs on the host itself; the user confirms. | The outer hypervisor is above this one; assess it too. |
| **Paired with Proxmox Backup Server** | A storage of type `pbs`; a separate backup server. | The backup server's admin access, datastore permissions, and encryption keys become part of recovery. Assess it as its own system. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Web UI and REST API on HTTPS **port 8006** (vendor default), page title ending in "Proxmox Virtual
  Environment", and a self-signed certificate issued by the cluster's own Proxmox CA on a fresh install. No
  service on port 443 by default.
- SPICE proxy on TCP 3128 and SSH on TCP 22 with a Debian OpenSSH banner. In clusters, corosync on UDP
  5405-5412 between nodes. Proxmox Backup Server, if present, answers on HTTPS port 8007.
- No mDNS or SSDP announcement by default.
- **Guests:** Proxmox VE generates guest MAC addresses with the prefix `BC:24:11`, the IEEE OUI registered to
  Proxmox Server Solutions GmbH (the `mac_prefix` datacenter option; verify on the installed version). Many
  devices with that OUI suggest a Proxmox host nearby. Older installs, custom `mac_prefix` values, and
  manually set MACs show other values (often random locally administered addresses).
- **The host itself** shows the vendor of its physical NIC, not a Proxmox OUI.
- **BMCs** show the server maker's or BMC chip's OUI and usually a web UI on 443 and IPMI on UDP 623.
  Don't probe IPMI beyond recording that the port answers.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer the web UI, the API with a read-only token, or user-run checks. For API access, ask the user to
create a dedicated user (in the built-in `pve` realm) with the `PVEAuditor` role on `/` and a
privilege-separated API token. `PVEAuditor` can read configuration but not secrets or consoles. If shell
access is available, these commands are candidates. Lines marked *vendor-documented* appear in the Proxmox
VE admin guide or man pages; the rest are **not yet verified** on every version. Check each exists first.

```sh
pveversion -v                         # package versions (vendor-documented)
cat /etc/os-release                   # Debian base release
cat /etc/apt/sources.list.d/*.sources   # repositories (deb822 format on 9.x)
apt list --upgradable                 # pending updates; run after the user's normal apt update, or skip
pvecm status; pvecm nodes             # cluster membership and quorum (vendor-documented)
qm list; pct list                     # VMs and containers on this node (vendor-documented)
qm config <vmid>; pct config <ctid>   # one guest's configuration (vendor-documented)
pvesm status                          # storages and usage (vendor-documented)
cat /etc/pve/storage.cfg              # storage definitions (no passwords; those are under priv/)
pveum user list; pveum group list; pveum role list; pveum realm list    # (vendor-documented)
pveum acl list                        # ACLs (vendor-documented)
pveum user token list <userid>        # tokens per user, no secrets (vendor-documented)
pveum user tfa list                   # which users have which second factors (vendor-documented)
pveum user permissions <userid>       # effective permissions (vendor-documented)
cat /etc/pve/jobs.cfg                 # backup jobs (vendor-documented location)
pve-firewall status                   # firewall state (vendor-documented)
cat /etc/pve/firewall/cluster.fw; cat /etc/pve/nodes/<node>/host.fw     # firewall rules
cat /etc/default/pveproxy             # web UI allow/deny lists, if the file exists
ss -tulpn                             # listening services
systemctl list-units --type=service --state=running; systemctl list-timers --all
ls -l /etc/systemd/system/ /usr/local/bin/ /usr/local/sbin/; crontab -l; ls -l /etc/cron.*
```

- **Never run** in Discover (all are C2 or C3): `qm destroy`, `pct destroy`, `qm stop`/`shutdown`/`reset`,
  `pct stop`, `qm rollback`, `qm delsnapshot`, `qmrestore`/`pct restore`, `vzdump` (writes data and can
  freeze guests), `pvesm free`/`remove`/`set`, any `zpool`/`zfs`/`lvremove`/`ceph` change, `pvecm add`,
  `pvecm delnode`, `pvecm expected`, editing `corosync.conf`, `pve-firewall start`/`stop`, `pveum ... modify`
  or `delete`, `qm guest exec`, `qm guest passwd`, `apt upgrade`/`dist-upgrade`, and reboots.
- **Never read** files under `/etc/pve/priv/` (shadow, TFA, tokens, storage keys, `authorized_keys`
  content), `/etc/pve/priv/storage/*.enc` or `*.pw`, `/etc/corosync/authkey`, or private keys under
  `/etc/pve/local/` and `/root/.ssh/`. List names and permissions only.
- `qm config` and `pct config` may show cloud-init user names and SSH public keys; that is fine. If any
  output contains a password, redact it.
- `apt update` changes only the package lists, but ask before running it; on the enterprise repository
  without a valid subscription it reports errors, which is itself useful evidence.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, version, and repositories

- Major release and Debian base (`pveversion -v`, `/etc/os-release`). Proxmox VE 8 (Debian 12) reached end
  of life in 2026-08; a host still on 8.x is an end-of-life finding (core triage). Confirm the current
  lifecycle in the vendor FAQ.
- Pending updates and when the host was last updated. Compare against the Proxmox VE security advisories
  forum section and Debian security advisories (core triage: validate before rating).
- Repositories: which Proxmox repository is enabled (enterprise, no-subscription, test), and whether the
  enterprise repository is enabled without a valid subscription (updates silently fail). The Debian base
  and `trixie-security` repositories must stay enabled. Note legacy one-line `sources.list` entries.
- Any third-party repository, or packages not from Debian or Proxmox (`apt list --installed` and origin).
- Ceph repository and Ceph release, if Ceph is used; check its end of life on the vendor repository page.
- Kernel running versus installed (a pending reboot means fixes aren't active yet).
- On clusters: all nodes on the same version.

#### B. Realms, authentication, and two-factor

- Realms (`pveum realm list`): `pam` (Linux accounts on that node), `pve` (built-in), LDAP, Active
  Directory, OpenID Connect. For each: who it serves and whether the default realm in the login form is
  appropriate.
- `root@pam` is an unconfined administrator that cannot be deleted. Is it used for daily work? Does it have
  a strong, unique password and TFA? Is there a documented break-glass path?
- Linux users on each node with a login shell (pam-realm users can log in to the UI).
- **TFA:** which users have TOTP, WebAuthn, or recovery keys (`pveum user tfa list`). Admin users without
  TFA are a finding. Whether a realm enforces TFA. Recovery keys exist and are stored off the host.
- LDAP/AD: bind over LDAPS or StartTLS, certificate verification on, a least-privilege bind account, and
  sync settings (which groups map in, whether removed users are removed).
- OpenID Connect: issuer, autocreate setting (autocreated users get whatever ACLs their groups have), and
  claim mappings.
- Disabled or expired users: disabling does not end existing sessions or running tasks.

#### C. Users, roles, ACLs, and API tokens

- `pveum acl list` and `pveum user permissions` for each user and group. Record who has `Administrator`
  on `/`, and every grant with propagation on a high-level path (`/`, `/vms`, `/storage`, `/nodes`).
- Treat these privileges as full-admin equivalent and confirm only fully trusted admins hold them:
  `Permissions.Modify` (can grant itself anything), `Sys.Modify`, `Sys.Console` (node shell and console
  access), `Realm.Allocate`, `User.Modify` with broad scope, `Datastore.Allocate`, and VM config privileges
  on guests that host the firewall or other critical services. Verify the current privilege list in the
  admin guide; privileges change between releases (for example, 9.0 removed `VM.Monitor` and made
  creating privileged containers require `Sys.Modify`).
- Custom roles: list their privileges; look for roles that quietly include the ones above.
- **API tokens** (`pveum user token list <userid>` for each user): owner, comment, expiry, and whether
  **privilege separation** is on. With it on (the default), a token gets only its own ACLs, intersected
  with the user's. A token without privilege separation carries its user's full rights; on `root@pam` that
  is unconfined root over the API. Flag tokens with no expiry, no known purpose, or full privileges.
- Integrations that hold tokens (monitoring, Terraform, backup tools, dashboards, home automation): what
  each can do and where its secret is stored.
- Resource pools and their ACLs.

#### D. Management-plane exposure (web UI, API, SSH, consoles)

- Is port 8006 (or 22, 3128, 5900-5999) reachable from the internet? Check upstream port forwards, reverse
  proxies, and tunnels. The web UI should never be exposed directly. Test from outside only with explicit
  authorization.
- Which internal segments can reach 8006 and 22. Ideally only a management network or admin hosts.
- `/etc/default/pveproxy`: `ALLOW_FROM`, `DENY_FROM`, `POLICY` (default allow), `LISTEN_IP`. Note the
  vendor's advice against setting `LISTEN_IP` on cluster nodes.
- Web UI certificate: self-signed, internal CA, or ACME. A self-signed certificate trains users to click
  through warnings.
- Reverse proxy in front of the UI: it must pass WebSockets for consoles, and it becomes part of the
  exposure.
- SSH: `PermitRootLogin` and `PasswordAuthentication` values. In clusters, root SSH between nodes is used
  for cluster actions, and the vendor setup allows root login; prefer keys only, with the firewall
  limiting who can reach port 22. Review `/root/.ssh/authorized_keys` (it links to the cluster-wide file):
  every key should be a current node or a known admin. Removed nodes' keys stay there until deleted.
- Fail2ban or similar on the UI and SSH logins, if used.

#### E. Proxmox VE firewall

- Datacenter firewall enabled? (Off by default; node and guest settings do nothing until it is on.)
- Datacenter input policy, and the `management` IPSet: which hosts may reach the UI, SSH, VNC, and SPICE.
- Node-level rules (`host.fw`) and whether the host firewall is enabled on every node.
- Per-guest firewall: enabled on the guest **and** on each virtual NIC (each NIC has its own firewall flag).
  For guests that should be isolated, check that the guest's own firewall is on and its policies are set.
- `macfilter` (on by default) and `ipfilter` (off unless enabled) on guests that untrusted users control:
  without them, a guest can spoof addresses on the bridge.
- Security groups, aliases, IPSets: stale or overly broad entries.
- Which firewall backend: the classic `pve-firewall` (iptables) or the nftables `proxmox-firewall`. The
  vendor lists the nftables backend as a technology preview; note it, and verify its status on the
  installed version.
- If the firewall is off by design (for example, an upstream firewall handles everything), record that as a
  decision and check that the upstream really separates management from guest networks.

#### F. Host networking and segmentation

- Bridges and VLANs (`/etc/network/interfaces`, SDN zones and VNets): does the host have an address on a
  bridge that also carries untrusted or WAN traffic? A host address on the WAN bridge of a virtualized
  firewall puts the hypervisor on the internet.
- Is management on its own VLAN or NIC, separate from guest traffic?
- Virtualized firewall WAN: passed-through NIC or bridge (if bridge, no host IP on it).
- Cluster, migration, Ceph, and storage (NFS/iSCSI) traffic on separate, non-routed networks where possible.
- IPv6: the host may get SLAAC addresses on bridges where no one expects it.

#### G. Guests: containers, passthrough, and guest agent

- Containers: **unprivileged** is the default for new containers; list any privileged containers
  (`unprivileged` not set in `pct config`). The vendor says privileged containers should only be used in
  trusted environments, and container escapes from them aren't treated as security issues upstream.
- Container features: nesting, `keyctl`, FUSE, NFS/CIFS mounts, bind mounts of host paths (`mp` entries
  pointing at host directories), device passthrough, and raw `lxc.*` lines in `/etc/pve/lxc/<ctid>.conf`,
  especially `lxc.apparmor.profile = unconfined` or capability changes. Each widens the path to the host.
- PCI and USB passthrough (`hostpci`, `usb` entries, and resource mappings): a passed-through device gives
  the guest direct hardware access; check IOMMU is enabled and which guests hold which devices.
- QEMU guest agent: where enabled, anyone with the right privileges on that VM can run commands inside it
  (`qm guest exec`), set guest passwords (`qm guest passwd`), and read or write guest files. That is useful
  and expected, but it means VM-level ACLs equal admin of that guest's operating system. Note which guests
  have it and who holds VM privileges on them.
- Hookscripts (`hookscript` in guest configs): each runs on the host during guest lifecycle events. List
  them and read them.
- Templates and cloud-init: default passwords or shared SSH keys baked into templates.
- Guests that are untrusted (lab, malware analysis, internet-facing): on a separate bridge/VLAN with
  firewall enabled, and without passthrough or privileged features.

#### H. Storage

- `pvesm status` and `/etc/pve/storage.cfg`: types (local, LVM-thin, ZFS, NFS, CIFS, iSCSI, Ceph, PBS),
  which nodes, and which content types (images, backups, ISO, snippets).
- Network storage: who else can reach the NFS export or SMB share (other hosts on the LAN, guests)? A
  writable backup or disk-image share is a path to tamper with every guest.
- Storage credentials (CIFS passwords, PBS passwords) are stored on the host under `/etc/pve/priv/`: note
  which accounts they are, and whether those accounts have more rights than needed.
- Disk encryption at rest, if the threat model includes stolen disks or hardware disposal.
- Storage health is a status item only. Don't run repair or pool operations (hard stops).

#### I. Backups and recovery

- **No backup jobs configured** (`/etc/pve/jobs.cfg` has no `vzdump` entries, or Datacenter → Backup is
  empty): a finding, usually high priority. Check the "guests not covered by a backup job" view if the
  installed version offers it.
- Each job: schedule, which guests (all, a pool, a list, or excludes), mode (snapshot, suspend, stop),
  target storage, retention (`prune-backups` / `keep-*`), notifications, and whether it is enabled.
- Where backups land: on the same host or same disks as the guests is not a backup. Prefer a separate
  Proxmox Backup Server or other separate storage, plus an off-site copy.
- **Proxmox Backup Server:** client-side encryption is optional and off by default. If used, the key is on
  the host under `/etc/pve/priv/storage/`; ask whether a copy exists elsewhere (password manager, paper
  key). Without it, encrypted backups can't be restored. Note any master key setup.
- Can an attacker with host root delete the backups? Check whether the PVE host's backup account can prune
  or delete, and whether the backup server has protected backups, its own admin separation, or an offline
  or sync copy the host can't reach.
- Restore testing: when was a guest last restored as a test? Untested backups are a finding.
- Host configuration: guest backups don't include the host's own configuration (`/etc/pve`, networking,
  custom scripts). Ask how the host would be rebuilt.
- Snapshots are not backups; note old snapshots that consume space or hold outdated sensitive state.

#### J. Host customization and persistence surfaces

- Custom systemd units and timers (`/etc/systemd/system/`), cron jobs, and scripts in `/usr/local/bin`,
  `/usr/local/sbin`, `/root`, and snippet storage. For each: what it does, who added it, whether it is still
  needed, and whether it handles secrets.
- Community helper scripts or "post-install" scripts run from the internet: what they changed
  (repositories, subscription nag removal patches, added packages, cron jobs). They run as root and
  persist; record them and check their source.
- Extra packages or services on the host (Docker, web servers, agents). Each one is host attack surface
  running as root next to every guest; such workloads usually belong in a guest.
- Monitoring or backup agents with root access, and their update path.

#### K. Clustering and shared secrets

- `pvecm status`: quorum, node count, number of corosync links, and whether `secauth` or Kronosnet
  encryption is on (verify how the installed version reports this).
- Corosync network: dedicated, low latency (the vendor asks for under 5 ms), redundant links, not
  reachable from guest or user networks. Anyone on that network can disrupt quorum.
- Two-node clusters: a QDevice for the third vote? The QDevice host gets the cluster's SSH key; assess it.
- Migration network and type in `datacenter.cfg`: `insecure` sends guest RAM unencrypted; acceptable only
  on a network the user fully controls.
- HA configuration and fencing: an unexpected fence can reboot nodes.
- Shared secrets: the corosync authkey, cluster SSH keys, the cluster CA, and storage credentials are shared
  by every node. Note them for incident scoping; don't read them.

#### L. Logging, monitoring, notifications, and time

- Task log and syslog retention; whether logs go to a remote syslog server.
- Notification targets and matchers: do backup failures, fencing, and update notices reach someone?
- Authentication logs (`pvedaemon`/`pveproxy` entries in the journal): failed logins, logins from
  unexpected addresses.
- NTP (chrony on recent releases; verify): correct time on every node (TFA and cluster need it).
- Subscription and update notifications, if an enterprise subscription is in use.

#### M. Hardware, BMC, and physical

- **Ask the user** (don't test): does the server have a BMC (iDRAC, iLO, IPMI)? Is it on a dedicated
  management network, not reachable from guests, users, or the internet? Have default credentials been
  changed? Is IPMI-over-LAN disabled if unused? Is BMC firmware current? Who holds BMC accounts?
- From the inventory only: whether a BMC web UI or UDP 623 answers from non-management segments.
- Physical access to the server, USB ports, and boot order; Secure Boot state if relevant.
- UPS and safe shutdown of guests; what stops on the network if this host goes down (DNS, DHCP, firewall).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

The hypervisor sits under everything on it, so list what depends on the setting before recommending:

- **Critical guests:** the firewall, DNS, DHCP, VPN, NAS, identity, and the agent's own machine, if any runs
  here. A host reboot or bridge change stops them.
- **Management path:** how the user (and the agent) reaches the UI and SSH today, including through a
  virtualized firewall or VPN on this same host.
- **Out-of-band access:** physical console or BMC, tested and reachable without this host's guests.
- **Integrations and tokens:** monitoring, automation, backup tools, and Terraform or similar using users
  and tokens that a change would affect.
- **Cluster:** changes to ACLs, realms, firewall, `datacenter.cfg`, and storage apply to every node; quorum
  loss blocks writes to `/etc/pve`.
- **Backups and storage:** jobs, retention, and the backup server that depend on storage credentials.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Proxmox VE 8.x or older | Plan an upgrade to the current major release, following the vendor upgrade guide and its checker. | Major change; full backups first, a maintenance window, and a tested rollback. Interface names and privileges may change. |
| Pending updates | Apply updates from the configured repository; reboot for kernel fixes. | Guests stop or migrate during the reboot; plan for critical guests. |
| Test repository on a production host | Switch to enterprise or no-subscription. | Packages may need to be realigned at the next update. |
| Enterprise repo without subscription | Disable it and enable no-subscription, or buy a subscription. | None, other than that updates start working. |
| UI or SSH reachable from the internet | Remove the forward or proxy; use a VPN that doesn't run only on this host, or one with an out-of-band fallback. | Remote admin needs a working VPN first; test it. |
| Management reachable from guest or IoT networks | Restrict with the upstream firewall, the PVE firewall `management` IPSet, or `ALLOW_FROM`. | Lockout risk; keep an SSH session and out-of-band access ready. |
| No TFA on admin users | Enroll TOTP or WebAuthn for each admin, including `root@pam`; store recovery keys off the host. | Admins need an authenticator; scripts using passwords need tokens instead. |
| `root@pam` used daily | Create named admin users (in `pve` or an external realm) with TFA; keep `root@pam` for break-glass. | Some operations still need `root@pam`; note which. |
| Over-broad ACLs | Replace `Administrator` on `/` with scoped roles on pools or paths. | Delegated users lose access outside their scope. |
| Tokens without privilege separation | Recreate as privilege-separated tokens with only the needed ACLs and an expiry. | The integration needs its new token secret; old one revoked. |
| Datacenter firewall off, no upstream control | Build a `management` IPSet, add node rules, then enable the datacenter firewall. | High lockout risk; C2 with a tested fallback. |
| Host address on an untrusted or WAN bridge | Remove the host address from that bridge. | Anything using that address to reach the host breaks. |
| Privileged containers | Recreate as unprivileged (backup and restore into a new unprivileged container). | File ownership changes; some workloads need adjustment. |
| Raw `lxc.*` overrides, nesting, or host bind mounts not needed | Remove them. | The container's workload may stop working. |
| No guest firewall or `ipfilter` on untrusted guests | Enable the guest and NIC firewall with `ipfilter`. | The guest loses traffic not explicitly allowed. |
| Insecure migration type | Use `secure`. | Somewhat slower migrations. |
| No backup jobs | Create jobs for all guests to separate storage, with retention and notifications. | Storage space; snapshot mode briefly affects guest IO. |
| Backups only on the same host | Add a separate Proxmox Backup Server or remote storage, and an off-site copy. | New hardware or storage. |
| Encrypted backups, key only on the host | Export the key (paper key or password manager) and store it off the host. | The exported key must be protected; anyone with it can read backups. |
| Host can delete all backups | Separate backup server admin, limit the host's account to backup without prune where workable, add a sync or offline copy. | Retention must then be managed on the backup server. |
| No restore test | Schedule a test restore of a representative guest to an isolated network. | Temporary storage and a few minutes of work. |
| Unknown custom scripts or units | Document or remove each one. | Whatever it did stops. |
| Extra services on the host | Move them into a guest. | Brief service outage while moving. |
| Corosync on a shared network | Move to a dedicated network with a redundant link. | Corosync changes risk quorum loss; specialist-level C2. |
| BMC reachable from user networks or default credentials | The user moves it to a management network, changes credentials, updates firmware, disables unused IPMI-over-LAN. | Done by the user in the BMC; risk of losing remote console if misconfigured. |

Changing the UI port or hiding the login page is supplementary only. Never recommend it as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet-exposed management, end-of-life
release, no backups) → high-priority hardening (TFA, ACLs, tokens, firewall) → routine maintenance →
optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Proxmox VE specifics:

- **Before any change:** confirm a recent backup of every critical guest exists and a copy of the host's
  configuration (at least `/etc/pve` content and `/etc/network/interfaces`, stored securely because they
  contain secrets). Confirm out-of-band access (physical console or BMC remote console) works.
- **Use the web UI, API, or documented CLI.** Don't hand-edit files under `/etc/pve` unless the vendor
  documentation says that's the method, and never while the cluster is not quorate.
- **Keep a way back in.** Keep one SSH session and one UI session open while changing firewall, SSH, realm,
  TFA, or ACL settings; test from a second session before closing the first. Keep `root@pam` with a known
  password as break-glass.
- **Firewall:** the vendor advises opening an SSH session before enabling the firewall. Build the
  `management` IPSet and node rules first, check `pve-firewall status`, enable at datacenter level, and test
  the UI and SSH from a management host and corosync between nodes.
- **ACL and token changes:** add the new scoped grant or token, update the integration, test it, then
  remove the old grant or token as a separate step.
- **Updates:** use `apt update` and `apt dist-upgrade` (or the UI's Updates panel), never `apt upgrade`
  alone (the vendor documents `dist-upgrade` / `full-upgrade` for Proxmox VE). In clusters, update one node
  at a time and migrate or shut down its guests first. Major upgrades follow the vendor's upgrade guide and
  its checker script (verify its name for the target release); treat them as their own project.
- **Reboots:** C2. Plan around critical guests and check start-on-boot order for firewall, DNS, and storage
  guests.
- **Container conversions** (privileged to unprivileged): via backup and restore into a new container,
  keeping the original until the new one is verified.
- **BMC changes** are made by the user in the BMC interface; the agent gives guidance only.

After each change, follow the core "after a change" steps: re-read the setting, check UI and SSH access,
cluster quorum (`pvecm status`), that critical guests are running, that backups still run, and record before
and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Destroying guests, deleting disks, snapshots, or backups as remediation.
- Storage operations: ZFS pool, LVM, Ceph, or RAID changes, `pvesm free`, disk wipes or repairs.
- Cluster membership and quorum changes: `pvecm add`, `pvecm delnode`, `pvecm expected`, editing
  `corosync.conf`, changing corosync links.
- Hand-editing `/etc/pve/priv/` files or the cluster database.
- Reinstalling a node or the whole cluster as a security fix while it still runs production guests.
- Testing BMC or IPMI credentials, trying defaults, or running exploit or brute-force tools against any
  component.
- Running `qm guest exec` or `qm guest passwd` inside a guest that isn't in scope.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the Proxmox VE-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### PVE-001: No backup jobs configured, and the firewall VM is on this host

**Confidence:** Confirmed
**Priority:** P1. Every guest, including the site's virtualized firewall and file server, has no recovery
point; one disk failure, ransomware event, or host compromise loses them all.
**State:** Open
**Component:** Datacenter → Backup, Proxmox VE 9.x, single host `<pve-host>`
**Evidence:** Observed 2026-01-16: `/etc/pve/jobs.cfg` contains no `vzdump` entries; Datacenter → Backup
lists no jobs. `pvesm status` shows only `local` and `local-lvm` on the same pair of disks. The user
confirms no backups are made outside Proxmox. `qm list` shows 6 VMs, including `<firewall-vm>`.
**Expected secure state:** every guest covered by a scheduled backup job to storage separate from the
host, with retention, notifications, and a tested restore (Proxmox VE admin guide, Backup and Restore).
**Exposure and prerequisites:** any hardware failure, accidental deletion, or attacker with host access.
**Dependencies / blast radius:** creating a job adds IO during the backup window; snapshot mode briefly
slows guests. The firewall VM routes all traffic, so its backup should run outside working hours.
**Recommended remediation:** add a Proxmox Backup Server or NFS share on a separate system at
`192.0.2.20`, add it as storage, create a nightly job for all guests with `keep-daily` and `keep-weekly`
retention and failure notifications, then test-restore one guest to an isolated bridge.
**Operation class:** C1 to add storage and a job; the first run is C2 for the firewall VM (brief IO impact).
**Approval required:** Yes.
**Verification:** the job appears in `jobs.cfg`; the first run's task log shows success for every guest;
backups are listed on the new storage; the test restore boots.
**Rollback:** disable or delete the job; remove the storage entry (backups on the remote side are kept).

---

## Version history

- **1.0** (2026-10-30): Initial version.
