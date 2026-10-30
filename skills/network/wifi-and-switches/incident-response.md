# Wi-Fi Mesh and Managed Switches: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only mesh- and switch-specific steps.

The Wi-Fi system decides who gets onto the network, and the switches decide which segment they land in.
A compromised vendor account, mesh node, or switch can let an attacker join the network, re-patch VLANs,
mirror traffic, or point clients at a rogue DNS server, often without any change on the firewall.

## Triage and containment

- **Indicators that point at the Wi-Fi or switching layer:** unknown devices on the main SSID; admins or
  household members added to the vendor account that nobody added; account sign-in or one-time-code
  emails nobody requested; port forwards, UPnP mappings, DNS settings, or mode changes nobody made; a
  new SSID or a changed passphrase; on switches, unknown local accounts, a changed enable secret, new
  SNMP communities, unexpected VLAN or trunk changes, a SPAN/monitor session nobody created, unexplained
  reloads, or a running config that differs from the last backup.
- **Account compromise (app-managed mesh):** first secure the vendor account (and its parent platform
  account) from a clean device: change the password, enable or reset MFA, and sign out other sessions
  where the app allows. Then remove unknown shared admins and integrations. Do this before changing
  anything on the network itself, or the attacker can undo it.
- **Unknown client on Wi-Fi:** block or remove that client in the app or controller, then change the
  passphrase of that SSID (C2: every legitimate device must rejoin). If WPS was on, turn it off first.
- **Switch compromise suspected:** contain *around* it. Move the uplink at the firewall side (or shut the
  firewall's port to it) rather than reloading the switch. Keep a console session. Don't reload: the
  running config, logs, and active sessions are in memory and are lost.
- **Don't factory-reset** a mesh node or switch during triage. A reset destroys evidence and, on mesh
  systems, may leave an open setup network until reconfigured.

## Evidence to preserve (mesh- and switch-specific)

Collect from a clean admin device, before changing anything:

- **Mesh / controller:** screenshots or exports of the device and client list, admin and shared-user
  list, account activity or notification history, port forwards, UPnP mappings, DNS settings, operating
  mode, SSIDs and their security modes, and the firmware version of every node. Self-hosted controllers:
  a controller backup (treat as secret) and its logs.
- **Switch:** `show running-config` and `show startup-config` copied **off-box to a protected location**
  (not pasted into a chat or report; they contain secrets), `show version` (uptime and last reload
  reason), `show users`, `show logging`, `show archive` and any archive log, `show monitor session all`
  (traffic mirroring), `show interfaces trunk`, `show vlan brief`, `show snmp user`, `show mac
  address-table`, and `show clock` to anchor timestamps. Verify command availability on the installed
  release.
- Remote syslog and the firewall's logs for the same period (DHCP leases, management-plane connections
  to the switch or controller).
- The last known-good configuration backup, to diff against.

## Scope checks specific to Wi-Fi and switches

- Every device on the affected SSID or VLAN: an attacker on the network could reach them directly.
- Every system whose credentials were on the device: RADIUS/TACACS shared secrets, SNMP communities and
  SNMPv3 users, syslog and backup destinations, the Wi-Fi passphrases of every SSID (all of them are in
  the mesh account and the controller backup).
- If DNS or DHCP settings were changed on the mesh, clients may have used attacker-chosen DNS; check for
  credential theft on services they used.
- If a SPAN or trunk change was made on a switch, assume traffic on the mirrored ports was captured.
- The admin devices used for the app, controller, or switch sessions.
- Other devices managed by the same vendor account or controller (other sites, cameras, smart-home
  integrations).

## Eradication and recovery

- **Mesh:** update every node to current vendor firmware. If node integrity is in doubt, remove the nodes
  from the account, factory-reset them (now, after evidence is preserved), and set them up fresh with new
  SSID passphrases. Don't restore settings from a time after the earliest plausible compromise.
- **Switch:** reinstall a vendor image verified against the published checksum, then rebuild from a
  backup taken **before** the earliest plausible compromise (diff it against the compromised config
  first). Used switches with unknown history get the same treatment.
- **Rotate everything the device held:** vendor account password and MFA, every Wi-Fi passphrase, switch
  local accounts and enable secret, SNMP communities and SNMPv3 credentials, RADIUS/TACACS secrets.
- If the hardware is past end of support, replace it rather than rebuild it.
- Before reconnecting: management not reachable from guest/IoT segments or the internet, Telnet/HTTP and
  read-write SNMP off, Smart Install disabled, WPS off, UPnP off unless justified, MFA on, and an
  off-box backup of the new configuration taken.

## Quick checklist tailored for Wi-Fi and switches

Start with the core quick checklist, plus:

- [ ] Secure the vendor account first (password, MFA, sign out sessions, remove unknown admins), from a
      clean device.
- [ ] Don't reload or factory-reset anything yet; screenshot the app and copy switch configs off-box.
- [ ] Remove unknown clients, turn off WPS, then change the affected SSID passphrase.
- [ ] Check switches for unknown accounts, SPAN sessions, and VLAN or trunk changes.
- [ ] Plan to rotate every passphrase and secret the mesh, controller, or switch held.
