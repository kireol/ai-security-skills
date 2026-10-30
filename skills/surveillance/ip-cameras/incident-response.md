# IP Cameras: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only camera-specific steps.

Cameras have little forensic logging, and much of what a camera botnet does lives only in memory. The
most useful evidence is usually **outside** the camera: firewall, DNS, and NVR logs. A compromised
camera is also a privacy incident (someone may have watched or listened) and a foothold into whatever
network it can reach.

## Triage and containment

- **Indicators that point at a camera:** settings changed that nobody changed (new users, P2P or UPnP
  turned back on, new port forwards via UPnP, changed DNS or NTP servers, FTP or email upload targets
  added); firmware version changed unexpectedly; telnet or another new port open; heavy or unusual
  outbound traffic (scanning, floods, connections to many internet hosts or to unusual ports); the camera
  scanning or logging into other local devices; PTZ moving, the speaker talking, or the IR or status LED
  behaving unexpectedly; the camera rebooting often; the user being locked out of their own account.
- **Contain at the network, not at the camera:** block the camera's internet access and its access to
  every local address except what's needed to observe it, at the firewall or switch (a firewall rule, a
  quarantine VLAN, or disabling the switch port). This stops it attacking others while keeping it
  powered.
- **Don't power-cycle or factory-reset first.** Memory-resident malware disappears on reboot, together
  with the only evidence of it, and the camera may be reinfected within minutes if it comes back on an
  exposed network. Record the state first; a reset is a later, user-performed recovery step.
- **If the camera may be watching or listening to people now** and network containment isn't possible
  quickly, the user can physically cover it or unplug it. Their privacy takes priority over evidence;
  note the time.
- **Remove the entry path:** router port forwards and UPnP mappings to the camera, and P2P or cloud
  access if the cloud account is suspected.
- **Check the cloud account** for cloud-first cameras: change its password and turn on MFA from a clean
  device, sign out other sessions, and remove unknown shared users. This is often the real incident.

## Evidence to preserve (camera-specific)

- Screenshots of the camera's settings pages (users, network, P2P/cloud, UPnP, upload targets, system
  information and firmware version, logs), taken by the user from a clean device.
- The camera's own log, exported if the camera supports it. Treat any configuration export as secret.
- Firewall and router logs for the camera's address: outbound destinations, ports, volumes, times.
  Router UPnP mapping tables.
- DNS query logs for the camera's address (lookups of unfamiliar domains are a strong botnet indicator).
- NVR logs: when the camera went offline, failed logins, stream interruptions; NVR recordings around the
  incident (they may show tampering or someone at the camera).
- Vendor cloud account history: login history, shared users, devices, notification history.
- DHCP and switch tables showing the camera's address and port over time.
- A light port check result (from the agreed short port list), if not done already; no further scanning.

## Scope checks specific to cameras

- **Other cameras of the same model or firmware family,** and any camera sharing the same password:
  assume they're affected until checked.
- **The NVR and any system holding camera credentials** (NVR software, home automation, apps): the
  attacker may have reached the camera through them, or used the camera to reach them.
- **Everything the camera could reach:** if the camera wasn't isolated, check the router or firewall
  admin interface, NAS, and other devices on that network for login attempts from it.
- **Systems whose credentials were on the camera:** FTP or file servers, email accounts used for alerts,
  dynamic DNS accounts, Wi-Fi passwords (a camera on the main Wi-Fi knows its passphrase).
- **The vendor cloud account and its other devices.**
- **People:** who was in view or in earshot during the exposure window, for privacy notifications in
  work or shared environments (core: reporting, privacy).

## Eradication and recovery

- The user factory-resets the camera (or replaces it), then updates firmware from the vendor's site for
  the exact model and hardware revision **before** reconnecting it to anything beyond a quarantine network.
- If the model is end-of-life or the vendor has no fix for the exploited issue, replace it rather than
  restore it.
- Set a new unique admin password and a separate low-privilege NVR account; update every consumer.
  Rotate any credential that was stored on the camera (FTP, email, DDNS, Wi-Fi passphrase if it was on the
  main SSID).
- Reconfigure from scratch rather than restoring a configuration backup taken after the compromise.
- Before reconnecting: P2P, UPnP, telnet, and unused services off; camera on the camera VLAN with internet
  egress blocked; only the NVR can reach it; router has no forwards or UPnP mappings for it; monitoring
  for its egress in place.

## Quick checklist tailored for cameras

Start with the core quick checklist, plus:

- [ ] Block the camera at the firewall or switch (internet and local), but keep it powered until its
      state is recorded.
- [ ] Remove router port forwards and UPnP mappings to it; secure the vendor cloud account (password,
      MFA, sessions, shared users).
- [ ] Save firewall, DNS, router, and NVR logs for the camera's address, and screenshots of its settings.
- [ ] Check every camera with the same model or password, and every system the camera could reach.
- [ ] Recover by user-performed reset, current firmware, new credentials, and isolation, or replace it.
