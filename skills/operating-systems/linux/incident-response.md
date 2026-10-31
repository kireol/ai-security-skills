# Linux Hosts: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only Linux-specific steps.

An attacker with root on a Linux host can change every log, binary, and tool on it, including the ones
used to investigate. Treat output from a possibly compromised host as evidence, not proof, and confirm
important observations from outside it (hypervisor, network, backup system, log host) where you can.

## Triage and containment

- **Indicators that point at the host itself:** unknown user accounts or UID 0 accounts, unknown
  `authorized_keys` entries, new sudoers rules, entries in `/etc/ld.so.preload`, cron jobs or systemd
  units/timers nobody created, unowned SUID binaries, unexpected listening ports or outbound connections
  (cryptominers and reverse shells commonly connect out), processes running from `/tmp`, `/dev/shm`, or
  deleted files, changed package-owned binaries (`debsums`, `rpm -Va`), SELinux or AppArmor suddenly
  disabled, firewall rules changed, logs or the journal truncated, or `.bash_history` linked to
  `/dev/null`.
- **Contain at the network layer, outside the host where possible:** block the host at the upstream
  firewall or switch, or (for VMs and containers) disconnect its virtual NIC at the hypervisor. A
  firewall rule added on a compromised host can be removed by the attacker.
- **Keep it running, isolated.** Memory, running processes, network connections, and deleted-but-open
  files are lost on reboot. Don't reboot, run updates, or "clean up" before evidence is preserved, unless
  destruction is ongoing.
- **Stop backups from this host** writing to shared destinations, and unmount backup targets and
  network shares if that can be done without destroying evidence. Don't delete or prune backups.
- **Remote access:** if the agent's own access path (SSH key, sudo account) might be known to the
  attacker, say so; plan to rotate it during recovery, not mid-triage.
- **Containers:** if the host runs privileged containers or exposes the container runtime socket,
  assume a container compromise may be a host compromise, and vice versa.

## Desktops and laptops

- **Desktop-specific indicators:** browser extensions nobody installed, new desktop autostart entries
  (`~/.config/autostart/`, `/etc/xdg/autostart/`), desktop sharing or a remote-support agent turned on
  that the user didn't enable, unknown MOKs (`mokutil --list-enrolled`) or Secure Boot suddenly off, an
  AUR, Flatpak, or snap package that changed owner or behavior just before the symptoms, and new paired
  devices in KDE Connect or GSConnect.
- **Contain:** disconnect the computer from the network (Wi-Fi off or cable out) rather than shutting it
  down, unless destruction is ongoing; turn off desktop sharing and remote-support agents by
  disconnecting, not by uninstalling (keep the evidence). From a **different, trusted device**, sign out
  the user's browser sessions and important accounts (email, password manager, cloud storage, Git
  hosting): session cookies in the browser profile let an attacker in without passwords or MFA.
- **Evidence:** in addition to the general list, copy (don't open in the browser) the browser profile's
  extension list and history databases if a specialist needs them, the autostart directories, the
  Flatpak and snap lists with versions, `pacman -Qm` and `/var/log/pacman.log` on Arch, and remote-desktop
  configuration and logs.
- **Scope:** everything the user's session could reach: saved browser passwords and cookies, the
  desktop keyring (GNOME Keyring, KWallet), SSH and GPG keys, password-manager vaults that were unlocked,
  synced cloud folders, and any work systems the user signed in to from this computer.
- **Lost or stolen laptop:** this is an incident even without malware. Establish whether the disk was
  encrypted and how it unlocked (domain P): passphrase-only with the laptop powered off is the best case;
  TPM-only unlock with auto-login, or a laptop taken while unlocked or asleep, means treat everything on
  it as exposed. Sign out its sessions from other devices, revoke its SSH keys, API tokens, and VPN
  peers, rotate saved passwords, and remove it from accounts that list trusted devices. Linux has no
  built-in remote wipe; don't promise one.
- **Recovery:** reinstall from verified media, with full-disk encryption on; restore documents from a
  backup taken before the compromise, but not the browser profile, autostart entries, or shell startup
  files without review; reinstall extensions and apps from their official sources only.

## Evidence to preserve (Linux-specific)

Collect before changing anything, saving output off the host (to the admin workstation or a log host),
and recording the time and the command used. Redact secrets.

- **Volatile state first:** `date -u; uptime`, `ps auxwwf` (process tree), `ss -tupan` (all sockets with
  processes), `ip addr; ip route; ip neigh`, logged-in users (`who`, `w`, `loginctl list-sessions`),
  `lsof -nP +L1` (deleted files still open; verify the flags on the installed version), and the
  executable path and command line of suspicious processes (`ls -l /proc/<pid>/exe`,
  `cat /proc/<pid>/cmdline | tr '\0' ' '`). Don't print `/proc/<pid>/environ` into chat; save it to the
  evidence store if needed.
- **Memory:** for a VM, a hypervisor snapshot that includes memory is the least invasive capture. On bare
  metal, memory acquisition needs specialist tools; refer it out rather than improvising.
- **Disk:** a VM or container snapshot, or (for physical hosts) a forensic image by a specialist. For a
  Raspberry Pi, image the SD card offline (on another machine) if it is taken out of service.
- **Accounts and access:** `/etc/passwd` and `/etc/group` (copies; never print `/etc/shadow`, but do copy
  it into the evidence store if a specialist needs it), sudoers and `/etc/sudoers.d/`, every
  `authorized_keys` file with fingerprints, `lastlog`/`last`/`lastb` output.
- **Persistence:** crontabs (system and per-user), `at` jobs, systemd unit files and timers in `/etc`,
  `/run`, and user directories, lingering users, `/etc/ld.so.preload`, `/etc/rc.local`, shell startup
  files, PAM configuration, loaded kernel modules (`lsmod`), and `/etc/update-motd.d/`.
- **Logs:** export the journal (`journalctl -o export` or `journalctl --since <time>` to a file), the
  auth log (`/var/log/auth.log` or `/var/log/secure`), the audit log (`/var/log/audit/`), package logs
  (`/var/log/dpkg.log`, `/var/log/apt/`, `dnf history`), web server logs, and container logs. If the
  journal is volatile, export it before any reboot. Copy logs held by a remote log host too; they are
  the most trustworthy.
- **Integrity:** package verification output (`debsums -c` or `rpm -Va`), a list of SUID/SGID files,
  recently modified files in system directories (`find /etc /usr /bin /sbin -xdev -newer <reference-file>`
  or with `-mtime`), and hashes of suspicious files (`sha256sum`). Don't upload unknown binaries to public
  scanning services without the user's agreement; hashes are usually enough to look up.
- **Configuration:** the firewall ruleset, `sshd -T`, repository lists and keys, and installed package
  list (`dpkg -l` or `rpm -qa`).

## Scope checks specific to a Linux host

- **Keys stored on this host:** every private SSH key, deploy key, or API token here may now be in the
  attacker's hands. List what each one opens (other servers, Git hosting, cloud accounts, backup
  repositories) and treat those as in scope.
- **Hosts that trusted this one:** systems where this host's keys are in `authorized_keys`, NFS clients
  and servers, and anything this host administers (Ansible control node, jump host).
- **Credentials in files and environment:** `.env` files, compose files, application configs, cloud CLI
  credentials, database passwords, and service tokens on this host.
- **Users who logged in during the window:** their passwords or agent-forwarded keys may have been
  captured (SSH agent forwarding exposes the agent to root on the far host).
- **The hypervisor or LXC host** (for VMs and containers) and other guests on it, especially if the
  container was privileged or had device or bind-mount access.
- **Shares and mounts:** data on NFS/SMB mounts and backup destinations reachable from this host.
- **Services the host provided:** DNS, reverse proxy, VPN, or home automation; clients may have been
  redirected or their credentials captured.

## Eradication and recovery

- **Rebuild rather than clean** when root compromise is confirmed or likely. Rootkits and modified
  binaries can't be ruled out from inside. Reinstall from verified distribution media (check the
  published checksum and signature), or recreate the VM or container from a known-good template.
- Restore data and configuration only from backups taken **before** the earliest plausible compromise,
  and review restored configuration (cron, units, `authorized_keys`, sudoers, repositories, shell startup
  files) before putting it back. Don't restore binaries or `/usr/local` from a possibly compromised backup.
- **Rotate every secret that was on the host or typed on it:** user and root passwords, SSH host keys
  (new host keys, and tell users to update `known_hosts`), user SSH keys stored here and any keys that
  were in `authorized_keys`, application secrets, API tokens, database passwords, cloud credentials,
  VPN keys, and backup repository passwords.
- Before reconnecting: supported release, fully updated and rebooted into the new kernel, SSH keys only,
  no root password login, firewall default-deny for IPv4 and IPv6, MAC (AppArmor/SELinux) enforcing,
  only expected repositories, persistence surfaces reviewed, and remote logging working so the next
  incident leaves evidence off the host.
- Find and fix the entry point (an exposed service, a weak password, a vulnerable web app, a leaked key)
  before reconnecting, or the rebuilt host will be compromised the same way.

## Quick checklist tailored for a Linux host

Start with the core quick checklist, plus:

- [ ] Isolate the host at the upstream firewall, switch, or hypervisor, not with rules on the host itself.
- [ ] Don't reboot: capture processes, sockets, logged-in users, and a VM snapshot with memory first.
- [ ] Export the journal and auth/audit logs off the host (and copy them from the remote log host).
- [ ] List accounts, sudoers, authorized_keys, cron, systemd units/timers, and `/etc/ld.so.preload`.
- [ ] List every key and credential on the host and what it opens elsewhere; plan to rotate all of them.
- [ ] Plan to rebuild from verified media or a known-good template rather than cleaning in place.
- [ ] Desktop or laptop: from another device, sign out browser and account sessions, and review browser
      extensions, autostart entries, remote-desktop settings, and MOKs.
- [ ] Lost laptop: confirm how its disk unlocks, then revoke its keys, tokens, and VPN peers and rotate
      saved passwords.
