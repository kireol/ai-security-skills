---
name: wifi-and-switches
description: >-
  Security assessment, hardening, remediation, and incident response for consumer and prosumer Wi-Fi mesh
  systems (app-managed systems such as eero, Google/Nest Wifi, Deco, Orbi, and UniFi-style controllers)
  and managed or smart switches, including used enterprise switches such as older Cisco Catalyst units in
  homelabs. Use when auditing Wi-Fi security modes, guest and IoT SSIDs, router versus bridge mode, vendor
  cloud accounts, UPnP, firmware and end-of-support status, or switch management access, legacy
  protocols, VLANs, ports, and config backups, or when a mesh system or switch may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "App- or controller-managed Wi-Fi mesh systems and managed/smart Ethernet switches, any vendor (verify the live firmware, app version, and support status; menus change often)"
  audience: "home, work, homelab"
  finding_prefix: "WIFI"
  modes: "discover, recommend, remediate, respond"
---

# Wi-Fi Mesh and Managed Switch Security

Act as a careful, evidence-driven network security engineer. The Wi-Fi system and the switches are the
layer every device joins first: a weak Wi-Fi mode lets anyone in radio range onto the network, a mesh in
the wrong mode can silently bypass the real firewall, and a switch with an exposed or legacy management
plane lets an attacker re-patch VLANs and watch traffic. A bad change here can also disconnect every
wireless client, including the user's phone that runs the management app. Identify, explain, prioritize,
remediate (only when authorized), and verify weaknesses in the wireless and switching layer.

## How to use this skill

This skill holds only Wi-Fi-mesh- and switch-specific guidance. It builds on the shared core, which always
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

Mesh- and switch-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and standards guidance are in [references.md](references.md).

If a separate firewall (for example OPNsense) sits in front of or behind the mesh, assess it with its own
skill too. This skill covers the mesh's own routing features only to decide whether they should be on.

## Wi-Fi- and switch-specific principles

- **Most Wi-Fi changes are C2.** Changing the security mode, passphrase, SSID, band settings, or
  router/bridge mode disconnects clients, and some vendors restart the whole network when the mode
  changes. IoT devices that only support older modes may never rejoin. Plan these with the user present.
- **The management app may ride on the network you are changing.** For app-managed mesh systems the
  phone running the app is usually a Wi-Fi client. A mistake can strand the user without a way to undo
  it except a physical reset. Confirm a fallback path (wired client, cellular-connected app, or physical
  access) first.
- **The vendor cloud account is the admin account.** For eero-, Google/Nest-, Deco-, Orbi-app- and
  cloud-hosted UniFi-style systems there is often no local admin password at all: whoever controls the
  cloud account (or a household member it is shared with) controls the network. Treat account security
  and shared-admin lists as part of the device.
- **Running configs are secrets.** Switch running/startup configurations and controller backups contain
  password hashes (some reversible, such as Cisco "type 7"), SNMP community strings, RADIUS/TACACS keys,
  and Wi-Fi passphrases. Never print, paste, or upload one whole. Read only the lines you need and redact.
- **Used and refurbished switches arrive with someone else's history.** An unknown prior config, old
  local accounts, Smart Install or other zero-touch features, and firmware of unknown origin are normal
  for second-hand enterprise gear. Check provenance and support status before trusting one.
- **Support status is a security property.** Consumer mesh vendors stop shipping firmware for old models
  and old enterprise switch lines reach their vendor's end of vulnerability/security support date. Look
  the date up on the vendor's lifecycle page for the exact model; don't assume.
- **Never test credentials.** Do not try default or guessed passwords, WPS PINs, or SNMP community
  strings against any device. Ask the user what is configured, or read it from the device with their
  authorized access.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Mesh in router mode, sole gateway** | The mesh's primary node connects to the modem/ONT; it hands out DHCP and is the default gateway. | The mesh *is* the firewall: its port forwards, UPnP, DMZ, and remote-access settings define internet exposure. |
| **Mesh in router mode behind another router or firewall** (double NAT) | Mesh WAN address is in a private range; clients get addresses from the mesh while a separate firewall also does NAT/DHCP. | Two NAT layers and two DHCP servers. Firewall rules and VLANs on the real firewall don't see individual Wi-Fi clients, and the mesh's own UPnP and port forwards may be invisible to the firewall's admin. Usually should be bridge mode. |
| **Mesh in bridge/access-point mode** | Clients get DHCP from the upstream firewall; the mesh has no WAN NAT. | Firewall policy applies to Wi-Fi clients. Vendors document that bridge mode disables some features (often guest networks, parental controls, and device-level security features); confirm what the guest/IoT SSIDs do in bridge mode. |
| **Controller-managed APs** (UniFi-style, Omada-style) | A controller (cloud, self-hosted, or a gateway console) adopts APs and switches. | The controller is the management plane for everything adopted; assess its exposure, accounts, and backups. VLAN-tagged SSIDs are possible. |
| **ISP-supplied gateway with Wi-Fi** | ISP-branded hardware; firmware pushed by the ISP. | The user may not control firmware or remote management; the ISP may have its own management access. Record what can't be changed. |
| **Unmanaged switch** | No IP address or management interface. | Nothing to harden; note it can't enforce VLANs and treat everything on it as one segment. |
| **Smart / web-managed switch** | Web UI only, sometimes an app or cloud; limited CLI. | Often HTTP-only management and simple passwords; management may answer on every VLAN. Check firmware support carefully. |
| **Enterprise managed switch** (new or used, e.g. Catalyst-class) | CLI over console/SSH/Telnet; full VLAN, ACL, SNMP features. | Large management-plane surface: Telnet, HTTP server, SNMP, zero-touch install features, CDP/LLDP. Used units may be past vendor support. |

## Detection

Hints for recognizing these devices during a network inventory (used by the `full-assessment` skill).
Defaults can be changed and many consumer mesh nodes expose almost nothing locally, so confirm with the
user before relying on a match.

- **App-managed mesh nodes:** often no local web UI at all, or a minimal page that tells you to use the
  app. If in router mode, the primary node is the LAN default gateway, DNS server, and DHCP server. Some
  answer SSDP (UDP 1900) as a UPnP Internet Gateway Device when UPnP is on; the SSDP device description
  usually names the vendor and model.
- **Controller-managed APs and switches (UniFi-style):** the vendor documents a required-ports list; it
  includes UDP 10001 for device discovery and TCP 8080 for device-to-controller communication, with the
  controller web UI on HTTPS (commonly 8443 on self-hosted controllers, 443 on console hardware). Verify
  against the vendor's current required-ports reference.
- **Smart/web-managed switches:** a web login page on HTTP 80 and/or HTTPS 443 whose title names the
  vendor or model; sometimes a vendor discovery utility protocol on a UDP broadcast port.
- **Enterprise switches:** SSH (22) and often Telnet (23) with a login banner or `User Access
  Verification` prompt; an HTTP/HTTPS management server (80/443) if enabled; SNMP on UDP 161; on Cisco
  IOS switches that still have it, Smart Install on TCP 4786. CDP and LLDP announcements on access ports
  name the platform, software version, and management address.
- **MAC address vendors (OUIs):** mesh nodes and switches usually carry the vendor's own OUI; rebadged
  ISP hardware carries the OEM's OUI, and per-SSID or per-band BSSIDs on Wi-Fi are often locally
  administered addresses that don't map to a vendor at all.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

For app-managed mesh systems, the evidence is mostly screenshots or user-read values from the vendor app
or web console. Ask the user to show each screen rather than handing over their account. For controllers,
ask for a read-only (view-only) admin role if the product offers one. For switches, prefer the console or
SSH session the user already uses.

Candidate read-only commands for Cisco IOS / IOS XE switches. These are standard Cisco IOS `show`
commands, but output and availability vary by platform and release: **not yet verified** on every
version. Check each exists first (`show ?`).

```text
show version                         ! platform, software release, uptime, last reload reason
show inventory                       ! model and module PIDs (redact serial numbers in the report)
show ip interface brief              ! which interfaces and SVIs have management addresses
show interfaces status               ! port state, VLAN, speed; spot unused but enabled ports
show vlan brief                      ! VLANs and access-port membership (VLAN 1 usage)
show interfaces trunk                ! trunks, native VLAN, allowed VLANs
show ip ssh                          ! SSH version and whether it is enabled
show line vty 0 15 | include put     ! allowed transports (telnet/ssh) on vty lines
show ip http server status           ! HTTP and HTTPS server state
show snmp community                  ! community names (treat output as secret; redact)
show snmp user                       ! SNMPv3 users and auth/priv settings
show vstack config                   ! Smart Install role and state (where the command exists)
show tcp brief all | include 4786    ! Smart Install listener (Cisco-documented check)
show cdp neighbors; show lldp neighbors
show users; show logging             ! current sessions and the local log buffer
show archive                         ! config archive, if configured
```

- **Never** run `write erase`, `erase startup-config`, `reload`, `configure terminal` (or `conf t`),
  `copy ... startup-config`, `copy ... running-config`, `delete` or `format` on flash, `vstack` commands,
  `debug` commands, or `boot` changes. These are C2/C3, not R.
- **Never** print `show running-config` or `show startup-config` whole; they contain secrets. Filter to
  the section you need (`show running-config | section line vty`) and redact keys, hashes, and community
  strings before showing them. Treat `show tech-support` the same way.
- For smart switches and mesh apps, there is no shell: use the UI. Don't install vendor "discovery"
  utilities on the user's machine without approval.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, firmware, and support status

- Every mesh node, AP, controller, and switch: vendor, model, hardware revision, firmware version.
- Support status for each, from the vendor's lifecycle or end-of-life page (not memory): still receiving
  security updates, announced end of sale, or past end of vulnerability/security support. For Cisco, the
  relevant milestone is "End of Vulnerability/Security Support" in the product's end-of-life bulletin.
- Automatic updates for mesh systems: on or off, and when the last update was installed. Some vendors
  update only automatically; others let the user defer or disable updates.
- Switch firmware: release in use versus the vendor's current recommended release for that model, and
  where the image came from (vendor download with checksum, or unknown, for example "came with the used
  switch").
- Check vendor security advisories for the installed release (core triage). For any device that is
  internet-reachable or on the network edge and past support, note CISA's end-of-support edge device
  guidance (BOD 26-02), which explicitly lists switches and wireless access points among edge devices.

#### B. Wi-Fi security modes

For each SSID and band:

- Security mode: WPA3-Personal (SAE), WPA2/WPA3 transition (mixed) mode, WPA2-Personal (AES/CCMP),
  WPA/WPA2 mixed with TKIP, WEP, or open. Open, WEP, and TKIP are findings; WPA2-only is a finding to
  plan, not an emergency, if clients can't do WPA3.
- Whether WPA3 is available but off. Some vendors default to WPA2 and offer WPA3 as an opt-in toggle
  that switches the network to transition mode.
- Protected Management Frames (PMF/802.11w): required, optional (capable), or off. Transition mode
  normally runs PMF as optional so WPA2 clients can join, which leaves them open to deauthentication and
  downgrade attacks.
- 6 GHz (Wi-Fi 6E/7): the Wi-Fi Alliance requires WPA3 or Enhanced Open there, with PMF; WPA2 and
  transition mode aren't allowed on 6 GHz. If a product offers 6 GHz only with WPA3, that is expected.
- Passphrase: length and whether it is a vendor-printed default from the label (ask the user; don't read
  it out). Who has it, and when it was last changed (former tenants, contractors, guests).
- **WPS:** on or off, and whether the PIN method (as opposed to push-button) is available. The WPS PIN
  design flaw (CERT VU#723755) lets an attacker in radio range recover the PIN and then the passphrase;
  CERT also noted some devices kept WPS on after the UI showed it disabled.
- Enterprise SSIDs (WPA2/WPA3-Enterprise): RADIUS server, certificate validation by clients, and EAP
  methods.

#### C. Guest and IoT networks and isolation

- Which SSIDs exist and which devices are on each: guest, IoT, cameras, main.
- Guest network: isolated from the main network (can't reach LAN devices or the mesh's admin), and
  whether guests can see each other (client isolation).
- IoT SSID: what it can reach. On a mesh in router mode, a "separate IoT network" may be only a separate
  passphrase on the same subnet; check whether it is really a different network. On controller systems,
  check the VLAN tag and the firewall rules that apply to that VLAN.
- In bridge mode: whether guest/IoT SSIDs still exist, and if so whether they are tagged onto a VLAN the
  firewall controls. Vendors differ; some remove the guest network in bridge mode.
- Hidden SSIDs and MAC filtering presented as security controls. They aren't; note them but don't count
  them as isolation.

#### D. Router vs. bridge mode and the routing features on the mesh

- Operating mode of the mesh: router (NAT/DHCP) or bridge/AP.
- If there is also a separate firewall or ISP router: is there double NAT? Which device hands out DHCP
  to Wi-Fi clients and which DNS server they get? Two DHCP servers on one segment is a finding.
- If the mesh routes: its port forwards, DMZ/"exposed host" settings, IPv6 firewall behavior (inbound
  IPv6 allowed or blocked), and any remote-access or VPN feature it offers.
- **UPnP and NAT-PMP on the mesh:** on or off, and current mappings if the app shows them. In double-NAT
  setups the mesh's UPnP mappings are invisible from the upstream firewall.
- DNS settings pushed to clients, and any "security" or content-filtering DNS feature (who operates it).

#### E. Vendor cloud account and administration

- Who owns the vendor account; whether **MFA** is on for that account (or for the parent account it
  uses, such as a large platform account). Some apps sign in only with an emailed or texted one-time
  code; record what the account really relies on.
- Shared admins / household members with admin rights; remove anyone who shouldn't have it.
- Linked integrations: smart-home platforms, voice assistants, ISP or installer access, third-party
  apps with API or "works with" access.
- Self-hosted controllers: local admin accounts, MFA, whether remote/cloud access is enabled, and
  whether the controller UI is reachable from the internet or from guest/IoT segments.
- Local web UI (where it exists): admin password changed from the label default, HTTPS, and whether it
  is reachable from guest/IoT SSIDs. Remote web management from the WAN should be off.

#### F. Switch management plane

- Which VLAN(s) and addresses the switch answers management on. Ideally a dedicated management VLAN (not
  VLAN 1) reachable only from admin hosts; not from guest, IoT, or camera segments.
- Remote management protocols: SSH version 2 only; **Telnet off** on all vty lines; **HTTP server off**
  (HTTPS only, or no web server if unused).
- vty access-class or management ACL restricting source addresses; exec timeout set.
- Local accounts: named accounts with strong secrets; no reversible (type 7) passwords as the main
  protection (`service password-encryption` only obscures); an enable secret, not an enable password.
- AAA/RADIUS/TACACS if used, and the fallback local account.
- **SNMP:** SNMPv1/v2c communities send the community in cleartext; any read-write community is a
  high-severity finding. Prefer SNMPv3 with authentication and privacy, restricted by ACL, or SNMP off
  if nothing polls it.
- Zero-touch and legacy services: Cisco **Smart Install** (TCP 4786) should be disabled where the release
  supports `no vstack`, or blocked by ACL where it doesn't. Also check for HTTP-based config features,
  TFTP servers, and unused services (finger, small servers, bootp) on old releases.
- CDP/LLDP on ports facing untrusted devices (they disclose the platform and version).
- Login banner and console/aux line passwords.

#### G. Switch ports and VLANs

- **VLAN 1:** whether access ports, the management SVI, or trunk native VLANs still use VLAN 1. NSA
  hardening guidance advises reassigning the native VLAN and not using the default VLAN for user traffic.
- **Unused ports:** shut down, or placed in an unused, non-routed VLAN. Enabled unused ports in a
  trusted VLAN let anyone who plugs in join that network (wall jacks, outdoor cameras' cable runs).
- Trunks: allowed VLAN lists restricted to what's needed; dynamic trunk negotiation (DTP) off on access
  ports (`switchport mode access`, `switchport nonegotiate`).
- Ports feeding APs or other switches: the right VLANs tagged, and guest/IoT VLANs not accidentally
  bridged into the main VLAN.
- Layer-2 protections where supported and appropriate: port security, DHCP snooping (stops rogue DHCP),
  BPDU guard on edge ports, storm control. Note these as hardening, not baseline.
- PoE ports feeding outdoor devices: an attacker who unplugs an outdoor camera gets that port's VLAN.

#### H. Configuration backup and change tracking

- Mesh systems: whether the vendor offers any backup (many don't; settings live in the cloud account).
  Record the settings the user would need to rebuild (SSIDs, modes, reservations, forwards).
- Controllers: automatic backups on, where they are stored, and who can read them (they contain
  secrets).
- Switches: a current off-box copy of the startup configuration, when it was last taken, whether the
  running and startup configurations match (unsaved changes are lost on reboot), and whether a config
  archive or change log exists.

#### I. Logging, monitoring, and time

- Remote syslog from switches and controllers; NTP configured (time is needed to correlate logs).
- Mesh app activity or notification history: new-device alerts, admin changes, firmware events.
- Rogue-AP or new-client alerts where the product offers them.

#### J. Physical and availability

- Physical access to mesh nodes and switches: reset buttons (a reset returns the device to setup mode,
  often with an open or label-default network), console ports, and exposed Ethernet jacks.
- Where the switch lives (closet, desk, outdoors), and power protection.
- What fails if the primary mesh node or core switch fails.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Clients that can't do WPA3 or PMF:** older IoT devices, printers, game consoles, cameras, and some
  smart plugs. List them before any security-mode change; they may need a separate legacy SSID.
- **The management path:** the phone or laptop the user (and the agent) uses for the app, controller, or
  switch session. Changing the SSID, mode, or management VLAN can cut it off.
- **DHCP reservations and port forwards on the mesh:** moving to bridge mode discards them; they must be
  recreated on the firewall first.
- **Devices pinned to a VLAN or port:** cameras, NAS, APs, the uplink to the firewall. Changing a port's
  VLAN or a trunk's allowed list can isolate a whole segment.
- **Monitoring that uses SNMP or Telnet/HTTP:** switching to SNMPv3 or turning off Telnet breaks pollers
  and scripts until they are updated.
- **Smart-home integrations** that depend on the mesh account or UPnP.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Open, WEP, or TKIP SSID | Move to WPA2 (AES) at minimum, preferably WPA3 or transition mode. | Clients rejoin with the passphrase; very old devices may not connect at all. |
| WPA2-only where WPA3 is available | Enable WPA3 transition mode; later move capable SSIDs to WPA3-only with PMF required. | Some legacy clients fail even in transition mode; the network may restart when toggled. |
| PMF off or optional | Set PMF required on WPA3-only SSIDs; keep optional only where WPA2 clients must stay. | WPA2 clients without PMF support are dropped when PMF is required. |
| WPS enabled | Turn WPS off (especially the PIN method); verify it is really off. | Devices that pair with the WPS button must use the passphrase. |
| Weak or label-default passphrase | Change to a long random passphrase; share it with a QR code. | Every device must rejoin; plan a time and list headless devices. |
| No guest isolation | Put guests on a guest network isolated from the LAN. | Guests lose access to casting and printing unless explicitly allowed. |
| IoT on the main network | Move IoT to its own SSID on a separate VLAN/subnet with firewall rules. | Discovery-dependent features (casting, local control) may need mDNS reflection or rules. |
| Mesh routing behind a firewall (double NAT) | Put the mesh in bridge/AP mode so the firewall does NAT, DHCP, and policy. | Mesh port forwards, reservations, and some features (often guest network) are lost; recreate them on the firewall first. |
| UPnP on the mesh | Disable it, or leave it only where a named device needs it and nothing better exists. | Consoles and some apps lose automatic port mapping. |
| Remote web management on the mesh | Turn it off; manage through the vendor app or VPN. | Remote admin works only via the app or VPN. |
| No MFA on the vendor account | Enable MFA on the vendor account (and its parent platform account). Review shared admins. | The user needs an authenticator or second factor; record recovery codes offline. |
| Mesh or switch past end of support | Plan replacement with a supported model; until then, keep its management off untrusted segments. | Cost; a migration window. Re-adding devices to a new mesh takes time. |
| Telnet or HTTP management on the switch | Enable SSH v2 and HTTPS (or no web UI); then disable Telnet and HTTP. | Scripts and tools using Telnet/HTTP break; test SSH before disabling Telnet. |
| SNMPv1/v2c communities, especially read-write | Remove read-write communities; move to SNMPv3 authPriv with an ACL, or disable SNMP. | Pollers need SNMPv3 credentials. |
| Smart Install listening | Disable with `no vstack` where supported; otherwise block TCP 4786 with an ACL. | Zero-touch provisioning stops (rarely used in homelabs). |
| Management on VLAN 1 or reachable from IoT/guest | Move management to a dedicated VLAN; restrict vty access by ACL. | C2 change; a wrong step locks you out of the switch. Keep the console cable handy. |
| Unused ports enabled | Shut them down or put them in an unused, non-routed VLAN. | Plugging something in later needs a config change. |
| Access ports negotiating trunks | Set access mode and disable negotiation. | None for ordinary end devices. |
| No switch config backup | Take an off-box copy of the startup config after every change; encrypt or restrict it. | The copy holds secrets; protect it. |
| Unsaved switch changes | Review the running vs. startup diff with the user, then save if intended. | Saving makes unknown changes permanent; review first. |

Hiding SSIDs, MAC filtering, and reducing transmit power are not security controls. Never recommend them
as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (open or WEP Wi-Fi, WPS PIN, management
reachable from the internet or guest Wi-Fi, read-write SNMP) → high-priority hardening (WPA3, isolation,
bridge mode, MFA, legacy switch protocols) → routine maintenance (firmware, backups) → optional defense in
depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Wi-Fi and switch specifics:

- **Before any change:** record the current settings (screenshots of the app or controller pages; for
  switches, an off-box copy of the running and startup configs). Confirm a fallback management path: a
  wired client, the app over cellular, or a console cable for the switch.
- **Use the vendor app, controller, or documented CLI.** Don't use unofficial tools, sideloaded
  firmware, or third-party firmware (for example open-source router firmware) as a remediation step
  unless the user explicitly chooses it as a separate project.
- **Wi-Fi mode and passphrase changes:** do them with the user present, at a time when a short outage is
  acceptable. Change one SSID at a time. Have the list of headless and legacy devices ready to rejoin.
- **Bridge mode migration:** recreate DHCP reservations, port forwards (only the ones still needed), and
  guest/IoT segmentation on the firewall first, then switch the mesh to bridge mode, then confirm
  clients get firewall-issued addresses. The vendor may require a wired backhaul to the primary node.
- **Firmware:** use the vendor's update path; on a switch, verify the image checksum against the
  vendor's published value, confirm there is room on flash, and keep the old image until the new one is
  proven. Updates and reloads are C2.
- **Switch management changes:** keep the current session open; enable and test the new method (SSH,
  management ACL, new management VLAN) from a second session before removing the old one. On Cisco IOS,
  `reload in <minutes>` before a risky change, cancelled with `reload cancel` once access is confirmed, is
  a vendor-documented safety net; use it only with approval, because it reboots the switch if you forget
  to cancel.
- **Save deliberately.** On switches, a change in the running config is lost on reboot until saved.
  Save only after the change is verified, and take a new off-box backup afterwards.
- **If you lose access:** use the console port (switch) or a wired client / physical access (mesh).
  A factory reset is the last resort and is the user's decision, not the agent's.

After each change, follow the core "after a change" steps: re-read the setting, confirm clients
reconnected (including legacy and headless devices), check internet access, DHCP, DNS, inter-VLAN rules,
and the management path, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- `write erase`, `erase startup-config`, factory reset buttons or app "reset network" actions, or
  deleting a mesh network from the vendor account, as security remediation.
- Reloading a switch, or rebooting the primary mesh node, without the user's explicit go-ahead and a
  console or physical fallback.
- Changing the management VLAN, vty ACLs, or AAA settings of the switch the agent is connected through,
  without console access confirmed and the user present.
- Formatting or deleting flash, or changing boot variables, on a switch.
- Loading firmware from any source other than the vendor, or third-party firmware.
- Testing default credentials, guessing passwords, brute-forcing WPS, or probing SNMP communities.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the mesh- and
switch-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### WIFI-001: Mesh in router mode behind the firewall, with UPnP on and a WPS-enabled guest SSID

**Confidence:** Confirmed
**Priority:** P2. Wi-Fi clients sit behind a second NAT the firewall can't see into, the mesh's UPnP lets
any Wi-Fi client open inbound mappings on the mesh, and WPS PIN lets anyone in radio range recover the
guest passphrase. No internet-facing exposure was observed at the firewall.
**State:** Open
**Component:** App-managed mesh system, primary node in router mode, current vendor firmware
**Evidence:** Observed 2026-01-20, user-provided app screenshots: operating mode "router"; WAN address
`192.0.2.20` assigned by the upstream firewall; LAN `198.51.100.0/24` with DHCP on the mesh; UPnP on;
guest SSID with WPS (PIN) enabled. The upstream firewall's DHCP leases show only one host (the mesh) for
the Wi-Fi clients.
**Expected secure state:** one routing/NAT device that applies firewall policy to every client; UPnP off
unless a named device needs it; WPS off (CERT VU#723755).
**Exposure and prerequisites:** WPS: anyone in radio range. UPnP: any Wi-Fi client, including IoT
devices, can create mappings on the mesh; the firewall still limits what reaches the mesh's WAN side.
**Dependencies / blast radius:** two port forwards and five DHCP reservations exist on the mesh; a game
console uses UPnP; the user manages the mesh from a phone on Wi-Fi.
**Recommended remediation:** (1) turn WPS off on the guest SSID and verify; (2) recreate the needed
reservations and forwards on the firewall, create guest and IoT VLANs there, then switch the mesh to
bridge mode; (3) leave UPnP off on the mesh and, if the console needs it, decide on the firewall.
**Operation class:** (1) C1; (2) C2, Wi-Fi outage of a few minutes and features lost in bridge mode.
**Approval required:** Yes.
**Verification:** WPS shows off and a client survey no longer shows WPS in the guest beacon; Wi-Fi
clients get addresses from the firewall; the firewall lists individual Wi-Fi clients; the console still
works online.
**Rollback:** switch the mesh back to router mode in the app (settings recorded beforehand).

---

## Version history

- **1.0** (2026-10-30): Initial version.
