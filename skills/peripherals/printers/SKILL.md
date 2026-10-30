---
name: printers
description: >-
  Security assessment, hardening, remediation, and incident response for network printers and
  multifunction printers (MFPs): home inkjets and lasers and small-office MFPs from HP, Brother, Canon,
  Epson, Xerox, Lexmark, and similar vendors. Use when auditing a printer's firmware and vendor support,
  embedded web server (EWS) admin password, exposed print and management services (raw 9100, IPP/IPPS,
  LPD, SNMP, FTP/Telnet, Wi-Fi Direct), cloud printing accounts, scan-to-email/SMB/FTP and LDAP stored
  credentials, stored jobs and internal storage at disposal, internet exposure, network placement, or
  logging, or when a printer may have been compromised or used as a pivot.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Networked single-function printers and MFPs from any vendor, home through small office (verify each model's current firmware, support status, and menu names)"
  audience: "home, work, homelab"
  finding_prefix: "PRN"
  modes: "discover, recommend, remediate, respond"
---

# Network Printer and MFP Security

Act as a careful, evidence-driven security engineer for printers and multifunction printers. A network
printer is an embedded computer with a web server, several network listeners, often Wi-Fi and a second
"direct" access point, and, on MFPs, a store of credentials for other systems (email accounts, file
shares, LDAP directories) and copies of what was printed and scanned. Printers are rarely updated, are
usually on the same flat network as everything else, and are trusted by every computer that prints.
Identify, explain, prioritize, remediate (only when authorized), and verify weaknesses in the printer, the
credentials it holds, what it stores, and what it can reach.

## How to use this skill

This skill holds only printer-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Printer-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md). Network segmentation and Wi-Fi settings are covered
in more depth by [wifi-and-switches](../../network/wifi-and-switches/SKILL.md) and the firewall skills
(for example [opnsense](../../network/opnsense/SKILL.md)).

## Printer-specific principles

- **Never test passwords; ask.** Don't try default, blank, sticker, or serial-number-derived passwords on
  the EWS, SNMP, Wi-Fi Direct, or any other login, and don't use tools that "check" for defaults. Ask the
  user whether the admin password was set and how. Several vendors' factory passwords are derivable from
  data the printer discloses on the network (see the vendor notes), so an unchanged factory password is a
  finding to report from the user's answer, not something to prove.
- **Never print, and never talk to the print engine.** Sending any job, PJL, PostScript, or PCL to
  port 9100, 515, or 631 is not read-only: it wastes paper and toner, can change persistent settings, can
  read or write the printer's file system, and can crash or brick some models. Discovery uses service
  presence (an open port, an mDNS record, an IPP attribute query the user agrees to), never job
  submission.
- **The address book is a password vault for other systems.** Scan-to-email (SMTP), scan-to-folder (SMB),
  scan-to-FTP, and LDAP settings store usernames and passwords for mail accounts, file servers, and
  directories. Anyone with EWS admin access can often read or redirect them. Never export, print, or
  screenshot those entries with secrets visible; record only which systems and which accounts.
- **Stored jobs and internal storage are data.** MFPs keep copies of print, copy, scan, and fax jobs,
  sometimes on a hard drive or flash that survives power-off. Reading them is not read-only in the
  privacy sense. Note what is stored and for how long; never open or download stored jobs.
- **Fragile network stacks.** Aggressive scans, UDP sweeps, OS detection, and vulnerability-scanner
  plugins have long been reported to hang printers or make them print pages of garbage (scanners sending
  probes to port 9100 often get printed as text). Identify printers passively first, then use only light
  TCP connect checks with the user's agreement.
- **Firmware updates have side effects beyond security.** Signed firmware usually blocks downgrades, and
  some vendors use firmware updates to change cartridge-authentication behavior. That is a reason to plan
  updates, read the release notes, and set expectations with the user, not a reason to skip security
  updates.
- **Factory reset and firmware flashing are the user's job.** They erase configuration and can brick the
  device. The agent never performs them, and a reset is not a sanitization method by itself (see
  domain I).

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Home inkjet or laser, app-managed** | Set up through a vendor phone app; a small EWS with few settings; often Wi-Fi only. | Few hardening options; security depends on the EWS password, Wi-Fi Direct, cloud account, and network placement. Some models leave the EWS without a password until one is set. |
| **Cloud-tied home printer** (subscription or "connected" plans, such as HP+ or ink subscriptions) | The printer requires a vendor account and a persistent internet connection to keep working under the plan's terms. | Blocking internet egress may stop the printer or breach the plan's terms; the vendor account becomes part of the security boundary (password, MFA, shared users). Check the plan's terms before recommending egress blocks. |
| **Small-office MFP** (print, copy, scan, fax) | Touch panel, user/department codes, address book, scan-to-folder/email, often an internal drive or large flash. | Stored credentials, stored jobs, LDAP, fax line, and disposal become the main concerns. Many settings exist; vendors publish hardening guides. |
| **Managed or leased MFP** | A dealer or managed-print-service agent reports meter readings; a service account or remote-support tool exists. | The dealer's remote access and service credentials are in scope; changes may need the dealer, and disposal is governed by the lease contract. |
| **Enterprise-class device in a small site** | Enterprise firmware families with signed firmware, runtime integrity features, syslog, and certificate management. | More controls are available; use the vendor's security guide and any fleet tool the user already has. |
| **Printer behind a print server** | Clients print to a Windows, CUPS, or macOS print queue that forwards to the device. | The print server is a separate system (assess it with the OS skill); the printer can then be firewalled to accept jobs only from the server. |
| **USB-attached or shared from a computer** | No network address; shared through the host. | Out of this skill's network scope; the host's printer sharing is covered by the OS skills. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Print service ports (IANA and vendor-documented defaults): TCP 9100 (raw/"AppSocket"/"JetDirect"),
  TCP 631 (IPP, and IPPS on the same port with TLS), TCP 515 (LPD). Many printers also answer on 80/443
  (EWS), 161/UDP (SNMP), and sometimes 21 (FTP), 23 (Telnet), 445 (SMB), or 5357 (WSD). Some Windows
  print servers and computers with printer sharing also answer on 631 or 515.
- mDNS/DNS-SD (Bonjour printing): `_ipp._tcp`, `_ipps._tcp`, `_printer._tcp` (LPD),
  `_pdl-datastream._tcp` (raw socket), `_printer._sub._http._tcp` (the EWS), and on scanners and MFPs
  `_uscan._tcp` / `_uscans._tcp` (eSCL/AirScan; reported widely, not verified for every model). A Mac with
  Printer Sharing also advertises `_ipp._tcp`, so check the TXT record (`ty=`, `product=`) and host.
- WS-Discovery (UDP 3702) and SSDP (UDP 1900) announcements describing a print or scan device.
- SNMP `sysDescr` and the Printer MIB (RFC 3805) commonly name the vendor and model; only query SNMP with
  a community string the user provides (see Discover).
- EWS page titles and headers usually name the vendor and model (for example "HP Embedded Web Server",
  "Brother" Web Based Management, Epson "Web Config", Canon "Remote UI", Xerox "CentreWare"/"Embedded Web
  Server", Lexmark EWS). A self-signed certificate naming the model or vendor is common.
- Wi-Fi: a second SSID beginning with `DIRECT-` (Wi-Fi Direct) near the printer's location.
- MAC vendors (OUI) usually name the printer maker (HP, Brother, Canon, Seiko Epson, Xerox, Lexmark,
  Kyocera, Ricoh, Konica Minolta), but Wi-Fi models may show the Wi-Fi module's maker and rebranded
  devices show the OEM.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Build the inventory from sources that don't touch the printer: DHCP leases, ARP and switch MAC tables,
mDNS/DNS-SD browsing, the print queues on users' computers or the print server, and the printer's own
**configuration or network status page**, which the user prints from the control panel (this prints
locally at the user's request; the agent doesn't send it). Read settings through the EWS with the user
logged in, or from screenshots the user provides, redacting any password fields.

Candidate read-only checks, each **not yet verified** against every model. Run them one printer at a
time with the user's agreement:

```sh
# Passive: what printers are advertising (macOS / Linux with Avahi)
dns-sd -B _ipp._tcp local.            # macOS; also _ipps._tcp, _printer._tcp, _pdl-datastream._tcp, _uscan._tcp
avahi-browse -rt _ipp._tcp            # Linux; -r shows TXT records (model, admin URL)

# Light TCP connect check of known ports, one host, no OS/version detection, no scripts:
nmap -sT -Pn --max-retries 1 --scan-delay 200ms -p 21,23,80,443,445,515,631,5357,8080,9100 <printer-ip>

# EWS headers only (no login, no credentials):
curl -skI https://<printer-ip>/
curl -sI  http://<printer-ip>/

# IPP attributes (a read-only Get-Printer-Attributes request; CUPS tools). Agree with the user first:
ipptool -tv ipp://<printer-ip>/ipp/print get-printer-attributes.test

# SNMP: only with a community string the user provides and agrees to use; never guess one.
snmpget -v2c -c <community-from-user> <printer-ip> SNMPv2-MIB::sysDescr.0
```

- A port that is open is evidence enough. Don't connect to 9100, 515, or 631 with `nc`, `telnet`, or a
  browser to "see what it says": raw ports print whatever they receive.
- The IPP query and SNMP query read attributes; they don't change settings. Some IPP attributes reveal
  the serial number, location, and organization name. Record them in the report only as needed and
  redact identifiers.

**Never do any of the following, for any reason:**

- Send a print job, test page, PJL, PostScript, PCL, or raw text to any printer port, or use printer
  exploitation frameworks (for example PRET-style tools) that do.
- Try default, blank, setup-sticker, or serial-derived passwords; guess or brute-force EWS, SNMP, FTP,
  Telnet, or Wi-Fi Direct credentials; or guess SNMP community strings.
- Run exploit or proof-of-concept scripts, including "check" scripts for printer CVEs, or vulnerability
  scanner plugins against printers.
- Open, preview, download, or delete stored, held, or secure-print jobs, scan files, fax logs, or job
  logs that show document names.
- Export, print, or screenshot address books, LDAP, SMTP, SMB, or FTP settings with passwords visible,
  or export a configuration or "clone" file that contains them.
- Factory-reset, "restore defaults", initialize storage, flash or downgrade firmware, or enable Telnet,
  FTP, or debug and service modes to look around.
- Join the printer's Wi-Fi Direct network to test it.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, firmware, and vendor support

- Every printer and MFP: vendor, model, firmware version, and how it is connected (Wi-Fi, Ethernet,
  both, Wi-Fi Direct). Note the real OEM for rebranded devices (some vendors' models are built on
  another vendor's platform and share its advisories).
- Firmware currency: compare with the vendor's support page for the exact model. Check the vendor's
  security advisories (see [references.md](references.md)) and CISA KEV for the model; validate per core
  triage rather than assuming a CVE applies because the brand matches.
- Automatic updates: on, off, or "notify only". Off is common because of cartridge-policy concerns; if so,
  is someone updating manually?
- Vendor support status: is the model end-of-life or no longer receiving firmware? An end-of-life printer
  with known vulnerabilities is a lifecycle finding (core triage).
- Firmware integrity features, where the model has them: signed firmware, secure boot, runtime integrity
  checks or whitelisting. Record whether they are present and enabled; don't test them.
- Remote or network firmware upgrade: who can push firmware (EWS admin only, or any client through a
  print port or an unauthenticated update service on older models).

#### B. Administration and authentication

- EWS admin password: **ask** whether it was set and how. Changed from the factory value? Unique to this
  device? Stored in a password manager? On models whose factory password is the serial number or is
  derived from it, an unchanged factory password is a high-priority finding (see vendor notes).
- Control-panel lock: can anyone at the panel change network settings, reset to defaults, or view the
  address book? Look for an administrator lock or panel PIN.
- Other accounts: user, guest, or department accounts; any service or dealer accounts; remote-support
  tools.
- EWS reachable over plain HTTP: redirected to HTTPS, or HTTP disabled where the model allows it. A
  self-signed certificate is normal; a certificate the user installed is better for MFPs that send
  credentials.
- Session timeout and lockout after failed logins, if offered.
- Access control for walk-up functions on MFPs (copy, scan, fax, USB): user codes, PIN or card release,
  or none.

#### C. Network services and protocols

For each service, record whether it is on, whether anything uses it, and from where it is reachable:

- **Raw port 9100, LPD 515, IPP 631:** which ones clients actually use. Modern clients usually need only
  IPP/IPPS (and AirPrint/Mopria, which use IPP). Unused print protocols are unnecessary attack surface;
  raw 9100 and LPD have no authentication.
- **IPPS / TLS:** offered, and preferred by clients? Minimum TLS version where configurable; old SSL/TLS
  versions disabled.
- **SNMP:** version in use. SNMPv1/v2c communities are clear-text passwords; a writable community lets
  anyone change settings. Prefer SNMPv3, or v1/v2c read-only with a non-default community restricted to a
  management host, or off if nothing monitors the printer. Note that SNMP commonly discloses the serial
  number, which matters on models with serial-derived passwords.
- **FTP, Telnet, TFTP:** printing or management over FTP and Telnet should be off; an open Telnet port is
  a high-priority finding by default.
- **SMB/WSD, LLMNR/NetBIOS, Bonjour/mDNS, SLP:** discovery and Windows printing services; needed on this
  network?
- **Wi-Fi Direct / "Wireless Direct" / soft-AP:** on or off; if on, is it using a custom passphrase (not
  the default printed on the configuration page or a well-known default)? Wi-Fi Direct lets anyone in
  radio range connect to the printer without joining the main network, and on some models reach the EWS.
  Ask the user whether anyone uses it.
- **Wi-Fi security** for the printer's main connection: WPA2 or WPA3; not WEP or open; WPS PIN disabled.
- **Remote panel, remote management, or remote-support services** (vendor-specific): needed?
- **IPv6:** a global IPv6 address on the printer may be reachable from outside if the firewall allows it.

#### D. Cloud printing and vendor accounts

- Vendor cloud features: email-to-print addresses (the printer's own email address accepts jobs from
  the internet), vendor apps' remote printing, cloud connectors, and web services. Which are on, and are
  they used?
- Email-to-print: is the printer's address public, and is there an allowed-senders list?
- The vendor account that owns the printer: strong unique password, MFA where offered, shared users and
  old devices reviewed. Under subscription plans, the account can see print history and may control the
  printer.
- Universal Print, mobile print services, and third-party cloud connectors: which accounts and tenants
  they belong to.
- Whether the printer must reach the internet to function under the user's plan (affects domain G).

#### E. Stored credentials: scan, email, and directory

List, without exposing secrets:

- **SMTP (scan-to-email, alerts):** which mail account, whether it is a dedicated account or someone's
  personal mailbox, whether it can send to any address, and whether TLS is required. A shared mailbox
  password stored on a printer is a common way to lose a mail account.
- **SMB scan-to-folder:** which server and share, which account (a domain or NAS user?), and what that
  account can reach. It should be a dedicated, least-privilege account with write access to one folder,
  not an admin or a person's account. SMB signing and SMB2/3 where offered; SMB1 off.
- **FTP/SFTP scan destinations:** clear-text FTP sends the password over the network on every scan.
- **LDAP (address book lookup, user authentication):** bind account and its rights (it should be a
  read-only, dedicated account), whether LDAPS or StartTLS is used, and whether anonymous bind is used
  instead. Anyone with EWS admin can usually point LDAP or SMB settings at a server they control and
  capture the stored credential (a "pass-back" attack; see the Xerox note).
- **Per-user address book entries** with their own stored passwords.
- **Cloud storage destinations** (scan to cloud drives) and the tokens they hold.
- Whether the EWS shows stored passwords or only masks them, and whether a configuration export or clone
  file includes them (ask; don't export).

#### F. Stored jobs, internal storage, and data at rest

- Internal storage: hard drive, SSD, or eMMC, and its size; or only RAM.
- Job retention: stored, held, or "secure print" jobs; scan-to-box or document server features; fax
  receive memory; job logs showing document names and users. Retention period and who can see them.
- Storage encryption: supported, enabled? Image overwrite or immediate job erase after completion:
  supported, enabled?
- Removable storage: USB direct print and scan-to-USB on or off.
- Fax: received faxes printed at once or held in memory; forwarding to email or folders.

#### G. Network placement and pivot risk

- Segment: is the printer on the main user LAN with servers and admin hosts (a flat network), or on a
  printer or IoT segment?
- Inbound: which clients can reach the print ports and the EWS. Ideally clients (or only the print
  server) reach the print ports, and only an admin host reaches the EWS and SNMP.
- Outbound: what the printer can reach. A printer that can reach file servers (scan-to-folder), the mail
  server, the directory, and the internet is a useful pivot for an attacker who controls it. Limit it to
  the destinations it needs: the scan share, the mail relay, LDAP, NTP, DNS, and the vendor update or
  cloud endpoints if required.
- Cross-segment discovery: mDNS reflectors or Bonjour gateways that make the printer visible on other
  VLANs; how clients find it after a move.
- Wired port: an MFP in a lobby or shared area gives anyone an Ethernet port; check what that switch port
  can reach.
- Static address or DHCP reservation, so rules and client queues keep matching.

#### H. Internet exposure

- Port forwards, DMZ, or UPnP mappings on the router pointing at the printer. Printers with IPP, raw
  9100, or the EWS reachable from the internet are routinely found by internet-wide scans (for example
  the Shadowserver Foundation reports open IPP on 631 daily). Treat any internet-reachable printer
  service as P1 by default.
- UPnP on the printer, and the router's current mappings for the printer's address.
- Global IPv6 address with an inbound firewall rule.
- External checks only with explicit authorization, and only connection checks (no job submission).

#### I. Disposal, return, and repair

- Is there a documented process for the end of the device's life, lease return, or warranty repair?
- MFPs with internal drives: the vendor's secure erase or "data overwrite at end of life" feature, the
  drive being removed and sanitized or destroyed, or a certificate from the dealer. NIST SP 800-88 applies
  to embedded storage in copiers and MFPs; follow the organization's sanitization program.
- Home printers: Wi-Fi passwords, the vendor account binding, address books, and fax logs. Some vendors
  document that a normal reset doesn't erase everything (see the Canon note); follow the vendor's
  disposal steps for the model.
- Remove the printer from the vendor cloud account and from the scan destinations' accounts (rotate those
  passwords) when it leaves.

#### J. Logging, time, and monitoring

- Syslog: can the printer send logs (logins, configuration changes, job events) to a central server?
  Many home models can't; note it.
- Local event or audit log: present, retention, and whether it records EWS logins and changes.
- NTP and time zone: correct time for log correlation and certificate validity.
- Alerts: email alerts for configuration changes or errors use the stored SMTP credentials (domain E).
- Network evidence: firewall logs for the printer's outbound traffic (unexpected destinations) and
  inbound connections from unusual hosts to 9100, 631, 515, or the EWS.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

List what depends on the setting before recommending a change:

- **Clients and queues:** which computers, phones, and print servers print to it, and over which
  protocol (raw 9100, LPD, IPP, AirPrint/Mopria, WSD). Disabling a protocol breaks queues that use it.
- **Discovery:** moving the printer to another VLAN breaks AirPrint and Mopria discovery unless an mDNS
  reflector or a manually added queue (by address) replaces it.
- **Scan workflows:** scan-to-folder, scan-to-email, and LDAP lookups depend on stored credentials and
  network paths; rotating a password or blocking egress breaks them.
- **Cloud and subscription plans:** some plans need a persistent internet connection and vendor account.
- **Managed print / dealer:** meter reading, supplies ordering, and remote support use SNMP, a vendor
  agent, or a cloud connection.
- **Monitoring:** anything polling SNMP.
- **Firmware updates:** downgrades are usually blocked after an update, and updates can change cartridge
  acceptance or remove old protocols.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Printer reachable from the internet (forward, DMZ, UPnP, IPv6) | Remove the forward or mapping; disable UPnP. Use the vendor cloud or a VPN for remote printing. | Remote printing through the forward stops. |
| EWS admin password never set or unchanged factory value | The user sets a strong, unique admin password and stores it in a password manager. | None for printing; anyone managing the printer needs the new password. |
| No control-panel lock | Enable the admin lock or panel PIN for network and reset settings. | Walk-up users can't change settings without the PIN. |
| Outdated firmware | The user updates from the vendor's site or the printer's update function after reading the release notes. | Reboot; downgrades usually blocked afterward; possible change to third-party cartridge acceptance or protocol defaults. |
| Automatic updates off | Turn them on, or set a recurring manual update check. | Same as above, without a chance to read release notes first if fully automatic. |
| End-of-life model | Plan replacement; until then, isolate and restrict inbound and outbound access. | Hardware cost. |
| Unused print protocols (9100, LPD, FTP, Telnet, WSD) | Disable the ones nothing uses; prefer IPP/IPPS. | Old drivers or queues using raw or LPD must be re-added as IPP. |
| SNMP v1/v2c with default or writable community | Use SNMPv3, or read-only v1/v2c with a non-default community restricted to the monitoring host, or turn it off. | Driver status, supply levels, and dealer meter reading may need reconfiguring. |
| Wi-Fi Direct on and unused, or default passphrase | Turn it off; if needed, set a custom passphrase. | Guests and phones that print directly lose that path. |
| EWS over plain HTTP | Redirect or disable HTTP; install a certificate where the model supports it. | Old bookmarks break; some apps may expect HTTP. |
| Scan-to-folder using an admin or personal account | Create a dedicated account with write access to one share only; the user enters it on the printer. | Scan-to-folder breaks until updated; the share's permissions need setting. |
| Scan-to-email using a personal mailbox | Use a dedicated mail account or an authenticated relay that only sends internally; require TLS. | Mail-provider setup work; some providers need app-specific passwords. |
| LDAP with a privileged bind account or no TLS | Use a read-only bind account and LDAPS or StartTLS. | Address lookup breaks if certificates don't validate on the printer. |
| Clear-text FTP scan destination | Move to SMB3 or SFTP where supported. | The destination server needs the new protocol enabled. |
| Stored jobs retained indefinitely | Enable automatic deletion after a short period and immediate job erase where supported. | Users can't reprint old jobs. |
| Internal storage unencrypted | Enable storage encryption where supported. | May require initializing storage (C3, user-run) and erasing stored jobs and boxes. |
| Printer on a flat network | Move printers to a printer or IoT segment; allow print ports from clients and EWS/SNMP from an admin host only; allow the printer outbound only to its scan, mail, LDAP, NTP, and update destinations. | C2 project; discovery needs an mDNS reflector or manual queues; scan workflows need explicit rules. |
| No disposal process | Document vendor secure erase plus storage removal or a dealer certificate; remove cloud bindings and rotate stored credentials at disposal. | Lease contracts may restrict drive removal. |
| Email-to-print address open to anyone | Restrict to allowed senders or turn it off. | Unlisted senders can't print. |
| No logging | Send syslog to a central server where supported; otherwise rely on firewall logs. | Needs a log receiver. |

Changing default ports and hiding the printer from discovery are supplementary only. Never recommend them
as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet exposure, unset or factory admin
password, open Telnet, known-exploited firmware) → high-priority hardening (stored credential accounts,
SNMP, Wi-Fi Direct, segmentation) → routine maintenance (firmware, logging, retention) → optional defense
in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Printer specifics:

- **Before any change:** record the current settings with screenshots of the relevant EWS pages, with
  password fields masked. If the user makes a configuration export or clone file, it contains stored
  credentials: it stays with the user, protected, and is never pasted into chat or reports.
- **Who types secrets:** the user sets the admin password, SNMP communities or v3 credentials, Wi-Fi
  Direct passphrases, and scan-destination passwords. The agent never generates, sees, or stores them.
- **Settings changes (C1):** disabling unused protocols, Wi-Fi Direct, or cloud features. Change one
  thing, then confirm printing from each client type still works (desktop, phone, print server). The
  agent may guide the user through the EWS or act in a session the user opened, with approval.
- **Credential rotation for stored accounts (C2):** create the new least-privilege account on the target
  system first, update the printer, test one scan, then disable the old account. Stored credentials on a
  printer that may have been accessed by others should be treated as exposed and rotated, not just moved.
- **Firmware updates (C2):** the user applies firmware only from the vendor's site or the printer's
  built-in update, for the exact model, with stable power, outside working hours for an office MFP. Read
  the release notes first for cartridge-policy, protocol, and downgrade notes. Never install firmware from
  third-party sites, and never use modified or "chip-free" firmware.
- **Network moves (C2):** reserve the new address, add the firewall rules and any mDNS reflector, move the
  printer, re-add or confirm client queues, then test print and every scan workflow. Keep EWS access from
  an admin host until verified.
- **Storage encryption or overwrite settings (C3 when they initialize storage):** user-run, after the user
  confirms nothing stored on the device is needed.

After each change, follow the core "after a change" steps: re-read the setting, run the light port check
where agreed, print a test page from a client (the user does this), test each scan destination, check
firewall logs, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Testing default, factory, or serial-derived passwords, guessing SNMP communities, brute force, or
  running exploit code or printer exploitation frameworks, for any reason.
- Sending print jobs, PJL, PostScript, or PCL to a printer as part of an assessment.
- Factory reset, "restore all defaults", storage initialization, or secure erase (except as the user's
  own disposal step).
- Flashing, downgrading, or cross-flashing firmware, or using service, debug, or bootloader modes.
- Opening, exporting, or deleting stored jobs, document boxes, fax memory, or address books with
  passwords.
- Removing or wiping an MFP hard drive (the user, dealer, or a sanitization provider does this).

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the printer-specific
steps in [incident-response.md](incident-response.md).

---

## Vendor-family notes

Short notes only for facts verified against the sources in [references.md](references.md). Always check
the vendor's current documentation for the exact model; menus and defaults change with firmware.

### HP

- HP's guidance for home printers is to set an EWS admin password (without one, anyone on the network can
  change any setting), turn Wi-Fi Direct off when not in use or set a custom or random Wi-Fi Direct
  password, and keep firmware current. Menu paths differ between the HP Smart app, the EWS, and the
  control panel; verify them for the model.
- HP's firmware readmes for code-signed LaserJet firmware note that once signature verification is
  installed, downgrading to earlier firmware is no longer possible. Enterprise-class HP devices add
  firmware integrity checks at boot and run time; check the model's security guide.
- HP inkjet firmware has been used to enable or change "dynamic security" cartridge authentication, which
  blocks cartridges with non-HP chips or circuitry. Users who disable automatic updates to keep third-party
  cartridges working also stop receiving security fixes; explain the trade-off and point to HP's support
  documentation for the current options on the model. Subscription plans such as HP+ add conditions
  (account, persistent internet connection, original supplies); check the plan's terms.

### Brother (and some Fujifilm, Konica Minolta, Toshiba Tec models)

- In 2025, researchers reported that the factory administrator password on several hundred Brother
  models is derived from the serial number (CVE-2024-51978), and that the serial number can be read
  without authentication over the network (CVE-2024-51977, and later CVE-2025-8452 via eSCL). Brother
  addressed the other issues in firmware and changed its manufacturing process; for existing devices the
  fix is to change the administrator password. Some Fujifilm, Konica Minolta, and Toshiba Tec models were
  also affected. Ask whether the password was changed; don't test it.

### Epson

- Epson documents that the initial Web Config administrator password on many products is the serial
  number (or a password on a label), and that the serial number can be obtained over SNMP on the same
  network (CVE-2025-35970). Epson's mitigation is to change the administrator password, and keep the
  product on a firewall-protected network with a private address. Epson publishes a security guidebook.

### Canon

- Canon's PSIRT advisory CP2023-003 warned that on many inkjet models a normal initialization does not
  erase Wi-Fi connection settings, exposing them to repairers, later owners, or renters. Canon's
  documented steps are to reset all settings, enable wireless LAN, then reset all settings again (models
  without "reset all" use the LAN reset steps). Follow the advisory for the model before disposal,
  repair, or resale.

### Xerox

- In 2025, Rapid7 reported pass-back vulnerabilities in Xerox VersaLink MFPs (CVE-2024-12510 for LDAP,
  CVE-2024-12511 for SMB/FTP): an attacker with admin access could point the LDAP or scan settings at a
  server they control and capture the stored credentials, including directory accounts. Xerox released
  fixed firmware. This class of issue applies broadly: protect the EWS admin account and use
  least-privilege accounts for every stored credential. Xerox publishes per-family security bulletins and
  an RSS feed.

### Lexmark

- Lexmark publishes security advisories per firmware family on its security advisories page and
  recommends firmware updates as the fix. Check the advisory list for the device's firmware family code.

---

## Worked example (invented)

### PRN-001: Office MFP on the flat LAN with no admin password and a domain admin account for scan-to-folder

**Confidence:** Confirmed
**Priority:** P1. Anyone on the network can open the MFP's EWS without a password and either read or
redirect the stored scan-to-folder credential, which belongs to a privileged account on the file server.
**State:** Open
**Component:** Small-office color MFP, vendor EWS, firmware one year behind the vendor's current release
**Evidence:** Observed 2026-05-04: the user confirmed no admin password was ever set; the EWS at
`192.0.2.40` opened its settings pages without a login when the user browsed to it. The scan-to-folder
profile targets `\\<file-server>\<share-name>` with the account `<admin-user>`, which the user confirmed
is a member of the server's administrators group. The printer is on the same subnet as the file server
(`192.0.2.10`) and the user workstations. A light TCP check showed 80, 443, 515, 631, 9100, and 23 open.
**Expected secure state:** EWS admin password set; scan-to-folder uses a dedicated account with write
access to one share; Telnet and unused print protocols off; printer reachable for administration only
from an admin host.
**Exposure and prerequisites:** any device on the LAN, including a compromised workstation or a guest on
the same Wi-Fi; no credentials required.
**Dependencies / blast radius:** six workstations print over IPP; two staff scan to the share daily; the
dealer reads meters over SNMP.
**Recommended remediation:** (1) the user sets a strong EWS admin password and a control-panel lock;
(2) create a dedicated scan account with write access to the scan share only, update the profile, test,
then remove the admin account from the printer and rotate that admin account's password, since it must be
treated as exposed; (3) disable Telnet and LPD after confirming no queue uses them; (4) update firmware;
(5) plan a move to a printer segment with rules allowing IPP from clients, SMB to the file server only,
and EWS/SNMP from an admin host and the dealer's collector.
**Operation class:** C1 (admin password, Telnet/LPD), C2 (credential rotation, firmware, network move).
**Approval required:** Yes.
**Verification:** EWS requires a login; the scan profile shows the new account and a test scan arrives;
the old admin password no longer works on the file server; port check shows 23 and 515 closed; printing
works from each workstation.
**Rollback:** re-enable LPD or Telnet if an unexpected dependency appears (not recommended for Telnet);
the admin password can be cleared by the user from the EWS.

---

## Version history

- **1.0** (2026-10-30): Initial version.
