# Unraid: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only Unraid-specific steps.

## Triage and containment

- **Don't reboot or power off first.** The root filesystem and logs live in RAM; a reboot erases running
  processes, `/var/log`, and anything an attacker changed outside the boot device. Capture evidence (below)
  before any restart, unless active destruction makes immediate isolation more important.
- **Isolate at the network edge.** From a clean device, remove router port forwards and UPnP mappings to the
  server, and disable Unraid Connect Remote Access. Disconnecting the server at the switch (or its virtual
  NIC on the hypervisor, for virtualized Unraid) is often faster and cleaner than changing settings on a
  possibly compromised WebGUI.
- **Stop the spread through shares.** Ransomware often runs on a client and encrypts shares over SMB. Find
  which client or share user is writing, and isolate that client too. Stopping the array halts all share
  access, but stopping it with a failing disk or during a rebuild is risky; check the Main page first and
  see the hard stops in [SKILL.md](SKILL.md).
- **Stop containers that are suspected** rather than deleting them, so their filesystem and logs remain for
  analysis. Stop backup and sync containers or plugins that could overwrite good copies with damaged data,
  after checking that stopping them won't prune recovery points.
- **Protect backup destinations** the server can write to (USB disks, another NAS, cloud buckets):
  disconnect them, or revoke the server's credentials at the destination from a clean device.
- **If the array shows disabled, emulated, or unmountable disks, don't start repairs.** Preserve
  diagnostics and get storage help.

## Evidence to preserve (Unraid-specific)

- **Tools → Diagnostics** zip (consider the non-anonymized option only if the investigator needs real
  names, and store it securely), downloaded to a clean machine.
- The live syslog and any remote syslog copy; the WebGUI and nginx logs if present.
- A full copy of the boot device's `config` folder (from a clean machine, or a local flash backup taken
  now), plus `/boot/extra` and similar boot-time package folders. Record hashes.
- The `go` script, every plugin `.plg` file and plugin folder, user scripts and their schedules, and cron
  entries.
- Container list with images, image IDs, templates, path mappings, networks, and ports; `docker inspect`
  output for suspicious containers; VM definitions.
- Management Access settings, Connect status, Unraid API keys present (names and age only), WireGuard
  peers, and root's SSH authorized keys.
- Users and share security settings, with recent changes.
- Running processes and network connections (`ps`, `ss`), since they disappear on reboot.
- For virtualized Unraid: a hypervisor snapshot may capture VM state, but passed-through disks and the USB
  boot device usually aren't included.

## Scope checks specific to Unraid

- Every client that maps shares, and every share user whose credentials could have been used.
- Every container and VM: each can reach the shares it maps and the LAN; check them for their own
  compromise.
- The Unraid account (Connect): sign-in history, 2FA, and whether cloud flash backups contain tampered
  configuration. Change its password from a clean device.
- Systems sharing the root password or holding the server's API keys (dashboards, phones, automation).
- Any VPN peers (built-in WireGuard, Tailscale) that could still reach the server.
- For virtualized Unraid: the hypervisor's admin accounts and logs.

## Eradication and recovery

- The base OS is reloaded from the boot device at every boot, so persistence usually sits in `/boot/config`
  (the `go` script, plugins, extra packages, SSH keys, templates), in containers and `appdata`, or in VMs.
  A reboot alone is not cleanup.
- If integrity is in doubt, rebuild the boot device with the vendor's current USB Flash Creator (or the
  internal-boot procedure) and restore only reviewed configuration, using the vendor's documented
  procedure for the installed version. Don't restore plugins, the `go` script, or extra packages wholesale
  from a possibly tampered backup; reinstall plugins from CA after review.
- Restore data from a backup outside the server's admin boundary, taken before the earliest plausible
  compromise. Pool snapshots on the compromised server may have been altered.
- Rebuild containers from verified images with fresh secrets; don't reuse `appdata` secrets or API keys.
- Before reconnecting: new root password, Telnet off, SSH keys reviewed, Remote Access and port forwards
  removed or replaced by a VPN, unauthorized plugins, scripts, containers, and VMs removed, Unraid account
  password and API keys rotated, OS and plugins current, and the initial access path identified and closed.

## Quick checklist tailored for Unraid

When the user says "I think my Unraid server has been hacked," start with the core quick checklist, plus:

- [ ] From a clean device, remove port forwards and UPnP mappings and disable Connect Remote Access, or
      unplug the server's network cable. Don't reboot.
- [ ] Download Tools → Diagnostics and copy the boot device's `config` folder to a clean machine.
- [ ] Find which client or share user is modifying files; isolate it.
- [ ] Stop (don't delete) suspicious containers; disconnect backup disks attached to the server.
- [ ] List plugins, the `go` script, user scripts, and SSH keys before changing anything.
