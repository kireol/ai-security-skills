---
name: unraid
description: >-
  Security assessment, hardening, remediation, and incident response for Unraid OS servers, including
  Unraid running as a virtual machine. Use when auditing an Unraid server, reviewing its WebGUI and root
  account, management access (SSH, Telnet, SSL/TLS), Unraid Connect and remote access, user shares and
  their SMB/NFS export security, Community Applications plugins, Docker and VM templates, the boot device
  (flash drive) and its backups, or when an Unraid server may have been compromised or hit by ransomware.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Unraid OS 7.x (7.3.x is the current stable line; 7.2.x still receives some security releases; verify the live version and release notes)"
  audience: "home, homelab, work"
  finding_prefix: "UNR"
  modes: "discover, recommend, remediate, respond"
---

# Unraid Security

Act as a careful, evidence-driven Unraid security engineer. Identify, explain, prioritize, remediate (only
when authorized), and verify weaknesses that could expose the server, its shares, its containers and VMs,
or its data to compromise, ransomware, unauthorized access, service disruption, or data loss. Unraid is
often the one box in a homelab that holds all the data, runs most of the services, and has a single root
account that controls everything, so small misconfigurations have a large blast radius.

## How to use this skill

This skill holds only Unraid-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Unraid-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation and
advisories are in [references.md](references.md).

Related skills: containers on the server are assessed in depth with
[Docker](../../containers/docker/SKILL.md); ZFS pools with [ZFS and Ceph](../zfs-and-ceph/SKILL.md);
backup design and independence with [backup tools](../backup-tools/SKILL.md); remote access through
tunnels with [tunnels](../../edge/tunnels/SKILL.md); a reverse proxy in front of the WebGUI or apps with
[web servers](../../web/web-servers/SKILL.md); a hypervisor hosting Unraid with
[Proxmox VE](../../virtualization/proxmox-ve/SKILL.md). For a general Linux comparison, see
[Linux](../../operating-systems/linux/SKILL.md), but read the principles below first.

## Unraid-specific principles

- **Unraid is an appliance, not a general Linux distribution.** The root filesystem is unpacked into RAM at
  every boot. Changes to `/etc`, `/usr`, or `/root` are lost on reboot unless something on the boot device
  re-applies them. Configuration lives on the boot device (traditionally a USB flash drive mounted at
  `/boot`; Unraid 7.3 also supports internal boot devices). There is no supported package manager for the
  base OS; don't recommend `apt`, `dnf`, or editing system files as a fix.
- **One administrator: root.** The WebGUI, SSH, and Telnet all use `root`. Share users can reach shares over
  SMB/NFS/FTP but can't log in to the WebGUI or a shell (vendor-documented). Root can't use shares over SMB
  or NFS. There's no per-admin separation or built-in WebGUI MFA on the server itself (verify on the live
  version), so the root password and the network paths to the WebGUI carry all the weight.
- **Persistence lives on the boot device.** Anything that runs at boot (the `go` script, plugins, extra
  packages, user scripts, container and VM templates, SSH keys) is stored there. The boot device is
  therefore both the most important backup target and the most important place to look for tampering.
- **Plugins run as root.** A plugin (`.plg`) downloads and installs code with full control of the server at
  every boot. Community Applications (CA) is a catalog of third-party plugins and Docker templates, not a
  vetted store. Treat each install as a supply-chain decision.
- **Parity is not a backup.** Parity protects against disk failure, not deletion, encryption, or
  corruption written by a user, container, or attacker. Storage repair is a separate discipline; see the
  hard stops under Remediate.
- **The vendor publishes security fixes mainly in release notes** (and occasional blog or forum
  announcements), not a dedicated advisory feed. Read the release notes for the installed and current
  versions every time (core: triage).

## Deployment variants

Identify the variant in Discover. It changes which rules apply.

| Variant | How to recognize it | What changes |
|---|---|---|
| **Bare metal, USB flash boot** | A USB flash drive mounted at `/boot`; the license is tied to that drive. | All guidance applies as written. The flash drive is a single point of failure and an easy physical-theft target: anyone holding it can read the configuration and reset the root password (vendor-documented). |
| **Bare metal, internal boot** (Unraid 7.3+) | Boot pool on an internal SSD/NVMe; TPM-based licensing may be in use. | Same, but boot-device backup and restore follow the internal-boot procedure, and rollback to older releases may be blocked after enabling internal boot or TPM licensing (vendor release notes). Check the BIOS boot order after boot-pool device changes. |
| **Virtualized Unraid** (inside Proxmox VE or another hypervisor) | Virtual NICs, a passed-through USB flash drive or controller, hypervisor tools; the user confirms. | The **hypervisor is part of the trust boundary**: anyone with hypervisor admin access controls the server and its disks. Passed-through disks and controllers are usually excluded from VM snapshots and backups. Disk health may need reading on the hypervisor. See [Proxmox VE](../../virtualization/proxmox-ve/SKILL.md). |
| **Unraid Connect enrolled** | Signed in to an Unraid account; the Unraid API and Connect settings appear under Management Access. | Adds a cloud account to the trust boundary (its password and 2FA), optional cloud flash backup, and optional Remote Access that publishes the WebGUI to the internet. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- WebGUI on HTTP port 80 and HTTPS port 443 (vendor defaults, set under Settings → Management Access),
  showing an Unraid-branded login page with the server name. The default server name is `Tower` and the
  default local TLD is `local`, so `tower.local` is common on fresh installs.
- With **Use SSL/TLS = Strict**, HTTP requests redirect to a hostname of the form
  `<lan-ip>.<hash>.myunraid.net` (the vendor's documented format; the address may be written with
  dashes), and the certificate is a publicly trusted `myunraid.net`
  certificate. With **Yes**, a self-signed certificate naming the server.
- SSH on TCP 22 when enabled, Telnet on TCP 23 when enabled, SMB on TCP 445, NFS on TCP/UDP 111 and 2049
  when enabled, and VM consoles (VNC, listed by the vendor as `57xx` ports) when VMs run. The built-in
  WireGuard VPN, if configured, listens on a UDP port (commonly 51820; verify in the tunnel settings).
- mDNS/DNS-SD announcements (Avahi) for the server name, SMB, and similar services; SMB NetBIOS or WS-Discovery
  names matching the server name. Verify which services the live version announces.
- **MAC vendors:** Lime Technology doesn't make hardware, so the host shows its NIC maker's OUI (or a
  hypervisor's for virtualized Unraid). VMs created by Unraid's libvirt default to the `52:54:00` prefix
  (QEMU/KVM locally administered range), and containers on a custom macvlan/ipvlan network may show Docker-
  generated or randomized MACs. Several such addresses near one host suggest an Unraid or other KVM host.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands (SSH or WebGUI terminal, if available)

Prefer the WebGUI, **Tools → Diagnostics** (a zip of logs and configuration, anonymized by default), and
documented APIs. If a shell is available, these are *candidate* read-only commands, **not yet verified**
on every release. Check each exists first, and never print secrets to the transcript.

```sh
cat /etc/unraid-version                 # Unraid OS version (not yet verified on every release)
uname -a                                # kernel
df -h; mount                            # array disks, pools, and /boot
ls -la /boot/config/                    # configuration files on the boot device
cat /boot/config/go                     # boot-time script: review every line
ls -la /boot/config/plugins/            # installed plugins (.plg) and their folders
ls -la /boot/extra/ /boot/packages/ 2>&1    # extra packages installed at boot, if present
cat /boot/config/ident.cfg              # server name, management ports, SSH/Telnet/SSL settings (do not print secrets)
ls /boot/config/shares/                 # one .cfg per user share (export and security settings)
docker ps -a --format '{{.Names}} {{.Image}} {{.Ports}}'
virsh list --all                        # VMs
ss -tulpn                               # listening ports and owning processes
```

- Key names inside `.cfg` files vary by release; read them, don't assume them. Treat values that look like
  credentials (SMTP, VPN keys, API keys) as secrets: record that they exist, never their values.
- Don't run array, parity, or disk commands (for example the md driver's control tool, `xfs_repair`,
  `btrfs check`, `zpool` changes) during an assessment. Read state from the WebGUI **Main** page and
  diagnostics.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, version, and lifecycle

- Unraid OS version and branch (stable vs. next/beta/RC), and how far behind the current stable release it
  is. Read the release notes for every version between installed and current for security fixes; recent
  releases include security-only maintenance builds for the previous minor line, with the vendor still
  recommending the newest stable line.
- Check public vulnerability sources for Unraid itself (NVD, ZDI) and for the bundled components the
  release notes list (kernel, PHP, nginx, Docker, Samba). Validate each against the installed version
  (core: triage). Unraid has had unauthenticated WebGUI flaws; exposure of the WebGUI multiplies their
  impact.
- Update notification settings (Settings → Notifications) and whether updates are checked regularly.
- Deployment variant and, for virtualized Unraid, the hypervisor's own status.

#### B. Root account and WebGUI administration

- Is a root password set? Unraid ships without one; an unset or trivial root password is a critical
  finding on any network with untrusted devices.
- Password strength (the OS doesn't enforce complexity), uniqueness, and storage in a password manager.
- WebGUI session handling: who has browsers logged in, and whether the WebGUI is used from shared or
  untrusted machines.
- Unraid account (Connect) linked to the server: whether 2FA is enabled on that account, who holds it, and
  its recovery options. Check the account provider's current 2FA options rather than assuming.
- Unraid API keys and any third-party dashboards, mobile apps, or home-automation integrations that hold
  root-equivalent credentials or API keys: existence, scope, and age only, never values.
- Share users: one per person or service, no shared accounts, unused accounts removed, strong passwords.
  Service accounts used by backup jobs or media players should have read-only access where possible.

#### C. Management access, network exposure, and remote access

- Settings → Management Access: **Use SSL/TLS** (No / Yes / Strict), HTTP and HTTPS ports, local TLD,
  **Use SSH**, **Use TELNET**, and **Use UPnP**. Telnet should be off. HTTP-only management on a network with
  untrusted devices exposes the root password.
- SSH: enabled only if needed; key authentication where possible; root's authorized keys reviewed. Keys
  persist via the boot device, so list where the live version stores them.
- **Unraid Connect Remote Access**: disabled, or Always with Static (manual port forward) or UPnP. Both
  publish the **full WebGUI** to the internet (vendor-documented). The vendor recommends its Tailscale
  integration or a VPN instead. Dynamic/on-demand modes, where available, open and close a port; record
  which mode and version.
- Router side (check the router, not just Unraid): port forwards to 80/443, 22/23, 445, 111/2049, VM
  console ports, container ports, any DMZ host setting (never acceptable for this server), and active
  UPnP/NAT-PMP mappings. Check IPv6 reachability separately.
- Other paths in: the built-in WireGuard VPN (peers, which peers get LAN or server-only access), Tailscale,
  tunnels, and reverse proxies in containers. Is the WebGUI behind any of them with extra authentication?
- Listening ports from `ss`, each mapped to the OS service, a plugin, a container, or a VM.
- DNS rebinding protection on the router and its effect on `myunraid.net` certificates (affects
  availability of Strict mode, not security directly).
- External exposure checks only within an authorized scope (core: tool-use contract).

#### D. Shares, SMB/NFS exports, and file protocols

- For each user share and disk share: **Export** (Yes / Yes (hidden) / No) per protocol and **Security**
  (Public / Secure / Private). Public means anyone on the network can read and write; Secure means anyone can
  read. Sensitive data should be Private.
- **Disk shares** (individual array disks or pools exported directly) bypass user-share settings and are
  often forgotten. They should normally be off.
- The **boot device share** (`flash`, labeled "Boot device" in 7.3+): exported? With what security? It
  contains the server's configuration, so anyone who can write to it can add boot-time code. It should be
  Private or not exported, and exported only while needed.
- SMB settings: minimum protocol, guest access, Enhanced macOS interoperability, NetBIOS, workgroup or
  Active Directory join. Very old clients that force legacy protocol support are a finding to weigh.
- NFS: which shares are exported, the Security mode, and for Private exports the client rule (allowed hosts
  and options such as `root_squash`). An export open to a whole subnet with read/write lets any device there
  rewrite the data; NFS has no user authentication by default.
- FTP: off unless needed; plain FTP sends credentials in cleartext.
- Secrets stored on shares: application configs, databases, `.env` files, SSH keys, password exports. The
  `appdata` share (container data) is especially sensitive and should not be exported, or only Private.

#### E. Community Applications, plugins, and supply chain

- Every installed plugin: name, author, source URL in the `.plg` file, version, last update, whether it's
  still maintained and supported on this Unraid version, and whether it's needed. A plugin installed from
  an arbitrary URL rather than CA is a higher risk.
- Plugin update practice: are plugin updates reviewed before applying? Does any plugin auto-update?
- The CA plugin itself: current, so its repository-transfer protections and deprecation warnings are
  active. CA flags deprecated or incompatible apps; record any that are installed.
- Plugins that add powerful surfaces: user scripts, web terminals, file managers, remote-access or VPN
  plugins, and anything that adds a listening port.
- The `go` script and extra packages installed at boot: every line and file accounted for, owner known.

#### F. Docker containers and templates

Treat each container as an independently exposed workload with a path into the shares. Assess them in
depth with the [Docker skill](../../containers/docker/SKILL.md). Unraid-specific checks:

- Templates (from CA or user-created): **Privileged** toggle, **Extra Parameters** (often where
  `--cap-add`, `--device`, `--pid=host`, or socket mounts hide), and **Post Arguments**. A template from CA is
  someone else's configuration; review it as code.
- Path mappings: containers mapped to `/mnt/user` or `/mnt` (every share), `/boot`, or
  `/var/run/docker.sock` (root-equivalent control of the server).
- Network type: bridge, host, or custom macvlan/ipvlan (`br0`) giving the container its own LAN address.
  Containers with LAN addresses bypass any port-based thinking and should be counted as hosts.
- WebUI links and published ports; admin panels with default credentials or open registration.
- Image sources: maintained publishers, pinned tags or digests for important services, update method
  (manual, CA auto-update plugin, or a watcher container), and rollback.
- Docker storage (`docker.img` or directory) and the `appdata` location, and whether both are backed up.

#### G. Virtual machines

- VMs: OS, purpose, network (bridged onto the LAN or isolated), passed-through devices (GPU, USB,
  controllers), and VNC console settings (password, listen address). VNC ports exposed beyond the LAN are a
  finding.
- VMs with access to the same shares or bridges as the host are part of its blast radius. Assess each guest
  with its own OS skill.

#### H. Boot device, configuration backup, and encryption

- Boot device health and age; a recent local backup (Main → Boot Device → Flash Backup, or the vendor's
  current equivalent) stored off the server; and whether Unraid Connect cloud flash backup is enabled.
- **Connect flash backup is not encrypted in the cloud** (vendor-documented at the time of writing) and
  excludes some secrets; anyone with the Unraid account can download the server's configuration. Decide
  whether that's acceptable, and protect the account accordingly.
- Physical security of the boot device: anyone with it can reset the root password.
- Array and pool encryption (LUKS): which devices are encrypted, how the passphrase or keyfile is supplied at
  start, and whether a keyfile is left on the boot device or in RAM after the array starts. A keyfile stored
  next to the encrypted disks defeats the purpose against theft.

#### I. Data protection and ransomware resilience

- Parity state and last parity check result (read only), plus pool redundancy, as availability facts.
- Backups of shares and `appdata`: tool, destination, schedule, last success, retention, encryption, and
  where keys live (see [backup tools](../backup-tools/SKILL.md)).
- **Independence:** can root on this server (or a container with `/mnt/user` mapped) delete every backup
  copy? At least one copy should be outside the server's administrative boundary, offline or immutable.
- Snapshots on ZFS or Btrfs pools: present, scheduled, and who can delete them (see
  [ZFS and Ceph](../zfs-and-ceph/SKILL.md)).
- Restore testing: when were representative files and container data last restored?

#### J. Monitoring, logging, and scheduled tasks

- Logs live in RAM and are lost on reboot. Is the syslog server configured to send to a remote host, or
  mirrored to the boot device (which wears flash; weigh this)?
- Notifications: agents (email, push) configured for array, disk, update, and plugin events. Notification
  agent credentials are secrets.
- Scheduled tasks: user scripts, plugin schedulers, mover, parity checks, container auto-updates, and cron
  entries added by the `go` script. A root-run script stored on a share others can write to is a privilege-
  escalation path.
- Correct time and NTP.

#### K. Hardware health, physical, and availability

- SMART status, disk errors, and any disabled or emulated disks (record only; see hard stops).
- UPS integration and clean shutdown.
- Physical access to the server and its boot device.
- How management access is regained if SSL Strict, DNS, VPN, or firewall changes fail (local console, the
  vendor's `use_ssl` recovery commands over SSH, IP-based access).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state. On Unraid, common hidden
dependencies are:

- **SMB/NFS clients** (workstations, media players, other servers, backup jobs) using guest or Public
  access. Making a share Private or tightening an NFS rule breaks them until they have credentials.
- **Containers** whose path mappings, PUID/PGID, and permissions assume current share settings. Bulk
  permission tools ("New Permissions" style) can break every app that uses `appdata`.
- **Integrations** (dashboards, mobile apps, home automation, monitoring) that use the root password or an
  API key.
- **Remote users** who rely on Connect Remote Access, a port forward, or a reverse-proxy route.
- **Plugins** that other plugins or containers depend on.
- **Hypervisor** (virtualized Unraid): host networking changes can affect the VM's reachability.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Root password | Set a strong, unique root password; store it in a password manager. | Integrations using the old password break; find them first. |
| WebGUI over HTTP | Set Use SSL/TLS to Yes (self-signed) or Strict (`myunraid.net`). | Strict depends on DNS; plan the `use_ssl` recovery path and keep IP or local access. |
| Telnet | Disable. | None for most users; use SSH or the WebGUI terminal. |
| SSH | Disable if unneeded; otherwise keys only and LAN/VPN only. | Automation using SSH passwords breaks. |
| WebGUI exposed (port forward, DMZ, or Connect Remote Access) | Disable Remote Access and remove forwards; use Tailscale, WireGuard, or another VPN, or an authenticated tunnel. | Remote users need a new path before removal. |
| UPnP | Disable on the router and in Management Access; verify mappings are gone. | Connect UPnP remote access and some apps stop working. |
| Public/Secure shares with sensitive data | Make them Private with named users; keep Public only for non-sensitive, ideally read-only data. | Clients need credentials; Windows allows one credential set per server name. |
| Disk shares, boot device share | Turn off disk shares; boot device share Private or not exported. | Workflows that copy files to the flash share over SMB change. |
| Broad NFS export | Private with a client rule naming specific hosts and appropriate squash. | Plan per client. |
| Plugins | Remove unneeded or unmaintained ones; review updates before applying. | Removing a plugin may remove features or settings; check dependents. |
| Privileged or broadly mapped containers | Remove privilege, socket mounts, and `/mnt/user` mappings; map only needed shares. | Some apps genuinely need a capability or path; test each change. |
| Boot device backup | Keep a current local backup off the server; decide on Connect cloud backup knowingly. | Cloud backup stores configuration unencrypted with the vendor. |
| Encryption keyfile | Don't leave the keyfile on the boot device; supply the passphrase at start or from a separate source. | Unattended array start may no longer be possible. |
| Backups | Add an independent offline or immutable copy of shares and `appdata`; test a restore. | Cost, capacity, and time. |
| Logging | Send syslog to a remote host. | Needs a receiving host. |

Changing the WebGUI port or hiding shares is supplementary only. Never recommend it as the main fix.

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Unraid specifics:

- **Use the WebGUI and vendor-documented procedures.** Don't persist changes by hand-editing files under
  `/boot/config` while the array or services are running, and don't add commands to the `go` script as a
  hardening method unless the user understands and accepts that it becomes boot-time code.
- **Back up the boot device first** (local download, stored off the server) before OS upgrades, plugin
  removals, or management-access changes.
- **Management access:** change one setting at a time and keep a second path open (a second browser
  session, SSH, or local console). Before switching to Strict, confirm the `myunraid.net` name resolves
  and know the `use_ssl` recovery command for the installed version. Changing management ports or SSL
  settings is **C2**.
- **OS updates:** read the release notes (including rollback limits, such as after internal boot, TPM
  licensing, or ZFS feature upgrades), confirm a boot-device backup and a recent data backup, and stop if
  the array has any disabled, emulated, or unmountable device. An update and reboot is **C2**.
- **Plugins:** before removing one, check what depends on it and whether removal deletes its data (then
  **C3**). Update CA and the OS before judging a plugin incompatible.
- **Containers:** back up `appdata` and the template, record the current image tag or digest, and change
  one container at a time. See the [Docker skill](../../containers/docker/SKILL.md).
- **Shares:** prefer adding a named user with the needed access before changing Security from Public to
  Private, and test every client. Never run bulk permission resets on `appdata` or whole shares without
  confirming which containers depend on current ownership.
- **Remote access:** set up and test the replacement path (VPN, Tailscale, tunnel) before disabling Connect
  Remote Access or removing a port forward, then confirm from outside that the old path is closed.

After each change, follow the core "after a change" steps, and re-run the affected Discover checks.

### Hard stops (refer to a specialist; never automate)

If any array disk is disabled or emulated, a disk or pool is unmountable, a parity sync or rebuild is
running, or a pool reports errors, **stop all hardening, plugin changes, and OS upgrades**, preserve
diagnostics, and recommend storage-recovery help (Unraid's support and forum guidance, or a specialist).
Never, as security remediation:

- Accept a prompt to **format** an unmountable disk. Formatting writes an empty filesystem and updates
  parity to match, so parity can no longer recover the old contents.
- Use **New Config**, reassign disks, or start a parity sync or disk rebuild.
- Run filesystem repair (`xfs_repair`, `btrfs check --repair`) or ZFS pool repair, import, or destroy
  operations.
- Run a parity check that writes corrections when disks are suspect.
- Delete pools, shares, or the Docker image as a cleanup step.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the Unraid-specific steps
in [incident-response.md](incident-response.md). Logs on Unraid live in RAM: **don't reboot** before
capturing diagnostics.

---

## Worked example (invented)

### UNR-001: WebGUI published to the internet by Connect Remote Access, with HTTP-only LAN management

**Confidence:** Confirmed
**Priority:** P1. The full WebGUI (root-equivalent control of every share, container, and VM) is reachable
from the internet. Unraid has had unauthenticated WebGUI vulnerabilities, so password strength alone isn't
an adequate control.
**State:** Open
**Component:** Unraid OS 7.x, Settings → Management Access; Unraid Connect Remote Access
**Evidence:** Observed 2026-10-31 in Management Access: Allow Remote Access = Always, forward type UPnP;
Use UPnP = Yes; Use SSL/TLS = No for LAN access. The router's UPnP table (observed) shows a mapping from a
high WAN port to the server at `192.0.2.20` port 443. An authorized external check from `203.0.113.50`
reached the Unraid login page.
**Expected secure state:** Remote Access disabled unless required; remote administration through a VPN or
the vendor's Tailscale integration; HTTPS for LAN management (Unraid Connect remote access and
securing-your-connection documentation).
**Exposure and prerequisites:** anyone on the internet who finds the port; no prior access needed to reach
the login page or any pre-authentication flaw.
**Dependencies / blast radius:** the owner uses the Connect dashboard's Manage link from a phone when away.
A media-server container has its own separate port forward (assessed in DKR-002).
**Recommended remediation:** set up and test WireGuard or Tailscale for remote management; then set Allow
Remote Access to Disabled, set Use UPnP to No, disable UPnP on the router if nothing else needs it, and set
Use SSL/TLS to Yes for LAN access. Alternative: keep Connect dashboard monitoring without Remote Access.
**Operation class:** C2 (remote management path changes; WebGUI restarts on SSL change).
**Approval required:** Yes. Disruptive to remote access.
**Verification:** external check from `203.0.113.50` can't reach the login page; router UPnP table has no
mapping for the server; the WebGUI loads over HTTPS on the LAN; remote management works over the VPN.
**Rollback:** re-enable Remote Access with the captured settings (not recommended); revert Use SSL/TLS to
the captured value via the WebGUI or the vendor's `use_ssl` command.

---

## Version history

- **1.0** (2026-10-31): Initial version.
