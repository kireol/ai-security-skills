---
name: opnsense
description: >-
  Security assessment, hardening, remediation, and incident response for OPNsense firewalls (community and
  business editions, on hardware or virtualized). Use when auditing an OPNsense firewall, reviewing its
  firewall and NAT rules, admin access, VPNs (WireGuard, OpenVPN, IPsec), DNS/DHCP services, plugins,
  backups, or logging, or when an OPNsense firewall may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "OPNsense 26.x community and business editions (verify the live version; menus change between series)"
  audience: "home, work, homelab"
  finding_prefix: "OPN"
  modes: "discover, recommend, remediate, respond"
---

# OPNsense Security

Act as a careful, evidence-driven network security engineer. The firewall is the boundary for everything
behind it: a weakness here exposes every device on the network, and a bad change here can cut off the
whole site, including the agent's own access. Identify, explain, prioritize, remediate (only when
authorized), and verify weaknesses in the firewall itself and in the policy it enforces.

## How to use this skill

This skill holds only OPNsense-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

OPNsense-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

## OPNsense-specific principles

- **Every firewall change is at least C1, and most are C2.** Rule, NAT, interface, VPN, DNS, and DHCP
  changes take effect for the whole network when applied. Treat anything that could affect the
  management path or internet connectivity as **C2**.
- **The configuration export is a secret.** `config.xml` and backup exports contain password hashes, API
  keys, VPN private keys, certificate private keys, and service credentials. Never print, paste, or upload
  one whole. Read only the sections you need and redact them.
- **Read the loaded ruleset, not just the GUI.** The GUI shows configured rules; the packet filter also
  contains automatic rules (anti-lockout, VPN, DHCP, NAT-generated rules). Where shell access exists,
  `pfctl` output is the ground truth for what is actually enforced.
- **OPNsense is not generic FreeBSD.** Configuration is generated from `config.xml` by the system. Edits
  to generated files under `/etc` or `/usr/local/etc` are overwritten and are not a supported way to make
  changes. Use the GUI or the documented API.
- **Follow vendor defaults where the vendor recommends them.** For example, OPNsense recommends leaving
  the web GUI and SSH listening on all interfaces and controlling access with firewall rules, because
  binding to specific interfaces breaks on dynamic or VPN interfaces and can lock you out.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Community edition** | Version without a business-edition marker; community release series (two major series per year). | Updates generally go only to the current series; check that the installed series still receives them. |
| **Business edition** | Business-edition version numbering and license. | Slower, more conservative release train with independent security testing; check the edition's own release notes. |
| **Physical appliance or bare metal** | Physical NICs; vendor hardware or a generic PC. | Physical console access is part of the trust boundary. |
| **Virtualized** (any hypervisor) | Virtual NICs, hypervisor guest tools; the user confirms. | The **hypervisor is part of the firewall's trust boundary**: anyone with hypervisor admin access controls the firewall and can bypass it. Check whether the WAN is a passed-through NIC or a bridge; if it's a bridge, make sure the hypervisor host itself has no address on the WAN bridge. VM snapshots are a useful pre-change rollback and evidence tool. |
| **Behind another router** (double NAT) | WAN address is in a private range. | Real internet exposure depends on the upstream router too: check its port forwards, DMZ/"exposed host" setting, and UPnP. If the upstream router forwards everything to OPNsense, OPNsense's WAN rules are the only boundary. |
| **High-availability pair** (CARP) | CARP virtual IPs; configuration sync settings. | Configuration sync uses privileged credentials; changes replicate to the peer. Assess both nodes. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Usually the LAN's default gateway, and often also its DNS server and DHCP server.
- Web GUI on HTTPS (port 443 by default, with an HTTP redirect on port 80) whose login page is titled
  OPNsense; a self-signed certificate on a fresh install.
- SSH (port 22) with a FreeBSD OpenSSH banner, if enabled.
- A MAC address vendor (OUI) of the official appliance maker on vendor hardware; generic NIC or hypervisor
  vendors otherwise.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer the web GUI, the documented REST API, or user-run checks. For API access, ask the user to create a
dedicated user with only the privileges needed for reading, and remember that some privileges are broader
than they look (domain B). If shell access is available (SSH, or console option 8), these are *candidate*
read-only commands, **not yet verified** on every version. Check each exists first.

```sh
opnsense-version                  # OPNsense version and edition
freebsd-version -ku               # kernel and userland
pkg info -x '^os-'                # installed plugins
pkg audit -F                      # same check as "Run an Audit": installed packages vs. FreeBSD VuXML
sockstat -4 -6 -l                 # listening services, IPv4 and IPv6
pfctl -s rules                    # the ruleset actually loaded, including automatic rules
pfctl -s nat                      # NAT and port-forward rules actually loaded
ifconfig -a; netstat -rn          # interfaces, addresses, routes
wg show                           # WireGuard peers, endpoints, last handshake (no private keys)
ls -l /conf/backup/               # configuration history files (names and dates only)
```

- **Never** run `wg showconf` (prints private keys), `cat /conf/config.xml` (whole file with secrets),
  `pfctl -d` (disables the firewall), or `pfctl -F` (flushes rules). The last two are C3, not R.
- `pkg audit -F` downloads the vulnerability database; it doesn't change configuration.
- Read specific `config.xml` sections only when needed, and redact secrets before showing them.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, firmware, and plugins

- Version, edition (community or business), series, and whether that series still receives updates.
- System → Firmware: pending updates, and the result of **Run an Audit** (security audit against FreeBSD
  VuXML). Validate high-severity audit hits per core triage; the audit can flag issues that don't apply to
  the shipped build. Also check OPNsense's GitHub security advisories and the release notes.
- Installed plugins: official, community, or from a **third-party repository**. Third-party repositories
  add supply-chain risk and can interfere with upgrades.
- Plugins installed but unused.
- Deployment variant (see above).

#### B. Administration and identity

- Who administers it: is `root` used for daily administration, or are there named admin accounts?
- Two-factor authentication on the web GUI (an authentication server of type local + time-based one-time
  password, selected under System → Settings → Administration → Authentication).
- Group privileges. Treat these as full-admin equivalent and confirm only fully trusted admins hold them:
  **XMLRPC Library** (remote sync and automation), **System: Configuration: Backups** (exports contain all
  secrets), user and group management, and **port forward management** (a user who can add port forwards
  can open paths into the network).
- Access to legacy pages (URLs ending in `.php`), which have fewer safeguards than newer pages; restrict
  them to fully trusted admins.
- API keys: which users have them, their age, and whether each is still needed. An API key has its user's
  full privileges.
- Remote authentication servers (LDAP/RADIUS): which groups map to admin.
- SSH authorized keys for every user with shell access; which users have a login shell; `sudo` settings.
- **Strict security** (System → Settings → Administration, deployment settings): whether the web GUI is
  prevented from running as root. Note some legacy components may not be compatible.
- Console: whether the console menu is password-protected (unprotected means anyone with physical or
  hypervisor-console access has full control).

#### C. Management-plane exposure

- Can the web GUI or SSH be reached from the WAN? Check WAN rules, port forwards that target the firewall
  itself, and the upstream router (double NAT). Test from outside only with explicit authorization.
- Which internal segments (guest, IoT, cameras, VPN) can reach the management ports. Ideally only a
  management network or specific admin hosts can.
- Web GUI: HTTPS only, certificate (self-signed or trusted), HTTP Strict Transport Security, session
  timeout, and that the **DNS rebind check** and **HTTP_REFERER enforcement** have not been disabled.
- SSH: enabled only if needed; **Permit Root Login** off; **Permit password login** off (keys only) where
  workable; reasonable algorithms.
- Login protection (brute-force blocking) in place for GUI and SSH.
- Listen-interface settings: if set to specific interfaces, note the vendor's warnings (they break on VPN
  and dynamic interfaces); access should be controlled with firewall rules instead.
- The anti-lockout rule: present on the LAN by default. Know it exists before changing any LAN rules.

#### D. Firewall rules and NAT

- **Inbound (WAN):** every pass rule and port forward, what it reaches, whether its source is restricted,
  and whether it is still needed. IPv4 and IPv6 separately; IPv6 pass rules on WAN reach hosts directly
  without NAT.
- One-to-one NAT and any rule that exposes an entire host.
- **Internal:** broad "any to any" pass rules between segments; rules that let IoT, cameras, or guests
  reach servers and admin interfaces; disabled rules left in place; rule order.
- **Egress:** whether devices that don't need the internet are blocked from it, and whether any segment
  can reach the internet on ports it shouldn't (for example, direct outbound DNS bypassing filtering).
- Aliases: URL-table and DNS-based aliases (their contents come from outside and change), stale entries.
- Floating rules and their effect across interfaces.
- WAN interface options: "block private networks" and "block bogon networks" (evaluate against the
  deployment; behind another router, the upstream may legitimately be a private address).
- Rules GUI state: since 26.7, rules are managed in the new rules GUI; the old pages are in the
  `os-firewall-legacy` plugin, and unmigrated rules keep working. Check both places for rules.
- **UPnP/NAT-PMP** (`os-upnp` plugin): enabled? If so, which internal hosts may create mappings, and what
  mappings currently exist.
- Compare the GUI with `pfctl -s rules` / `pfctl -s nat` where available.

#### E. VPN and remote access

- **WireGuard:** each peer is a credential. Peers nobody recognizes, peers with no recent handshake,
  allowed-IP ranges broader than needed, and which interfaces/rules apply to WireGuard traffic (a VPN
  interface with an "allow any" rule gives every peer the whole LAN).
- **OpenVPN:** certificate-based authentication plus a second factor where possible; TLS authentication or
  encryption key in use; revoked certificates on a CRL; cipher settings.
- **IPsec:** pre-shared key strength versus certificates; phase settings; which networks are reachable.
- **Site-to-site links:** what each remote site can reach. A compromised remote site should not get full
  access to this network.
- Other remote access: dynamic DNS clients and their credentials, remote management or monitoring agents.

#### F. DNS and DHCP services

- **Unbound:** access control lists (an Unbound listening on WAN without ACLs is an open resolver),
  DNSSEC, forwarding (and whether over TLS), DNS rebinding protection, blocklists, and **host overrides**
  (a malicious override silently redirects a name).
- **Dnsmasq** (DNS and/or DHCP): which interfaces it serves, and any DNS settings it exposes.
- **DHCP backend:** dnsmasq is the default (DHCPv4, DHCPv6, and router advertisements on new installs), and
  Kea is available. The ISC DHCP server moved out of core into a plugin in 26.1, and the vendor documents
  it as **end-of-life with no further updates or security patches**. If ISC DHCP is still in use, that's
  an end-of-life finding (core triage); plan a migration. There is no automatic migration; static
  mappings can be moved in bulk. dnsmasq doesn't do DHCPv6 prefix delegation, so check that first if
  it's needed.
- DHCP options pushed to clients (DNS server, gateway): unexpected values redirect every client.
- Static mappings: unrecognized devices.

#### G. Other services and plugins

- Every listening service (`sockstat`), mapped to the feature that owns it, on which interfaces.
- Captive portal: it's internet- or guest-facing by design; keep it current.
- Intrusion detection/prevention (Suricata), CrowdSec, or similar: enabled, rules updating, alerts reviewed.
- Reverse-proxy plugins (HAProxy, Caddy, nginx): every published backend is an exposure, assessed like a
  port forward.
- SNMP (community strings, which interfaces), NTP serving, web proxy, dynamic DNS credentials.

#### H. Configuration backups and change tracking

- Configuration history (System → Configuration → History): enabled, how far back, and who made recent
  changes.
- Off-box backups (cloud, git, or sftp backup plugins, or manual exports): where they go, how often,
  whether they're **encrypted**, and who can read them (they contain all secrets).
- Whether a restore has ever been tested, and whether console access works (the vendor advises testing
  the console after installation).
- High availability: sync credentials and which settings sync.

#### I. Logging, monitoring, and time

- Remote logging (System → Settings → Logging → Remote): enabled, which applications, and transport (TLS
  preferred).
- Logging on important rules (WAN passes, management access, VPN).
- Log retention, and whether `/var` is a RAM disk (logs lost on reboot).
- Web GUI access log, monitoring/alerting (for example Monit), and notifications for firmware updates.
- NTP: correct time for correlation.

#### J. Physical, hypervisor, and availability

- Physical and console access; serial console settings.
- For virtualized firewalls: hypervisor admin access, WAN NIC passthrough or bridge, snapshots, and
  whether the hypervisor's own management interface is reachable from untrusted segments.
- Power protection, and what happens to the network if the firewall fails (DNS, DHCP, VPN all stop).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

The firewall sits under everything, so list what depends on the setting before recommending a change:

- **Management access:** which rule or path the user (and the agent) currently uses to reach the GUI or
  SSH, including the anti-lockout rule.
- **Port forwards and reverse-proxy routes:** which services and users rely on each.
- **VPN peers and sites:** who connects, and what they need to reach.
- **DNS and DHCP:** every client depends on them; a mistake takes the whole network offline.
- **Devices with fixed addresses or reservations** that rules and aliases match on (cameras, servers).
- **Upstream router** configuration in a double-NAT setup.
- **HA peer:** synced settings change both firewalls.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| GUI/SSH reachable from WAN | Remove the WAN rule or port forward; use the VPN for remote admin. | Remote admin needs a working VPN first; test it before removing. |
| No 2FA on admin login | Add a local + TOTP authentication server and enroll each admin. | Admins need an authenticator app; keep a tested break-glass path (console). |
| `root` used daily | Create named admin accounts; keep `root` for break-glass with a strong password. | Scripts and API integrations using `root` must move to their own accounts. |
| Over-broad privileges | Remove XMLRPC, backup, user-management, and port-forward privileges from non-admin groups. | Delegated users lose those functions. |
| SSH | Disable if unused; otherwise keys only, no root login, restricted by firewall rules. | Automation using SSH passwords breaks. |
| Strict security off | Enable it. | Some legacy pages or plugins may not work; disabling it again needs console access. |
| Management reachable from IoT/guest | Add block rules for the firewall's management ports from those segments. | Rule order matters; test from each segment. |
| Unneeded port forwards | Remove, or restrict the source. | The service becomes unreachable from outside. |
| Flat network | Separate IoT/cameras/guests onto their own VLANs with restrictive rules. | Large C2 project; plan per device group. |
| No egress control for IoT | Block internet access for devices that don't need it (allow NTP if needed). | Cloud features and firmware updates for those devices stop. |
| UPnP enabled | Disable, or restrict to specific hosts and ports. | Consoles and some apps lose automatic port mapping. |
| Over-broad VPN rules | Restrict each VPN or peer to the networks it needs. | Remote users lose access to anything not listed. |
| Stale VPN peers or certificates | Remove peers; revoke certificates via CRL. | Anyone still using them is cut off. |
| ISC DHCP still in use (end-of-life) | Migrate to dnsmasq or Kea. | Manual migration; brief DHCP interruption; check static mappings and any DHCPv6 prefix delegation. |
| Unbound open on WAN | Restrict ACLs to internal networks. | None for legitimate clients. |
| Third-party plugin repositories | Remove those not needed. | Plugins from them stop updating or must be removed. |
| No encrypted off-box backup | Configure an encrypted backup to a separate system. | The destination must be protected; it holds every secret. |
| No remote logging | Send logs to a separate syslog server (TLS if possible). | Needs a log receiver. |
| Outdated firmware | Update within the current series; plan major upgrades with a backup or snapshot. | Reboot; brief outage. |

Changing ports, hiding the login page, and geoblocking are supplementary only. Never recommend them as
the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet-exposed management, critical
updates) → high-priority hardening → routine maintenance → optional defense in depth. Then ask for
approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. OPNsense specifics:

- **Before any change:** download an encrypted configuration backup and store it off the firewall. On a
  virtualized firewall, also take a VM snapshot. Note the current configuration-history entry so you can
  revert to it.
- **Use the GUI or documented API.** Don't hand-edit `config.xml` or generated files.
- **Keep a way back in.** Keep one session open while applying, and test new rules from a second session
  or client before closing the first. Confirm console access (physical, serial, or hypervisor) works
  before changing anything that touches the management path.
- **Never disable the anti-lockout rule** until an explicit management allow rule exists and has been
  tested.
- **Rule changes:** add the new rule, apply, test, then remove the old rule as a separate step. Mind rule
  order. Don't make interface, rule, and NAT changes in one apply.
- **Updates:** minor updates within the current series are C2 (reboot). Major-series upgrades also need
  release-note review, a check for third-party repositories or plugins that might interfere, and a
  backup or snapshot.
- **DHCP migration:** move one interface at a time and confirm leases and static mappings work.
- **VPN changes:** confirm the user isn't connected through the VPN being changed, or has another path.
- **If you lose access:** use the console to revert to an earlier configuration from history or a backup
  (verify the exact console option on the installed version), or restore the VM snapshot.

After each change, follow the core "after a change" steps: re-read the setting, compare `pfctl` output
where available, check the management path, internet access, DNS, DHCP, and VPNs, and record before and
after.

### Hard stops (refer to a specialist or do manually; never automate)

- `pfctl -d` (disable the firewall) or `pfctl -F` (flush rules) as a troubleshooting step.
- Factory reset, reinstall, or disk/ZFS operations as security remediation.
- Hand-editing `config.xml` and reloading it.
- Deleting configuration history or backups.
- Changing the listen interfaces of the GUI or SSH (vendor-documented lockout risk) without console
  access confirmed and the user present.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the OPNsense-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### OPN-001: Web GUI reachable from the internet through a port forward

**Confidence:** Confirmed
**Priority:** P1. The firewall's own admin login is exposed to the internet, so any authentication
weakness or unpatched GUI vulnerability gives control of the whole network.
**State:** Open
**Component:** NAT port forward on WAN, OPNsense 26.x
**Evidence:** Observed 2026-01-16: a WAN port forward from TCP 8443 to the firewall's LAN address
`192.0.2.1` port 443, source "any", with its associated pass rule. `pfctl -s nat` shows the same
redirect. With approval, an external check from `198.51.100.7` loaded the OPNsense login page.
**Expected secure state:** management reachable only from trusted internal networks or through the VPN
(OPNsense security documentation, deployment considerations).
**Exposure and prerequisites:** anyone on the internet; requires valid credentials or a GUI vulnerability.
No 2FA configured.
**Dependencies / blast radius:** the user manages the firewall remotely through this forward; WireGuard
is configured but the user hasn't used it for admin.
**Recommended remediation:** confirm admin access over WireGuard works, then remove the port forward and
its rule. Separately, add TOTP 2FA for admin accounts.
**Operation class:** C2 (removes the user's current remote-admin path).
**Approval required:** Yes.
**Verification:** external check no longer reaches the login page; admin over WireGuard works; `pfctl -s
nat` no longer shows the redirect.
**Rollback:** re-enable the forward from configuration history (not recommended; restrict its source
instead if remote access breaks).

---

## Version history

- **1.0** (2026-10-30): Initial version.
