---
name: home-routers
description: >-
  Security assessment, hardening, remediation, and incident response for home routers, ISP-supplied
  gateways (cable, DSL, and fiber ONT/router combos), standalone modems, consumer routers (ASUS, TP-Link,
  Netgear, Linksys, and similar), routers running OpenWrt or DD-WRT, and devices in bridge, passthrough, or
  IP-passthrough mode in front of a separate firewall. Use when auditing a home router or ISP gateway,
  reviewing bridge versus router mode and double NAT, DMZ/exposed-host settings, port forwards, UPnP and
  NAT-PMP, WPS, DNS settings, remote and cloud management, ISP remote management (TR-069), firmware and
  end-of-life status, built-in VPN or file-sharing features, or OpenWrt/DD-WRT specifics, or when a home
  router may have been compromised or had its DNS settings changed.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Consumer routers, ISP gateways, modems, and OpenWrt/DD-WRT routers, any vendor (verify the live firmware, ISP restrictions, and support status; menu names vary by vendor, ISP, and firmware)"
  audience: "home, homelab, work"
  finding_prefix: "RTR"
  modes: "discover, recommend, remediate, respond"
---

# Home Router and ISP Gateway Security

Act as a careful, evidence-driven network security engineer. The home router or ISP gateway is usually the
only thing between the household and the internet: whoever controls it can expose any device with a port
forward, redirect every lookup with a DNS change, and watch or proxy traffic. Even when a separate firewall
does the real work, the upstream gateway can still expose things the firewall's admin never sees. A bad
change here can also cut off the whole household's internet, including the agent's own access. Identify,
explain, prioritize, remediate (only when authorized), and verify weaknesses in the router, modem, or
gateway and in the settings it applies.

## How to use this skill

This skill holds only home-router- and gateway-specific guidance. It builds on the shared core, which
always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Router-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation,
government guidance, and advisories are in [references.md](references.md).

Related skills: if a dedicated firewall sits behind this device, assess it with
[OPNsense](../opnsense/SKILL.md) or [pfSense](../pfsense/SKILL.md). App-managed mesh Wi-Fi systems and
managed switches are covered by [Wi-Fi and switches](../wifi-and-switches/SKILL.md); Wi-Fi security modes
and SSID design for a router's own radios follow that skill too. DNS filtering services are in
[DNS filtering](../dns-filtering/SKILL.md) and self-hosted VPN servers in
[VPN servers](../vpn-servers/SKILL.md).

## Router-specific principles

- **Almost every change here is C2.** Changing WAN settings, bridge or passthrough mode, the LAN address
  range, DHCP, DNS, Wi-Fi, or the admin interface can drop the internet for the whole household. Many
  consumer routers reboot or restart networking to apply even small changes. Plan changes with the user
  present.
- **Bridge and WAN changes are the most dangerous.** Putting a gateway into bridge or passthrough mode, or
  taking it out, usually changes which device holds the public address and can strand the downstream
  firewall without a WAN connection. Recovery may need the ISP's help or a factory reset with the ISP's
  provisioning details (PPPoE credentials, VLAN tags) at hand. Never make these changes remotely.
- **The ISP may control part of the device.** ISP-supplied gateways are often managed by the ISP through
  TR-069/CWMP or a similar protocol, and the ISP can push firmware and settings. Some settings may be
  hidden, locked, or reverted by the ISP. Record what the user can't change instead of fighting it; the
  user's lever is a device of their own behind the gateway (NSA home-network guidance recommends this).
- **The cloud account or app may be the admin account.** Many current routers can be managed from a
  vendor app or cloud portal, sometimes from anywhere. Whoever controls that account controls the router.
  Treat the account, its 2FA, and anyone it is shared with as part of the device.
- **End of life is a security finding, not a footnote.** Old routers that no longer get firmware are a
  well-documented botnet target (see domain A). Look up support status on the vendor's own page for the
  exact model and hardware version; don't assume.
- **Configuration backups and some status pages are secrets.** Router backup files can contain the admin
  password, Wi-Fi passphrases, PPPoE credentials, dynamic DNS and VPN keys, sometimes in weak or reversible
  encoding. Never print, paste, or upload one. On OpenWrt and DD-WRT, whole-config dumps (`uci show`,
  `nvram show`) include secrets; read only the keys you need and redact.
- **Never test credentials.** Do not try default, printed-on-the-label, or guessed passwords, WPS PINs, or
  known exploits against any router, including the user's own. Ask the user to log in, or read settings
  through the access they already have.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Router as sole gateway** (consumer router or ISP gateway in router mode) | It holds the public address (or the ISP's CGNAT address), does NAT, DHCP, and DNS forwarding, and is the LAN's default gateway. | This device *is* the firewall: its port forwards, DMZ, UPnP, IPv6 firewall, remote management, and DNS define internet exposure. Assess everything here. |
| **ISP gateway in router mode in front of your own router or firewall** (double NAT) | The downstream device's WAN address is in a private range; two NAT layers; the gateway's own Wi-Fi may still be on. | Real exposure depends on both devices. Check the gateway's DMZ/exposed-host setting, port forwards, UPnP, and its own Wi-Fi and LAN ports: anything plugged into or joined to the gateway is *outside* the firewall. |
| **ISP gateway in bridge mode** | The downstream firewall gets the public address directly; the gateway no longer routes. | Usually the cleanest setup. Confirm what bridge mode really disables on this model: some gateways keep Wi-Fi, a management address, or extra LAN ports active, and ISP management still works. |
| **IP passthrough / "half bridge"** | The gateway still terminates the ISP link (login, authentication, or the fiber/DSL session) and hands its public address to one downstream device. | The gateway still routes, still runs management services, and may still serve other LAN or Wi-Fi clients. ISP documentation describes passthrough as removing the gateway's firewall protection from the passthrough device, so the downstream firewall must be complete on its own. Check what other devices still attach to the gateway. |
| **Standalone modem or ONT** | No routing; one Ethernet port to the router; often a status page on a fixed address. | Little to harden; the ISP manages it. Check the status page isn't reachable from untrusted segments and note that it reveals line and account details. |
| **Consumer router with vendor app or cloud management** | Setup and admin through an app or vendor account, sometimes alongside a local web UI. | The cloud account is an admin path; check 2FA, sharing, and whether remote cloud management can be turned off. |
| **Router running OpenWrt** | LuCI web UI, `uci` configuration, Dropbear SSH, `apk` (25.12 and later) or `opkg` (older) packages. | Full control and frequent security fixes, but releases reach end of life on a published schedule; mass package upgrades are discouraged by the project. See domain J. |
| **Router running DD-WRT** | DD-WRT web UI; configuration in `nvram`. | Builds are beta releases with limited testing and no formal security-advisory process found; judge support by build date and the project's own notes. See domain J. |
| **Router in access-point mode** behind a firewall | No NAT or DHCP; clients get addresses from the upstream firewall. | Routing features should be off; assess admin access, firmware, and Wi-Fi. Mesh systems use [Wi-Fi and switches](../wifi-and-switches/SKILL.md). |

## Detection

Hints for recognizing these devices during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **Position:** usually the LAN's default gateway, DNS server, and DHCP server, or (behind a separate
  firewall) the next hop on the firewall's WAN side. A downstream WAN address in a private range points to
  an ISP gateway still routing (double NAT).
- **Admin web UI** on HTTP 80 and/or HTTPS 443 (some vendors also use 8080 or 8443), whose page title,
  login page, or certificate names the vendor, model, or ISP. Many vendors also publish a convenience
  hostname for the admin page; don't rely on it during inventory.
- **SSDP/UPnP:** routers with UPnP on answer SSDP on UDP 1900 and announce an `InternetGatewayDevice`
  (UPnP IGD) device type; the device description XML usually names the manufacturer and model.
  NAT-PMP/PCP listens on UDP 5351 when enabled.
- **ISP management:** TR-069/CWMP connection-request listeners commonly use TCP 7547 on the WAN side. Only
  check the WAN side from outside with explicit authorization; an open 7547 shows the device is
  ISP-managed, not that it is vulnerable.
- **OpenWrt:** LuCI login page titled with the hostname and "LuCI"; uHTTPd web server; Dropbear SSH banner
  on port 22. **DD-WRT:** web UI that names DD-WRT. Many consumer firmwares also run a DNS forwarder on 53
  and sometimes Telnet, SSH, SMB, FTP, or media services if USB sharing is on.
- **Modems and ONTs:** a minimal status page on a fixed address reachable only from the directly connected
  port; the vendor documents the address.
- **MAC address vendors (OUIs):** retail routers usually carry the vendor's own OUI; ISP gateways often
  carry the OEM manufacturer's OUI rather than the ISP's name. Per-SSID BSSIDs and WAN MACs may differ from
  the LAN MAC.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

For most consumer routers and ISP gateways the evidence is the web UI or the vendor app, viewed by the
user. Ask the user to log in and show each screen (or share screenshots with secrets covered) rather than
handing over the admin password. Menu names and locations vary widely by vendor, ISP, and firmware, so
describe each setting by its function and ask the user to find it; verify the exact path in the vendor's
current documentation.

From a LAN client, these are candidate read-only checks, **not yet verified** against every environment:

```sh
ip route show default            # Linux: default gateway (macOS: route -n get default)
ipconfig getpacket en0           # macOS: DHCP-provided router and DNS servers (interface name varies)
resolvectl status                # Linux with systemd-resolved: DNS servers in use
dig example.com                  # which resolver answered (the SERVER line) and whether it resolves
upnpc -l                         # miniupnpc: lists the IGD and its current port mappings (if UPnP is on)
nmap -sT -p 21,22,23,53,80,139,443,445,1900,5351,7547,8080,8443 <router-lan-ip>   # with authorization
```

- `upnpc -l` only lists mappings. **Never** run `upnpc -a` or `-d` (they add or delete mappings).
- Run port scans only against the router's LAN address, only with the user's authorization, and never
  aggressive or script scans. Scanning the WAN side from outside requires explicit authorization and is
  only meaningful from a host that is really outside (not from the LAN through NAT loopback).

For OpenWrt over SSH, candidate read-only commands, **not yet verified** on every release (check each
exists first; 25.12 and later use `apk`, older releases `opkg`):

```sh
cat /etc/openwrt_release; ubus call system board   # release, target, board name
apk list --installed            # 25.12+: installed packages (older: opkg list-installed)
apk list --upgradable           # 25.12+: packages with updates (older: opkg list-upgradable after opkg update)
netstat -lntup                  # listening services (BusyBox netstat)
uci show firewall               # zones, forwards (port forwards are 'redirect' sections), rules
uci show uhttpd; uci show dropbear   # LuCI/uHTTPd and SSH listen settings
uci show upnpd                  # UPnP/NAT-PMP daemon, if installed
nft list ruleset                # fw4 ruleset actually loaded (22.03 and later)
uci show wireless | grep -E "wps|encryption|disabled|ssid"   # avoids printing the 'key' lines
logread | tail -n 200           # recent system log (RAM; lost on reboot)
```

- **Never** run `uci show network` or `uci show wireless` whole in a shared session (they can contain
  PPPoE credentials and Wi-Fi keys), `uci set`/`uci commit`, `/etc/init.d/<service> restart`,
  `apk upgrade`/`opkg upgrade`, `sysupgrade`, `firstboot`, or `reboot`. On DD-WRT, never run `nvram show`
  (prints every secret) or `nvram set`/`nvram commit`; read single keys with `nvram get <key>` only.

### Things never to do in Discover

- Reboot, power-cycle, or factory-reset the router, gateway, modem, or ONT.
- Update firmware or packages, or toggle automatic updates, without explicit approval (Remediate, C2).
- Change WAN, bridge/passthrough, PPPoE, VLAN, LAN addressing, DHCP, or DNS settings.
- Log in with, test, or guess default or label passwords, WPS PINs, or any credential.
- Run exploit scripts, vulnerability "proof" scripts, or router-attack tools.
- Export a configuration backup into the agent's context or upload it anywhere.
- Ask the ISP to change anything on the user's behalf.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Hardware, firmware, and end-of-life status

- Exact model and **hardware version** (vendors often support one hardware revision and not another), who
  supplied it (ISP or user), and the running firmware version and date.
- Support status on the vendor's own end-of-life or support page for that model. For ISP gateways, ask
  the ISP's support pages whether the model is still current; ISPs replace old gateways on request.
- Firmware update mechanism: automatic updates on or off, last update date, and whether the ISP pushes
  updates (the user may not control them).
- Vendor security advisories for the model (vendor PSIRT pages in [references.md](references.md)); then
  validate per core triage and check CISA KEV for anything that matches.
- Why this matters, factually: the FBI warned in May 2025 (IC3 PSA I-050725-PSA) that criminal proxy
  services were compromising end-of-life routers, mostly with remote administration turned on, with
  variants of the TheMoon malware, and said routers dated 2010 or earlier likely no longer receive
  updates. CISA's BOD 26-02 (February 2026) orders US federal civilian agencies to remove end-of-support
  edge devices, including routers; it binds only those agencies, but its reasoning applies to any network.
- An end-of-life router that is the sole gateway is at least **P1** if any internet-facing service is on
  (remote management, VPN server, cloud/file access, port forwards), and a replacement finding otherwise.

#### B. Administration and accounts

- Local admin account: whether the password is still the default or the label password (ask the user;
  never test), and whether it is shared with the Wi-Fi passphrase.
- Number of admin accounts; some routers have a separate, weaker "user" account or a hidden ISP account.
- Vendor app or cloud account: who owns it, whether it has 2FA, who it is shared with, and whether
  remote/cloud management is on. Note any vendor "account required" setup flow.
- Admin session protection: HTTPS on the admin UI where offered, login lockout or rate limiting, session
  timeout.
- Which networks can reach the admin UI: the guest network and IoT devices should not.
- Other admin protocols on the LAN: Telnet, SSH, SNMP, TR-064 (LAN-side ISP-configuration protocol on some
  gateways), vendor discovery or HNAP-style APIs. Each one that isn't needed is surface.

#### C. Remote management and cloud access

- **WAN/remote management** of the web UI (often called remote management, web access from WAN, or remote
  access): on or off, which port, and any allowed-source restriction. CISA, NSA, and FBI guidance all say
  to turn it off; the FBI linked compromised end-of-life routers to remote administration being on.
- Cloud or app remote management: whether it can be disabled, and what it lets the vendor or a stolen
  account do.
- **ISP remote management (TR-069/CWMP):** whether the device is ISP-managed (ISP gateway, ACS URL shown in
  a management or TR-069 page, open TCP 7547 seen from outside). On ISP gateways this usually can't and
  shouldn't be disabled by the user; record it as an accepted, ISP-controlled risk. On a user-owned router,
  a configured ACS the user doesn't recognize is a finding. Context: in 2016 a Mirai variant abused an
  internet-reachable TR-064/TR-069 service on port 7547 and knocked about 900,000 ISP routers offline.
- Vendor remote-access features that publish LAN resources to the internet (for example ASUS AiCloud,
  which shares USB storage and LAN files over the web, and similar features from other vendors). ASUS has
  published advisories for AiCloud-enabled routers and has advised disabling AiCloud and other
  internet-facing services where firmware can't be updated. Check whether each such feature is on and
  needed.
- Dynamic DNS clients: which hostname points at the household, and who holds the DDNS credentials.

#### D. Bridge, passthrough, and double NAT

- Which device holds the public IPv4 address (or whether the ISP uses CGNAT), and which hands out IPv6
  prefixes.
- In a two-device setup, the upstream gateway's mode: router, bridge, or IP passthrough. Confirm with the
  gateway's status page, not only the setting name.
- **DMZ / "exposed host" / "default server"**: if set, every unsolicited inbound connection goes to that
  host. Pointed at a downstream firewall's WAN address this is a common and acceptable pattern (the
  firewall becomes the boundary); pointed at a PC, NAS, or console it is a **P1** exposure.
- Port forwards and UPnP on the *upstream* device (domain E): invisible from the downstream firewall.
- The upstream gateway's own Wi-Fi and spare LAN ports: if still on, anything joining them is outside the
  firewall and may reach the gateway's admin UI. Identify every client attached to the gateway.
- Two DHCP servers or two Wi-Fi networks with similar names, which confuse users into joining the wrong
  one.

#### E. Port forwards, UPnP/NAT-PMP, and DMZ

- Every port forward and port trigger: target host, ports, IPv4/IPv6, whether still needed, and who uses
  it. Forwards to admin interfaces (NAS, cameras, the router itself) are high priority.
- **UPnP IGD** and **NAT-PMP/PCP**: on or off; if on, the current mapping list (`upnpc -l` or the router's
  UPnP status page) and which hosts created them. CISA advises disabling UPnP, enabling it only briefly
  if a device needs it. A mapping nobody can explain is a potential compromise indicator.
- Whether UPnP is reachable from the WAN side (it should never be; check from outside only with
  authorization).
- DMZ/exposed host (domain D).

#### F. DNS settings and DNS hijacking

- WAN DNS servers the router uses, and the DNS server(s) it hands to clients over DHCP and IPv6 router
  advertisements. Every value should be the ISP's, a resolver the user chose, or the user's own resolver.
  An unknown resolver is a **P0 indicator** (see Respond): attackers, including state groups reported by
  the UK NCSC in 2026, change router DNS settings to redirect traffic and harvest credentials, and older
  campaigns did the same through browser-based attacks on router admin pages.
- Whether clients actually resolve through the expected server (the `SERVER` line from `dig`).
- Router-provided "secure DNS", parental-control, or filtering services: which provider, and whether they
  replace the user's resolver.
- DNS rebinding protection, where the firmware offers it.
- Static host entries or local DNS overrides on the router.

#### G. Wi-Fi features on the router itself

Use [Wi-Fi and switches](../wifi-and-switches/SKILL.md) for security modes, passphrases, and SSID design.
Here, check only router-specific items:

- **WPS** (push-button and especially PIN): CISA recommends disabling it.
- **Guest network:** on or off, whether it is isolated from the LAN and from the admin UI (vendor
  wording varies; "allow guests to access local network" should be off), and whether isolation still
  works in the current mode (some routers drop guest isolation in access-point or bridge mode).
- Radios that should be off (an ISP gateway's Wi-Fi in a double-NAT setup, or an unused band).
- ISP "community" or public hotspot features that share the gateway's bandwidth as a separate SSID: on or
  off, and whether the user knows.

#### H. IPv6

- Whether IPv6 is active on WAN and LAN.
- The router's IPv6 firewall: on, and blocking unsolicited inbound by default. NSA home-network guidance
  says the router should have IPv6 firewall capabilities. Some firmwares expose an option to allow all
  inbound IPv6 or to disable the IPv6 firewall; either is a finding.
- IPv6 pinholes and forwards (which reach hosts directly, with no NAT), including UPnP/PCP-created ones.

#### I. Built-in services: VPN, file sharing, media, and others

- Built-in VPN servers (WireGuard, OpenVPN, IPsec/L2TP, legacy PPTP): which are on, who has accounts or
  profiles, and protocol strength. PPTP is obsolete; treat it as a finding. Assess active servers using
  the principles in [VPN servers](../vpn-servers/SKILL.md).
- USB storage sharing: SMB, FTP, DLNA/media server, "web file access". Check guest/anonymous access, which
  networks can reach it, and whether it is reachable from the WAN (FTP and web file access often are when
  "remote" options are on). Old SMB1 support is a finding.
- Other add-ons: vendor security suites, parental controls, traffic analysis services that send data to
  the vendor, printer sharing, Telnet/SSH, SNMP.
- Every listening service you saw (domain B scan or `netstat -lntup`) mapped to the feature that owns it.

#### J. OpenWrt and DD-WRT specifics

- **OpenWrt release support:** the project publishes a support table; a release reaches end of life one
  year after its initial release or six months after the next major release, whichever is later, and
  end-of-life releases get no updates, even for severe vulnerabilities. Compare the installed release
  with the current table and check the OpenWrt security advisories page.
- **Package updates:** the OpenWrt project strongly discourages mass package upgrades (`opkg upgrade`,
  `apk upgrade`, or the equivalent LuCI button); the supported path to current packages is a sysupgrade
  to a new release (Attended Sysupgrade in LuCI or `owut` on 25.12). Note available updates; don't apply
  them.
- **LuCI and SSH exposure:** OpenWrt's default firewall blocks inbound WAN traffic; LuCI or SSH reachable
  from WAN means someone added a rule or port forward, which the project strongly discourages. Check
  uHTTPd listen addresses and the HTTP-to-HTTPS redirect, Dropbear interface binding, password versus key
  login, and root password set.
- Firewall zones: the WAN zone's input and forward policy (should reject/drop), any rules or redirects
  that open the WAN, and zones that let guest or IoT networks reach the router's services.
- Extra packages: third-party feeds, packages nobody remembers installing, and services they listen on.
- **DD-WRT:** build date and source (the project's FAQ says builds are betas with limited hardware testing
  and warns that its router database may be out of date); remote management, Telnet/SSH, UPnP, and DNS
  settings as for any router. No formal security-advisory channel was found; judge currency by build date.
- Vendor firmware replaced by OpenWrt or DD-WRT: who maintains it, and whether anyone will keep it
  updated.

#### K. Logs, monitoring, and physical

- What the router logs (admin logins, configuration changes, firmware updates, blocked connections) and
  whether logs survive a reboot (most consumer routers keep logs only in RAM).
- Remote syslog or email alerts, where offered.
- Physical location: anyone with physical access can factory-reset most routers and then set them up
  fresh, and some ISP gateways print admin and Wi-Fi credentials on the label.
- Who in the household or at the ISP can change the router.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

The router is under everything in the home, so list what depends on the setting first:

- **Internet access for the whole household**, including work-from-home, phones on Wi-Fi calling, alarm
  systems, and medical or safety devices.
- **The agent's own access** and the user's path to the admin UI (Wi-Fi client, wired client, app).
- **The downstream firewall's WAN**: bridge, passthrough, DMZ, and LAN-address changes on the gateway can
  disconnect it.
- **Port forwards and UPnP mappings**: game consoles, remote cameras, self-hosted services, VPN servers.
- **DNS and DHCP**: every client; static reservations that firewall rules or cameras depend on.
- **ISP services that ride on the gateway**: TV set-top boxes, voice/phone ports, ISP Wi-Fi extenders, and
  ISP support tools that need TR-069.
- **Wi-Fi clients and IoT devices** that may not rejoin after a change.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| End-of-life router | Replace with a supported model, or install supported OpenWrt if the hardware is supported and the user can maintain it. Until then, turn off every internet-facing feature. | Cost; setup time; Wi-Fi clients must rejoin unless SSID and passphrase are reused. |
| Outdated firmware | Update from the vendor's own update function or site; turn on automatic updates if offered. | Reboot and brief outage; rare regressions. ISP gateways may update only when the ISP pushes. |
| Default or label admin password | Set a long, unique admin password in a password manager. | Saved app or browser logins need updating. |
| Remote/WAN management on | Turn it off; use a VPN to the home network for remote admin. | Remote admin stops until a VPN path exists. |
| Cloud/app management without 2FA | Enable 2FA on the vendor account; review shared admins; turn off cloud remote access if not needed. | Some apps need cloud access for any management. |
| Vendor cloud/file-access feature on (AiCloud-style) | Turn it off unless actively needed; prefer a VPN. | Remote file access stops. |
| UPnP/NAT-PMP on | Turn off, or limit to the device that needs it. | Some games, consoles, and apps lose automatic port mapping. |
| Unneeded port forwards or DMZ to a host | Remove; if the DMZ targets a downstream firewall, keep it but make sure the firewall's WAN rules are complete. | Services behind the forward become unreachable from outside. |
| Double NAT with the gateway still routing | Use bridge or passthrough mode if the ISP supports it; otherwise DMZ to the firewall and turn off the gateway's Wi-Fi and UPnP. | **Highest-risk change** in this skill: the whole household goes offline if it fails. Needs the user present and a recovery plan. |
| Gateway Wi-Fi left on behind a firewall | Turn it off, or keep only clients that should be outside the firewall. | Devices on it must move to the main Wi-Fi. |
| Unknown DNS servers | Treat as an incident first (Respond); then set known resolvers. | Clients may cache bad answers until renewed. |
| WPS on | Turn it off. | Push-button pairing stops working. |
| Guest network not isolated | Turn on isolation from the LAN and the admin UI. | Guests lose casting/printing to LAN devices. |
| IPv6 firewall off or allow-all | Turn the IPv6 firewall on with default-deny inbound. | Inbound IPv6 services need explicit pinholes. |
| Built-in VPN with PPTP or stale accounts | Disable PPTP; use WireGuard or OpenVPN; remove unused accounts. | Old clients need new profiles. |
| USB sharing open or WAN-reachable | Disable if unused; require accounts; turn off FTP and web access from WAN. | Shared drive access changes. |
| OpenWrt end-of-life release | Sysupgrade to a supported release (Attended Sysupgrade or `owut`), after a configuration backup. | Reboot; packages are reinstalled; test each feature after. |
| LuCI or SSH reachable from WAN | Remove the WAN rule or forward; use a VPN or SSH tunnel. | Remote admin stops until a VPN path exists. |

Changing the admin port or hiding the SSID are not security fixes. Never recommend them as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet-facing admin or file access,
unknown DNS, end-of-life with exposed services) → high-priority hardening → routine maintenance → optional
defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Router specifics:

- **The user must be present, at home, with physical access.** Changes to bridge or passthrough mode, WAN
  or PPPoE settings, the LAN address range, DHCP, or the admin path can cut off the whole household's
  internet and the agent's own access. Don't make any of them remotely, and don't make them while the
  household depends on the connection (calls, work, school) unless the user accepts that.
- **Have a fallback before starting:** a wired client that can reach the router's admin page directly,
  the router's physical reset button and what it restores, the ISP's provisioning details (PPPoE
  username/password, VLAN, MAC cloning) if a reset would need them, and the ISP's support number. A phone
  with mobile data helps if the home internet drops.
- **Take a configuration backup first** where the router offers one, and have the user store it off the
  router as a secret. Screenshot each settings page you will change.
- **Bridge and passthrough changes:** confirm the downstream firewall is ready to take the WAN (correct
  WAN mode, rules complete without the gateway's protection), know how to reach the gateway after the
  change (many gateways keep a management address only on a specific port or need a reset to leave bridge
  mode), and plan for the downstream firewall needing a WAN renew or reboot.
- **Firmware updates are C2:** use the vendor's own update function or downloads only; never third-party
  firmware images unless the user has chosen OpenWrt/DD-WRT knowingly. Don't interrupt power during an
  update. On OpenWrt use sysupgrade (Attended Sysupgrade or `owut`), not mass package upgrades.
- **Admin password and access changes:** keep one logged-in session open while changing the password or
  remote-management settings, and confirm the new login works from a second session before closing it.
- **ISP-controlled settings:** don't try to work around TR-069 or ISP locks. If a setting can't be changed,
  record it and recommend putting a user-owned router or firewall behind the gateway.
- Change one thing, then verify (core "after a change"): re-read the setting, confirm internet access,
  DNS resolution through the expected server, DHCP for a new client, the admin path, and anything that
  depended on the setting (port forwards, VPN).

### Hard stops (refer to a specialist or do manually; never automate)

- Factory reset as a security fix without the user present and the ISP provisioning details at hand.
- Bridge, passthrough, WAN, or PPPoE changes from a remote session.
- Flashing third-party firmware (OpenWrt, DD-WRT), bootloaders, or recovery images; serial or TFTP
  recovery.
- Any attempt to disable, bypass, or reconfigure ISP management (TR-069), unlock ISP firmware, or extract
  ISP credentials.
- Credential guessing, default-password testing, or running exploits, on any device.
- Mass package upgrades on OpenWrt (`apk upgrade`, `opkg upgrade`) or `nvram` edits on DD-WRT.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the router-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### RTR-001: ISP gateway still routing in front of the firewall, with its own Wi-Fi and UPnP on

**Confidence:** Confirmed
**Priority:** P2. Devices on the gateway's Wi-Fi sit outside the firewall's policy, and UPnP on the
gateway lets any of them open inbound ports the firewall's admin can't see.
**State:** Open
**Component:** ISP-supplied fiber gateway in router mode, upstream of a separate firewall
**Evidence:** Observed 2026-10-12: the firewall's WAN address is `192.0.2.2` with the gateway at
`192.0.2.1`; the gateway's status page shows the public address `203.0.113.45`, DMZ set to `192.0.2.2`,
UPnP on, and its 2.4/5 GHz Wi-Fi broadcasting an SSID with two clients (a smart plug and a game console).
`upnpc -l` from the console's segment listed one mapping, TCP 3074 to the console. The user confirmed
both clients were joined to the gateway by mistake.
**Expected secure state:** one routing boundary under the user's control; the gateway in bridge or
passthrough mode, or with Wi-Fi and UPnP off and DMZ only to the firewall (NSA home-network guidance;
CISA advice to disable UPnP).
**Exposure and prerequisites:** any device on the gateway's Wi-Fi; the UPnP mapping is internet-reachable.
**Dependencies / blast radius:** the ISP's TV box is wired to the gateway and needs it in router mode
(per the ISP's support page), so bridge mode is not possible here.
**Recommended remediation:** move the two clients to the main Wi-Fi behind the firewall, then turn off
the gateway's Wi-Fi and UPnP; keep the DMZ pointed at the firewall. Record bridge mode as not possible
(accepted, ISP-dependent).
**Operation class:** C2 (Wi-Fi off disconnects clients; done with the user present).
**Approval required:** Yes.
**Verification:** the gateway's SSID no longer broadcasts; its UPnP status shows disabled and no
mappings; the console reaches the internet through the firewall; the TV box still works.
**Rollback:** re-enable Wi-Fi or UPnP on the gateway from its settings page (screenshots taken before the
change).

---

## Version history

- **1.0** (2026-10-30): Initial version.
