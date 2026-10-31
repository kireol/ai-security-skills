# Printers and MFPs: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only printer-specific steps. They apply to standalone network document scanners
too; scanner-specific additions are marked.

A compromised printer matters less for what it prints than for what it holds and what it can reach: the
credentials in its scan and directory settings, copies of documents in its storage, and a trusted
position on the network. If an attacker had admin access to the EWS, assume every stored credential was
read or redirected.

## Triage and containment

- **Indicators that point at the printer:** unexpected pages printing (messages, garbage, or other
  people's documents), changed EWS admin password or new accounts, changed scan destinations, SMTP, or
  LDAP server addresses, new or changed address book entries, Telnet, FTP, or remote-management services
  turned on, unfamiliar firmware versions, a Wi-Fi Direct network the user didn't enable, outbound
  connections from the printer to unknown internet addresses, or the printer connecting to internal hosts
  it never talked to before (a sign of use as a pivot or a pass-back capture). For scanners: new or
  edited scan profiles or shortcuts, a cloud connector linked to an account nobody recognizes, scans
  arriving in an unexpected folder, mailbox, or cloud account, scan-to-email sent to outside addresses,
  or an unknown device or sign-in on the vendor scanner account (for example a ScanSnap account).
- **Contain at the network, not at the printer.** Block the printer's switch port or wireless client, or
  add a firewall rule isolating its address, with approval. Turn off Wi-Fi Direct from the control panel
  if it is in use by an unknown client. Don't factory-reset or power-cycle it before evidence is
  collected: some logs and the current configuration exist only on the device, and some are lost at
  reboot.
- **If the printer is internet-exposed,** remove the port forward or UPnP mapping first (core: containment
  at the edge).
- **Scanner cloud links:** with approval, revoke the scanner's or vendor service's authorization in each
  linked cloud provider's connected-apps page and sign out unknown devices from the vendor scanner
  account; that cuts the path even if the device itself is not yet reachable.
- **Stop trusting stored credentials immediately:** treat every SMTP, SMB, FTP, LDAP, and cloud credential
  on the device as exposed, even before scoping confirms it.

## Evidence to preserve (printer-specific)

Collect with the user, without printing or opening stored jobs:

- Screenshots of the EWS pages for device information (model, firmware, serial redacted in shared
  reports), network and protocol settings, accounts, scan destinations and address book (with password
  fields masked), SMTP, LDAP, SNMP, cloud and web services, and Wi-Fi Direct.
- The device's event, audit, or job log, exported or photographed, and any syslog already sent to a
  central server.
- A configuration export if the model supports it and the user agrees: it holds secrets, so the user keeps
  it protected and it never goes into chat or a shared report.
- Firewall, DNS, and switch logs for the printer's address: inbound connections to 9100, 631, 515, 23, 21,
  and the EWS, and outbound connections to internal servers and the internet.
- Router port-forward and UPnP mapping lists, if internet exposure is suspected.
- For MFPs with internal storage, leave stored jobs and storage untouched; if forensic imaging of the
  drive is needed, that is a specialist task.

## Scope checks specific to printers and MFPs

- Every account whose credential was stored on the device: the scan-to-folder account and every share it
  can reach, the SMTP mailbox (check sent mail and forwarding rules), the LDAP bind account and the
  directory, FTP servers, and cloud storage tokens.
- File servers and shares the printer could reach: new files, changed permissions, or logins from the
  printer's address using unexpected accounts.
- The vendor cloud account: sign-in history, shared users, registered devices, and print history.
- For scanners: every linked cloud storage account (files uploaded by the scanner, app authorizations,
  sharing links), the vendor scanner account's registered scanners and computers, the scan folder's
  access log where available, and the companion-app computers, whose saved destinations hold their own
  credentials.
- Clients that print to it: rogue firmware could serve malicious drivers or content over the EWS or
  discovery responses; check whether any client recently installed a driver from the printer.
- Other printers of the same model and firmware: the same weakness probably applies.
- Documents printed, copied, scanned, or faxed while the device was compromised may have been copied;
  the user decides whether notification obligations apply (core: reporting and privacy).

## Eradication and recovery

- Update to the vendor's current firmware from the vendor's own site, applied by the user. Where the
  vendor documents a way to verify or reinstall firmware, use it. If the firmware's integrity can't be
  established, or the model no longer gets updates, replace the device.
- The user then performs the vendor's factory reset (and, for MFPs, the vendor's storage initialization
  if stored data may be tainted), and reconfigures from scratch rather than restoring a configuration
  export taken after the compromise.
- **Rotate every credential the printer held**, on the target systems: scan-to-folder accounts, SMTP
  mailbox, LDAP bind account, FTP, cloud tokens, SNMP communities, and the Wi-Fi password if the printer
  joined the main Wi-Fi with a shared passphrase that may have been read. For scanners, also re-link
  cloud connectors to accounts the user controls and reset the vendor scanner account's password with
  two-factor authentication on. Replace privileged accounts with
  least-privilege ones as part of the rotation.
- Before reconnecting: EWS admin password set by the user, unused protocols and Telnet/FTP off, Wi-Fi
  Direct off or with a new passphrase, no internet inbound path, outbound limited to required
  destinations, and logging (syslog or firewall logs) in place.

## Quick checklist tailored for printers and MFPs

Start with the core quick checklist, plus:

- [ ] Isolate the printer at the switch, Wi-Fi, or firewall; remove any port forward or UPnP mapping.
- [ ] Don't reset or reboot it until the EWS settings and logs are captured.
- [ ] List every credential stored on the device (scan, email, LDAP, FTP, cloud) and start rotating them
      on the target systems.
- [ ] Check the scan share, mailbox, and directory for activity from the printer's accounts.
- [ ] For scanners, revoke and review cloud connector authorizations and the vendor scanner account.
- [ ] Update firmware from the vendor, reset, and reconfigure with least-privilege accounts before
      reconnecting.
