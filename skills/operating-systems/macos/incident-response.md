# macOS: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only macOS-specific steps.

A compromised Mac usually means compromised accounts: the attacker may have had the user's browser
sessions, keychain items, SSH keys, cloud tokens, and Apple Account session. Scope beyond the Mac early.

## Triage and containment

- **Work Mac first:** if the Mac is employer-owned or MDM-enrolled, tell the user to contact their IT or
  security team before doing anything else. They may need to collect evidence with their own tools, and
  wiping or changing the Mac may break their investigation or violate policy.
- **Indicators that point at the Mac itself:** "background item added" notifications nobody expected;
  unknown LaunchDaemons, LaunchAgents, or login items; an MDM enrollment or configuration profile nobody
  recognizes; new admin accounts or `sudoers.d` entries; new `authorized_keys` entries; sharing services
  (Remote Login, Screen Sharing, Remote Management) turned on unexpectedly; Full Disk Access, Accessibility,
  or Screen Recording granted to an unknown app; SIP, Gatekeeper, or startup security lowered; unknown
  trusted root certificates; changed DNS, proxy, or `/etc/hosts`; XProtect malware alerts; unexpected
  outbound connections; or browser extensions nobody installed.
- **Contain by isolating the network, not by powering off.** Turn off Wi-Fi and unplug Ethernet (or block
  the Mac at the router, with approval). Keep it powered on and logged in: shutting down loses memory and,
  with FileVault on, locks the data until someone unlocks it again. Don't log out the affected user.
- **Don't run "cleaner" or removal tools** before evidence is collected; they delete the artifacts needed
  for scoping.
- **Lost or stolen Mac:** use Find My to mark it as lost (locks it and shows a message). Erasing it
  remotely protects the data but ends any chance of locating it; that's the user's decision. Then treat
  every credential on it as exposed.
- If an unknown remote-access session is active, disconnecting the network ends it; record what was on
  screen first (photo or screenshot) if safe.

## Evidence to preserve (macOS-specific)

Collect with the user's approval, before changing anything. Copy evidence off the Mac to separate storage.
Several of these outputs contain personal data; treat them as sensitive and don't paste them into chats or
tickets whole.

- Version and state: `sw_vers`, `csrutil status`, `spctl --status`, `fdesetup status`, firewall state,
  `profiles status -type enrollment`, and the installed profiles list.
- Background items: `sudo sfltool dumpbtm` output, and copies of every non-Apple plist in
  `/Library/LaunchDaemons`, `/Library/LaunchAgents`, and each user's `~/Library/LaunchAgents`, with file
  timestamps and hashes (`shasum -a 256`). Record each referenced executable's path, hash, and code
  signature (`codesign -dv --verbose=4 <path>`, `spctl -a -vv <path>`). Don't delete them.
- Accounts and access: local users and admin group membership, `/etc/sudoers.d/` contents, every
  `authorized_keys` file (key comments and fingerprints via `ssh-keygen -lf`), sharing services state, and
  the Privacy & Security permission lists (screenshots are fine).
- Running state: `ps auxww`, `sudo lsof -nP -i`, `systemextensionsctl list`, loaded kernel extensions, and
  `launchctl list` for root and each user.
- Network settings: `scutil --dns`, `scutil --proxy`, `/etc/hosts`, VPN and network extensions, and trusted
  root certificates in the System keychain (certificate subjects and fingerprints only).
- Logs: the unified log is short-lived; export it early. `sudo log collect --last <period>` writes a log
  archive (not yet verified flags; check `man log`). `sudo sysdiagnose` collects a broad diagnostic bundle
  that includes logs and system state, but also much personal data; use it when the user agrees.
- Download and install history: `/Library/Receipts/InstallHistory.plist`, the quarantine events database
  (`~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2`, which records where downloaded
  files came from), recent items in `~/Downloads`, and shell histories (copy; don't print).
- Scheduled tasks: `crontab -l` for root and each user, and `/etc/periodic` additions.
- Snapshots: `tmutil listlocalsnapshots /` and the Time Machine backup list. Local snapshots and backups are
  both evidence and recovery; don't delete or thin them.
- Never dump the keychain or print stored passwords, even to check what was stolen. Record *which*
  accounts were stored, from the user's knowledge or the password manager's list.

## Scope checks specific to a Mac

- **Apple Account:** devices signed in (remove unknown ones), recent sign-ins and security notifications,
  and whether iCloud Keychain synced passwords to other devices. If the attacker had the Mac unlocked, they
  may have had iCloud Keychain, Messages, Mail, and Photos.
- **Browsers:** saved passwords, active sessions and cookies (session theft bypasses passwords and 2FA),
  and extensions in every installed browser and profile.
- **SSH keys and known_hosts:** every server the Mac's keys can reach; `known_hosts` lists where they were
  used.
- **Developer and cloud credentials:** Git hosting tokens, package-registry tokens, cloud CLIs,
  kubeconfigs, Docker registry logins, CI secrets in dotfiles.
- **Homelab systems the Mac administers or serves:** NAS shares and Time Machine destinations mounted with
  stored credentials, hypervisors, routers, and any device managed from this Mac. On an always-on server,
  every service it hosts and every system whose credentials it stores.
- **Docker Desktop:** containers, images, and volumes created around the time of compromise; containers
  with the Docker socket mounted.
- **Other Macs and Apple devices** on the same Apple Account, and other Macs with the same admin password
  or the same SSH keys.
- **Work:** any corporate account used on the Mac (email, chat, SSO sessions). Report to the employer.

## Eradication and recovery

- **Don't try to clean a compromised Mac in place** when persistence or privilege escalation is
  suspected. Erase and reinstall macOS from recoveryOS (or use Erase All Content and Settings where
  supported), after evidence is collected and backups of the user's *data* are confirmed.
- On Apple silicon, if firmware-level tampering is suspected, Apple supports reviving or restoring the
  Mac's firmware with Apple Configurator from a second Mac; this is a specialist step. Verify the current
  procedure in Apple's documentation.
- **Restore data, not the compromise.** Restoring a whole Time Machine backup or using Migration Assistant
  also restores launch agents, login items, apps, and profiles. Restore user files from a backup taken
  before the earliest plausible compromise, reinstall apps from the App Store or the developer's site, and
  reapply settings by hand.
- **Rotate credentials from a clean device:** Apple Account password (and review trusted devices and
  recovery contacts), local account passwords, the FileVault recovery key (re-enable FileVault on the
  rebuilt Mac to get a new one), SSH keys (new keys; remove the old public keys everywhere they were
  authorized), API and cloud tokens, Git and registry tokens, browser-saved passwords for important
  sites, VPN keys, and any service credentials stored on a server Mac. Sign out all browser sessions.
- **Before reconnecting:** current macOS, FileVault on, firewall on, only needed sharing services, no
  unknown profiles, login items, or privacy permissions, SIP and Gatekeeper at defaults, and a fresh
  encrypted backup started.

## Quick checklist tailored for a Mac

Start with the core quick checklist, plus:

- [ ] If it's a work Mac, contact the employer's IT or security team before changing anything.
- [ ] Disconnect Wi-Fi and Ethernet; keep the Mac on and logged in.
- [ ] Save `sfltool dumpbtm` output, copies of non-Apple launch plists, profiles, and the unified log.
- [ ] From a different, trusted device, change the Apple Account password and review signed-in devices.
- [ ] Plan to erase and reinstall, restore data only, and rotate every credential the Mac held.
