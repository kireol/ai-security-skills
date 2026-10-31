---
name: out-of-band-management
description: >-
  Security assessment, hardening, remediation, and incident response for out-of-band management
  controllers: server BMCs (Dell iDRAC, HPE iLO, Supermicro IPMI/BMC, Lenovo XCC, AMI MegaRAC and OpenBMC
  boards, generic IPMI and Redfish) and Intel AMT/vPro on PCs. Use when auditing a server's or PC's
  management controller, reviewing BMC accounts, default credentials, IPMI over LAN (RAKP hash disclosure,
  cipher 0), Redfish API accounts, virtual console and virtual media, management-network placement,
  firmware support status on old hardware, or AMT provisioning and MEBx settings, or when a BMC or AMT
  controller may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Dell iDRAC 7-10, HPE iLO 4-7, Supermicro BMCs, other IPMI 2.0 and Redfish BMCs, Intel AMT/vPro (verify the live firmware; features and defaults vary by generation)"
  audience: "home, work, homelab"
  finding_prefix: "OOB"
  modes: "discover, recommend, remediate, respond"
---

# Out-of-Band Management Security

Act as a careful, evidence-driven hardware-management security engineer. A management controller is a
small computer inside the server or PC that runs whenever the machine has power, even when it is "off".
Whoever controls it can power the machine on and off, watch and type on its console, boot it from an
attacker-supplied disk image, change firmware and BIOS settings, and often read or reset the host's
storage controller. It sits below the operating system, so host security tools can't see it, and it is
usually the oldest, least-patched software in a homelab. Identify, explain, prioritize, remediate (only
when authorized), and verify weaknesses in these controllers, their accounts, their network placement,
and their firmware.

## How to use this skill

This skill holds only out-of-band-management-specific guidance. It builds on the shared core, which always
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

Out-of-band-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and advisories are in [references.md](references.md).

Related skills: the host on top of the controller is assessed with its own skill, for example
[Proxmox VE](../../virtualization/proxmox-ve/SKILL.md) (which has a short BMC section; this skill is the
full version), [VMware ESXi](../../virtualization/vmware-esxi/SKILL.md),
[Linux](../../operating-systems/linux/SKILL.md), or [Windows](../../operating-systems/windows/SKILL.md).
The UPS that powers the server is covered by [UPS](../ups/SKILL.md).

## Out-of-band-specific principles

- **The controller is the host's root of trust, so rate it like the host.** A BMC finding on a server that
  runs the network's firewall, NAS, or hypervisor is a finding against all of them. A BMC compromise
  survives operating-system reinstalls and disk replacement.
- **Never test logins.** Don't try default or guessed credentials, don't run IPMI hash-retrieval or
  cipher-0 tools, and don't brute-force anything, even "just to confirm". Many BMCs lock accounts or
  crash under unexpected traffic, and a failed BMC can need physical recovery. Ask the user, read the
  configuration with credentials they provide, or read it in-band from the host.
- **IPMI 2.0 has flaws that can't be patched.** By design (the RAKP exchange), a BMC that speaks IPMI over
  LAN gives anyone who can reach UDP 623 a salted hash of any valid user's password, which can be cracked
  offline. Cipher suite 0 and anonymous or null users, where enabled, allow login without a valid
  password. Strong passwords and firmware updates don't fix RAKP; only network isolation or disabling IPMI
  over LAN does.
- **The host can usually reach the BMC without a password.** Host root (or Windows administrator) can talk
  to the BMC in-band (the KCS or SSIF system interface, or a host-interface virtual NIC such as Redfish Host
  Interface, Dell OS-to-iDRAC Pass-through, or HPE Virtual NIC) and, on many platforms, create users or
  reset passwords. So host compromise often means BMC compromise. Newer platforms can require
  authentication for host access; check whether it is on.
- **Old hardware is normal here, and its controllers are often past end of support.** Homelabs run
  servers retired from data centers. Their BMC firmware may get no more security fixes, may need old TLS
  and Java to use, and may never get a fix for a published flaw. Treat end-of-support firmware as
  unsupported (core triage) and weigh isolation more heavily than patching.
- **Firmware updates on a BMC are risky.** An interrupted or wrong-image update can leave the controller
  (and sometimes the server) unbootable. Treat every BMC or AMT firmware update as **C2**, or **C3** where
  the vendor documents no rollback, and follow only the vendor's procedure for the exact model.
- **Intel AMT is a BMC inside a PC.** On vPro PCs, Intel AMT gives the same powers (power control,
  KVM, storage redirection) over the network, sharing the PC's own network port and MAC address, so it
  is easy to forget it is there.

## Deployment variants

Identify the variant in Discover. It changes which checks apply.

| Variant | How to recognize it | What changes |
|---|---|---|
| **Dell iDRAC** (iDRAC 7/8 on 12th/13th generation, iDRAC9 on 14th-16th, iDRAC10 on 17th; verify) | Web UI titled iDRAC; Dell OUI; `racadm` available; service tag on the system label. | Generation decides support status and features. Newer servers ship with a unique default password on the label; older ones used a well-known default. Check the license tier (Express/Enterprise/Datacenter), which gates the virtual console and some security features. System Lockdown mode is available on iDRAC9 and later. |
| **HPE iLO** (iLO 4 on Gen8/Gen9, iLO 5 on Gen10, iLO 6 on Gen11, iLO 7 on Gen12; verify) | Web UI titled iLO; HPE OUI; a pull-out tag with the factory password. | iLO 4 and older are past or near end of support; verify on HPE's site. iLO 5 and later have a security dashboard and security states (Production, High Security, FIPS, CNSA) that change which ciphers and interfaces work. The Advanced license gates the remote console on some generations. |
| **Supermicro BMC** | Web UI from Supermicro (older boards show an ATEN-based UI); Super Micro Computer OUI; `ipmicfg` or SMCIPMITool used. | Boards shipped from about 2020 have a unique password on a label; older boards used a well-known default. Older X9/X10-era boards are likely past support; verify. Some boards default the management interface to failover (dedicated or shared) mode. |
| **Other IPMI/Redfish BMCs** (Lenovo XCC/IMM, ASRock Rack, Gigabyte, Tyan, white-box AMI MegaRAC, OpenBMC) | Vendor web UI; `/redfish/v1` answers; vendor OUI. | Firmware often comes from a BMC-stack supplier (AMI, Insyde, Aspeed SDK), so a supplier advisory can apply across brands; check the board vendor's advisory, not just the supplier's. |
| **Intel AMT / vPro** (business PCs, some workstations and mini PCs) | Intel vPro sticker or spec sheet; Intel MEI device in the OS; Intel CSME firmware; AMT ports answer when provisioned. | Check provisioning state (unprovisioned, Client Control Mode, Admin Control Mode), the MEBx password, user-consent setting, and whether KVM and storage redirection are enabled. Intel Standard Manageability is a reduced feature set with the same network exposure. |
| **Shared vs. dedicated management port** | BMC NIC setting: dedicated, shared (NC-SI/LOM), or failover. | In shared mode the BMC sits on whatever network the host's first port is on, often the main LAN or a guest VLAN, unless a management VLAN is tagged. Failover mode can silently move the BMC onto the host network if the dedicated cable is unplugged. |
| **Server without a BMC** (desktop-class hardware, PiKVM or other IP-KVM added) | No BMC; a separate KVM-over-IP device or smart plug provides remote control. | An IP-KVM is the same risk class: console, keyboard, virtual media, sometimes power. Assess it with the same domains (accounts, network placement, firmware). |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match. Detection means recording
what already answered in an approved inventory; don't send IPMI or AMT requests beyond that.

- **IPMI over LAN:** UDP 623 (RMCP/RMCP+). An answer from a host on a user or guest network is itself a
  finding to raise with the user.
- **Web UI and Redfish:** HTTPS 443 (often HTTP 80 redirecting to it) with a page title or self-signed
  certificate naming iDRAC, iLO, Supermicro, MegaRAC, XClarity Controller, or OpenBMC. Redfish answers at
  `/redfish/v1` on the same port; the service root (readable without credentials on many BMCs) names the
  vendor and Redfish version.
- **Console and media ports** (vendor defaults; verify against the vendor's port table for the
  generation): iDRAC virtual console and VNC on TCP 5900/5901; iLO remote console and virtual media on
  TCP 17990 and 17988; Supermicro iKVM on TCP 5900 with virtual media on separate vendor ports. SSH on 22
  and, on old firmware, Telnet on 23 may also answer. SNMP on UDP 161 may report the BMC model in
  `sysDescr`.
- **Intel AMT:** TCP 16992 (HTTP, WS-Management) and 16993 (HTTPS), 16994 and 16995 (redirection for
  serial-over-LAN, storage redirection, and KVM; 16995 over TLS), and RMCP on UDP 623/664. Intel has
  deprecated the non-TLS ports, and newer platforms refuse remote connections to them (verify for the
  platform's CSME version). AMT answers on the PC's own address and MAC, so the host and its AMT look like
  one device.
- **Discovery announcements:** some BMCs answer SSDP or Redfish SSDP discovery, and HPE iLO can be found by
  HPE's discovery tools. Many send nothing unsolicited.
- **MAC address vendors (OUIs):** Dell, Hewlett Packard Enterprise (older units Hewlett Packard), Super
  Micro Computer, Lenovo, ASRockRack/ASRock, Gigabyte, Quanta, Inventec, Tyan/MiTAC, or the BMC chip maker
  (ASPEED). BMCs usually have their own MAC, often one higher or lower than the host's first NIC. Intel AMT
  uses the host's Intel NIC MAC, so it shows Intel or the PC maker.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer, in order: the user reading screens in the BMC web UI; a dedicated **read-only** account the user
creates for the assessment (Redfish role `ReadOnly`, iDRAC Read Only, iLO Login-only, IPMI `USER`
privilege); in-band reads from the host operating system with the user's approval. Never use the BMC's
administrator account for discovery if a read-only one can be made.

Candidate commands. Lines marked *vendor-documented* appear in the vendor's or tool's documentation; the
rest are **not yet verified** on every BMC. Check each tool exists first (`command -v`), and run in-band
commands on the host only with the user's approval, since they need root.

```sh
# In-band from the host (needs root; reads the local BMC through the system interface)
ipmitool mc info                      # BMC firmware version and IPMI version (ipmitool man page)
ipmitool lan print 1                  # IP source, address, VLAN, auth types, cipher suite privileges (channel may differ)
ipmitool user list 1                  # user IDs, names, enabled state, privilege per channel
ipmitool channel getaccess 1          # per-user channel access
ipmitool sol info 1                   # serial-over-LAN state
ipmitool sel elist                    # system event log (read; never clear it)
dmidecode -t 38                       # IPMI device information, if the platform reports it

# Redfish, read-only GETs with a read-only account (DMTF Redfish standard; paths vary slightly by vendor)
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/Managers
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/Managers/<id>/NetworkProtocol
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/AccountService
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/AccountService/Accounts
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/UpdateService/FirmwareInventory
curl -sk -u <readonly-user> https://<bmc-host>/redfish/v1/SessionService/Sessions

# Vendor tools (read-only subcommands; vendor-documented)
racadm getversion; racadm get iDRAC.Users; racadm get iDRAC.IPMILan; racadm getsel   # Dell
ilorest serverinfo; ilorest list --selector=AccountService.                           # HPE
```

- `curl -u <user>` prompts for the password; never put it on the command line or in evidence. `-k` is
  needed for self-signed BMC certificates; record that the certificate is self-signed as evidence.
- Some old BMCs crash or slow down under rapid API calls. Make one request at a time.
- For Intel AMT, see domain I.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, platform, and support status

- Every controller in scope: server or PC model, controller type and generation, firmware version, BIOS
  version, license tier, and who manages it. Include IP-KVM devices that serve the same purpose.
- Vendor support status of the **controller firmware and the server platform** (end of sale, end of
  support, last firmware release). Record the source page and date. Old generations may be past support
  even when the server works fine.
- Installed firmware vs. the vendor's latest for that model and vendor security advisories (core: triage).
  Also check BMC-stack supplier advisories that the board vendor has confirmed apply.
- BIOS/UEFI firmware version and advisories; BMC and BIOS fixes are often released together.

#### B. Accounts and authentication

- Every local account: name, enabled, privilege (Administrator/Operator/User or role), which interfaces it
  may use (web, Redfish, IPMI, SSH, serial). Look for the vendor's built-in admin, extra admins, disabled
  but present accounts, and accounts nobody can explain.
- **Default credentials:** ask whether the factory credential (well-known default on older hardware, or
  the unique password printed on the label on newer hardware) is still in use. A label password is still a
  default: anyone who sees the label or the server's paperwork knows it. Dell and HPE can warn when the
  default is unchanged; check whether that warning is showing. Never confirm by trying it.
- **Anonymous or null users:** IPMI user ID 1 often has an empty name; check it is disabled or has no
  privileges.
- Password reuse: is the BMC password shared with the host, hypervisor, other BMCs, or a password manager
  entry used for many systems? RAKP makes a BMC password crackable offline, so reuse spreads the damage.
- Directory, LDAP, or RADIUS integration if used, and its fallback local account. Two-factor options
  where the firmware supports them.
- Lockout and session-timeout settings; concurrent session limits.
- Redfish and API accounts used by automation (monitoring, Ansible, cluster fencing, hypervisor power
  management): which account, what role, where the credential is stored. Fencing agents often hold
  admin-level BMC credentials on every cluster node.
- SSH keys and certificates uploaded for BMC accounts: existence and age only.

#### C. Network placement and exposure

- Which network the controller is on: dedicated management VLAN, the main LAN, a server VLAN shared with
  guests, or the internet. Dedicated vs. shared vs. failover NIC mode, and the VLAN tag if any.
- Who can reach it: user devices, IoT and guest networks, VMs and containers on the same host, VPN users.
  A BMC reachable from the guests it manages lets a compromised guest attack its own host's controller.
- **Never exposed to the internet**, including by router port forwards, UPnP, DMZ, or a reverse proxy.
  Check the router, not just the BMC. Record any exposure as at least P1.
- IPv6: whether the BMC has SLAAC or link-local addresses that bypass IPv4-only firewall rules.
- Host-to-BMC paths: host interface (Redfish Host Interface, OS-to-iDRAC Pass-through, HPE Virtual NIC),
  and whether host access requires authentication (for example the iLO "require host authentication"
  setting; verify the name on the generation).
- The BMC's own IP allow-list or firewall, if the firmware has one (iDRAC IP range filter, iLO and
  Supermicro IP access control).

#### D. Services and protocols

- IPMI over LAN: enabled? Needed? If enabled, which cipher suites are allowed (cipher 0 must not be), the
  maximum privilege per cipher suite, and which authentication types are on (none, MD2, MD5, password
  should all be off for IPMI 1.5 paths).
- Web UI: HTTP redirect to HTTPS, minimum TLS version and ciphers, certificate (self-signed default,
  expiry, hostname). Old firmware may support only TLS 1.0/1.1 or weak ciphers.
- SSH, Telnet (must be off), SNMP (version, communities; v1/v2c communities should not be defaults, v3
  preferred), serial-over-LAN, Redfish, legacy remote-command protocols (such as iDRAC remote RACADM),
  and vendor discovery protocols. Disable what nobody uses.
- Alerts: SNMP traps, email, and Redfish event subscriptions: where they go, and whether any destination
  is unknown.

#### E. Virtual console, virtual media, and remote power

- Who can open the virtual console (KVM) and attach virtual media. Virtual media lets a user boot the
  server from any image they supply, which bypasses the host's disk encryption prompts and boot security
  unless Secure Boot and a BIOS password stop it.
- Console plug-in type: HTML5 (preferred) or Java/ActiveX. Old Java consoles push users to run old Java
  with security checks disabled on their workstation; that is a workstation finding too.
- Console locking or "local display off" settings and whether the console session is visible to someone
  at the physical screen.
- Remote file share or virtual media mounted at the moment (an unexplained mounted image is a P0 lead).
- Power control, boot-order override, and BIOS settings changes over the BMC: which roles can do them.

#### F. Firmware integrity and update path

- Root-of-trust and firmware-verification features where the hardware has them (Dell Silicon Root of Trust
  and System Lockdown, HPE Silicon Root of Trust and runtime firmware verification, Supermicro hardware
  root of trust on newer boards): enabled and reporting good?
- How firmware is obtained: vendor download, vendor update tool, or a third-party "unlocked" or modified
  firmware (a supply-chain risk to note).
- Who can upload firmware (which roles), and whether downgrades are allowed.
- BIOS/UEFI: Secure Boot state, BIOS setup password, boot-order lock, and whether the BMC can change them.

#### G. Logging, time, and monitoring

- System Event Log (SEL) and the vendor's audit log (Dell Lifecycle Log, HPE iLO Event Log and Integrated
  Management Log, Supermicro maintenance and event logs): enabled, retention, last review.
- Remote syslog where the firmware supports it, so an attacker can't erase every record.
- NTP configured and correct, so BMC events line up with host and network logs.
- Alerts for login failures, new users, firmware changes, and chassis intrusion where available.
- Whether anything monitors the BMC at all (see [Monitoring](../../monitoring/monitoring/SKILL.md)).

#### H. Physical access and recovery

- Physical access to the server: rack locks, chassis intrusion switch, front USB ports, the BMC's own USB
  management port where present (some servers offer direct BMC access over a front USB port), and the
  security-override or password-reset jumpers.
- Where the factory password label and the BMC recovery credentials are kept.
- How the user regains control if a BMC change locks them out (physical console, jumper reset, vendor
  recovery), and whether that has been tested.

#### I. Intel AMT / vPro

Ask the user, and read from the PC itself; don't connect to AMT over the network unless the user provides
credentials and approves.

- Is the PC vPro-capable, and is AMT **provisioned**? Unprovisioned AMT has no network listener, but a
  local administrator (or malware with admin rights) can provision it in Client Control Mode from the
  operating system. Record who is expected to manage AMT, if anyone.
- Provisioning mode: Client Control Mode (KVM and some actions need user consent) or Admin Control Mode
  (no user consent needed unless configured). User-consent setting for KVM and redirection.
- MEBx (the AMT setup screen at boot): has the default MEBx password been changed? Is MEBx access
  protected by the BIOS password? Can AMT be enabled or provisioned locally without it (USB key
  provisioning)?
- Enabled features: KVM, serial-over-LAN, storage redirection, remote power. TLS required or plain HTTP
  allowed. Network access: wired only, or also Wi-Fi.
- CSME/AMT firmware version vs. Intel and PC-vendor advisories. Intel's CSME version detection tool, the
  Intel Management and Security Status app on Windows, or `rpc amtinfo` from Intel's Open AMT Cloud
  Toolkit can report it (vendor-documented; verify on the platform). Fixes ship as PC-vendor BIOS/firmware
  updates.
- If AMT is unused: is it disabled in BIOS or MEBx (on some PCs it can only be unprovisioned, not removed)?
- Management software: which console manages AMT (Intel EMA, MeshCentral, a vendor tool), and that
  console's own exposure and accounts. Intel has retired several of its older AMT tools (Intel SCS is end
  of life); check Intel's current support page for what is still supported.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the controller's current state. Common hidden
dependencies:

- **Cluster fencing and power management:** Proxmox VE HA fencing, Pacemaker, OpenStack Ironic, MAAS, and
  similar tools use IPMI or Redfish credentials to power-cycle nodes. Changing the password, disabling IPMI
  over LAN, or moving the BMC to another network breaks fencing, which can stop failover.
- **Monitoring:** Prometheus IPMI or Redfish exporters, vendor management consoles (OpenManage, OneView,
  HPE GreenLake/Compute Ops, Supermicro SSM), and SNMP pollers.
- **The user's only way back in:** if the hypervisor, firewall, or VPN runs on this server, the BMC may be
  the only remote recovery path. Don't remove it before another path exists.
- **Automation and provisioning:** PXE and virtual-media workflows, Ansible or Terraform BMC modules,
  scripts that use `ipmitool -H` with a password.
- **Console clients:** old Java-based consoles may stop working after TLS hardening.
- **Intel AMT:** a management console or MSP tool that relies on AMT for remote support.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Network placement | Move BMCs to a dedicated management VLAN reachable only from an admin workstation or jump host (or a VPN into that VLAN). Set the NIC to dedicated mode, not failover. | Tools that reach the BMC from other networks lose access; set up the admin path first. |
| Internet exposure | Remove every port forward, UPnP mapping, or proxy route to the BMC; use a VPN. | Remote recovery needs the VPN to work when the server is down; host the VPN elsewhere. |
| Default or label password | Create and **test** a named admin with a unique password, then change or disable the built-in admin. Store the credential in a password manager. | Fencing, monitoring, and scripts using the old credential break; update them in the same window. |
| IPMI over LAN | Disable if unused. If needed (fencing), restrict it to the management network, disable cipher 0 and weak suites, disable null and anonymous users, and use a unique password per BMC. | RAKP hash disclosure remains while IPMI over LAN is on; isolation is the only mitigation. Prefer Redfish over HTTPS for automation where supported. |
| Unused services | Disable Telnet, unused SSH, SNMP v1/v2c with default communities, serial-over-LAN, and remote-command interfaces nobody uses. | Some vendor tools need a specific service; check before disabling. |
| Least privilege | Read-only roles for monitoring; operator role for power-only automation; admin only for people. | Some tools request admin by default; test with the lower role. |
| Host-to-BMC path | Disable the host interface if unused, or require host authentication where the firmware supports it. | Some vendor OS agents and update tools use it. |
| Firmware | Plan an update to the vendor's latest for the model, with the vendor procedure and a maintenance window. If the platform is past support, plan for isolation and eventual replacement. | Update risk (see Remediate); old firmware may need stepping-stone versions. |
| Virtual media and console | Limit to admins; enable BIOS password and Secure Boot so virtual media can't silently boot another OS. | Admins must enter the BIOS password for legitimate rescue boots. |
| Logging | Enable remote syslog and NTP; set alerts for logins and user changes. | Needs a log receiver; check the BMC can reach it on the management network. |
| Intel AMT unused | Unprovision and disable AMT in BIOS/MEBx; set a strong MEBx password and a BIOS password either way. | Removes remote-support capability an MSP or employer may rely on; confirm first. |
| Intel AMT used | Admin Control Mode only if needed; require user consent for KVM where practical; TLS only; update CSME firmware; restrict the management console. | User consent adds friction for remote support. |

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Out-of-band specifics:

- **Keep a way back in.** Before changing BMC network settings, accounts, TLS, or IP filters, confirm
  physical console access or another tested path. A BMC that drops off the network can need someone at the
  server to recover it.
- **Accounts:** create and test the new admin in a second browser session before changing or disabling the
  old one. Never disable the only administrator. Update fencing and monitoring credentials in the same
  window and test them (for example, a read-only power-status query).
- **Network moves (C2):** changing the BMC's IP, VLAN, or NIC mode drops the current session. Set the new
  switch port or VLAN first, change the BMC, then reconnect from the management network. Don't change the
  host's network at the same time.
- **IPMI over LAN and cipher suites (C2 if fencing uses them):** change one setting, then confirm the tools
  that need IPMI still work.
- **TLS and certificates:** check that the BMC firmware supports the new certificate type and key size
  before uploading; some old BMCs reject modern keys or become unreachable over HTTPS until reset.
- **Firmware (C2, or C3 where no rollback is documented):** use only the vendor's image and procedure for
  the exact model and current version, from the vendor's site or official update tool. Confirm the
  required intermediate versions, a stable power supply (UPS-backed), and a maintenance window. Don't
  interrupt an update, don't update BMC and BIOS at the same time unless the vendor bundles them, and
  don't reboot the host mid-update. Never use third-party or modified firmware as security remediation.
  This skill doesn't give step-by-step flashing instructions; follow the vendor's.
- **Intel AMT:** unprovisioning or disabling AMT is **C2** when anyone relies on it. CSME updates ship as
  PC-vendor BIOS/firmware packages; follow the PC vendor's procedure.

After each change, follow the core "after a change" steps and re-run the affected Discover checks
(account list, `lan print`, Redfish `NetworkProtocol`, reachability from a non-management network).

### Hard stops (refer to a specialist; never automate)

- Never try default, guessed, or leaked credentials, run IPMI hash-dumping, cipher-0, or brute-force tools,
  or exploit a known BMC vulnerability "to prove it", even with permission to scan.
- Never reset a BMC to factory defaults as security remediation without the user's fresh approval: it can
  wipe network settings (dropping it off the network), licenses, and logs needed as evidence.
- Never cross-flash firmware from another model, force a downgrade, or flash during a power warning.
- Never use the BMC to change storage-controller (RAID) configuration, clear foreign disks, or initialize
  virtual disks. Those are storage operations and are out of scope.
- Never clear the SEL or audit logs.
- If a firmware update fails or the BMC stops responding, stop and follow the vendor's recovery procedure
  or contact vendor support; don't retry with other images.

---

## Respond

On any P0 indicator (unknown BMC accounts, unexplained virtual media or console sessions, firmware that
doesn't match what the user installed, power events nobody caused, or a BMC that was exposed to the
internet with weak credentials), switch to Respond immediately. Follow the core playbook plus the
out-of-band-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### OOB-001: Server BMC on the main LAN with IPMI over LAN enabled and the label password unchanged

**Confidence:** Confirmed
**Priority:** P2. Any device on the LAN, including a compromised IoT device or a guest VM on the same
server, can request the admin password's RAKP hash over UDP 623 and crack it offline, then control the
server below its operating system. Not internet-exposed, so not P1.
**State:** Open
**Component:** BMC of a rack server running the household hypervisor; firmware two years old; vendor
support for the generation ends next year (vendor lifecycle page, retrieved 2026-10-31).
**Evidence:** Observed 2026-10-31 in-band on the host with the user's approval: `ipmitool lan print 1`
shows a static address `192.0.2.40` (same subnet as user devices), no VLAN, IPMI over LAN enabled,
cipher suites 3 and 17 at admin privilege, cipher 0 at no access. `ipmitool user list 1` shows the
built-in admin enabled. User-reported: the password is still the one on the label. UDP 623 answered from
the user VLAN in the approved inventory scan.
**Expected secure state:** BMC on a dedicated management network, IPMI over LAN disabled or restricted
to that network, unique admin password, unused services off (vendor security configuration guide; CISA/NSA
BMC hardening guidance).
**Exposure and prerequisites:** any host on `192.0.2.0/24`. No credentials needed to obtain the hash.
**Dependencies / blast radius:** the hypervisor cluster's fencing agent uses IPMI with the built-in admin
account; a monitoring exporter polls sensors over IPMI.
**Recommended remediation:** (1) create a named admin and an operator-role account for fencing, each
with a unique password, and update the fencing configuration; (2) move the BMC to the management VLAN in
dedicated NIC mode; (3) restrict IPMI over LAN to that VLAN, or replace it with Redfish fencing; (4) plan a
firmware update and record the end-of-support date.
**Operation class:** C2 (BMC network change drops the session; fencing must be retested).
**Approval required:** Yes. Disruptive to fencing and monitoring.
**Verification:** UDP 623 and HTTPS no longer answer from the user VLAN; the fencing agent's power-status
query succeeds with the new operator account; the admin account list matches the approved list.
**Rollback:** restore the captured network settings from the physical console; restore the fencing
configuration from the captured copy.

---

## Version history

- **1.0** (2026-10-31): Initial version.
