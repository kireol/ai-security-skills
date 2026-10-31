---
name: homebridge
description: >-
  Security assessment, hardening, remediation, and incident response for Homebridge, the Node.js bridge
  that exposes non-HomeKit devices to Apple Home, including the Homebridge UI, the Homebridge Raspberry
  Pi image, the apt/hb-service install, and Docker. Use when auditing a Homebridge server's web UI
  (default port 8581) and its credentials, the npm plugin supply chain, child bridges, HomeKit pairing
  and setup codes, insecure (accessory control) mode, the service account and sudo rights, backups that
  contain pairing keys and plugin secrets, or when a Homebridge server may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Homebridge 1.x and 2.x with the Homebridge UI (homebridge-config-ui-x) 4.x and 5.x (verify the live versions; Homebridge 2 requires newer Node.js releases)"
  audience: "home, homelab"
  finding_prefix: "HB"
  modes: "discover, recommend, remediate, respond"
---

# Homebridge Security

Act as a careful, evidence-driven security engineer for a Homebridge server. Homebridge runs third-party
code from npm, written by hundreds of independent authors, with the credentials of the household's
cloud accounts (cameras, thermostats, garage doors, locks, alarm systems) in its configuration file, and
presents the result to Apple Home as trusted accessories. Its web UI can install code, edit that
configuration, and often open a terminal. Identify, explain, prioritize, remediate (only when
authorized), and verify weaknesses in Homebridge itself, its plugins, the host it runs on, and the data
it keeps.

## How to use this skill

This skill holds only Homebridge-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Homebridge-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
is in [references.md](references.md). Related skills: [home-assistant](../home-assistant/SKILL.md) (often
run alongside, and can also bridge to HomeKit), [smart-home-devices](../smart-home-devices/SKILL.md) (the
devices and cloud accounts the plugins control), [mqtt](../mqtt/SKILL.md) (if plugins use a broker),
[linux](../../operating-systems/linux/SKILL.md) (the host), and
[docker](../../containers/docker/SKILL.md) (container installs).

## Homebridge-specific principles

- **The UI is an admin console for the host.** From the Homebridge UI an administrator can install any
  npm package, edit `config.json`, restart the service, download backups, and, on many install types,
  open a web terminal as the service account. With the passwordless `sudo` rights that some installs
  grant, that is root on the host. Treat UI admin access as host access.
- **Default credentials are documented.** The Homebridge UI's README states that the default username
  and password are `admin` / `admin`; the Homebridge Raspberry Pi image's getting-started page says the
  same for the UI. Newer installs may ask for an account at first launch (verify on the live version).
  Either way, any account still using the default is a finding, and any UI reachable without a
  login (`auth` set to `none`) is a worse one.
- **The UI listens on every interface by default.** The documented `host` option defaults to `0.0.0.0`,
  and the UI is plain HTTP on port 8581 unless TLS is configured. Every device on the LAN can reach the
  login page, and credentials cross the network in clear text.
- **Plugins are unvetted third-party code.** Homebridge marks some plugins as "verified" after a review
  of basic quality and behavior; that is not a security audit. Every plugin runs with the service
  account's rights, can read the whole `config.json` (including other plugins' secrets), and updates
  pull new code from npm. Plugin choice is a supply-chain decision (see the
  [docker](../../containers/docker/SKILL.md) and core triage guidance on third-party code).
- **`config.json` and the storage folder are secrets.** The configuration usually holds cloud-account
  usernames and passwords, API tokens, and camera stream URLs with credentials. The `persist/` and
  `accessories/` folders hold HomeKit pairing keys. Never print, paste, or upload them whole; read only
  what you need and redact.
- **HomeKit pairing keys make a Homebridge bridge "the" accessory.** Anyone with a copy of the storage
  folder (including a UI backup archive) can impersonate the bridge to the household's Apple Home and
  control every accessory it exposes. Backups must be treated like the live secrets.
- **Insecure mode is an unauthenticated control API.** Running Homebridge with `-I` ("insecure", needed
  for the UI's accessory-control feature and some plugins) lets clients on the network read and set
  accessory states over the HomeKit Accessory Protocol port using only the setup PIN; the UI's own
  documentation warns that anyone with network access to the port and PIN can control accessories.
  Garage doors and locks make this a serious exposure.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Homebridge Raspberry Pi image** (flashed with Raspberry Pi Imager) | `homebridge.local` on mDNS; a "Homebridge WiFi Setup" hotspot on first boot without Ethernet; `hb-config` tool on the console. | Debian-based Raspberry Pi OS with the apt package preinstalled. From release 1.4.0 the local OS account is created at first boot (or through Imager customisation); check that account's password and SSH settings. OS updates are the owner's job. |
| **apt package on Debian/Ubuntu** (hb-service) | `homebridge` package installed; storage path `/var/lib/homebridge`; `hb-service` and `hb-shell` commands; a `homebridge` systemd service. | Runs as a dedicated service account (verify which user on the live system). `apt upgrade` updates Node.js, Homebridge, and the UI together and overwrites local changes to them. Check sudoers entries for the service account. |
| **npm global install with hb-service** (Linux, macOS, Windows) | Installed with `npm install -g`; `hb-service install`; storage under the user's home folder. | May run as the installing user (often an everyday or admin account) or root; Node.js updates are manual. |
| **Docker** (official `homebridge/homebridge` image) | A `homebridge` container, usually with `network_mode: host` (needed for mDNS); a bind-mounted `/homebridge` volume. | Host networking means the UI and every HAP port are on the host's interfaces. Container updates replace Homebridge and the UI; plugins live in the volume. Docker group membership on the host is root-equivalent. |
| **NAS or appliance packages** (community-packaged) | Installed from a NAS app catalog. | Packaging, Node.js version, run-as user, and update timing depend on the packager. Check what is actually running. |
| **HOOBS** and other forks | HOOBS branding; UI on another port (HOOBS used 8080). | Separate projects with their own lifecycle; the original HOOBS packaging is deprecated. Treat an unmaintained fork as end of life. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **TCP 8581:** the Homebridge UI's documented default port, plain HTTP unless TLS is set up; the page
  title is Homebridge and shows a login form (or, if `auth` is `none`, the dashboard directly, which is
  itself a finding).
- **mDNS/DNS-SD:** the main bridge and each child bridge advertise a HomeKit Accessory Protocol service,
  `_hap._tcp`, on UDP 5353, each on its own TCP port (the main bridge's port is set in `config.json`;
  child bridges get their own). The Raspberry Pi image also answers as `homebridge.local`.
- **Several `_hap._tcp` services from one IP address** are a strong hint of a bridge with child bridges.
- The host is usually a Raspberry Pi, mini PC, NAS, or Docker host: a MAC vendor (OUI) registered to
  Raspberry Pi is common but not specific to Homebridge.
- Often found near Home Assistant (TCP 8123) and an MQTT broker (TCP 1883/8883).

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer the Homebridge UI as an admin (the user signs in and shares screenshots), or read-only commands on
the host. Candidate commands, each **not yet verified** on every install type; check they exist first:

```sh
hb-service status 2>/dev/null || systemctl status homebridge --no-pager   # service state and user
ps -o user,pid,cmd -C node                     # which account runs Homebridge (look for -I in the args)
node --version                                 # Node.js version (Homebridge 2 needs a supported LTS)
sudo -l -U homebridge                          # sudo rights of the service account (name may differ)
ls -la /var/lib/homebridge                     # storage path on apt installs; check ownership and modes
ss -tlnp | grep node                           # listening ports owned by Node.js
dns-sd -B _hap._tcp local.                     # macOS; on Linux: avahi-browse -rt _hap._tcp
```

- Read `config.json` only to answer specific questions (UI `port`, `host`, `auth`, `ssl`, bridge `port`,
  plugin list, child-bridge settings), and redact every credential, token, PIN, and URL before quoting
  anything. Prefer `jq` with specific keys over printing the file:

```sh
jq '{ui: (.platforms[] | select(.platform=="config") | {port, host, auth, ssl: (.ssl != null)}),
     bridge: (.bridge | {port, advertiser})}' /var/lib/homebridge/config.json
```

- **Never** test the default `admin` password or any guessed password, use the UI terminal, install or
  update plugins, download a backup, read the `persist/` or `accessories/` folders, pair with the bridge,
  or send accessory-control requests to a HAP port.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, versions, and lifecycle

- Homebridge, Homebridge UI, and Node.js versions (shown on the UI dashboard). Homebridge 2 dropped older
  Node.js releases; a Node.js version past its upstream end of life is a finding.
- Install type (variant table) and how updates happen: UI-driven, `apt`, container image, or manual npm.
  Who applies them and when they last ran.
- The host OS and its updates (the [linux](../../operating-systems/linux/SKILL.md) skill), especially on
  the Raspberry Pi image, where the OS is the owner's responsibility.
- Homebridge and UI security advisories on the projects' GitHub security pages and release notes; check
  each plugin's repository for advisories (core triage). Don't rely on memory.

#### B. UI authentication and accounts

- UI users: is any account still `admin` with the default password (ask the user; don't test)? Named
  admin accounts; non-admin users where the UI supports roles; stale users.
- `auth` setting: `form` (default) or `none`. `none` is a finding unless the UI is reachable only from
  the host itself.
- 2FA: the Homebridge UI offers optional two-factor authentication for UI users (verify on the live
  version); is it on for admins?
- Session timeout (`sessionTimeout`, default 8 hours) and whether the UI is left signed in on shared
  devices.
- Strong, unique passwords stored in a password manager.

#### C. Network exposure and remote access

- UI `host` binding: `0.0.0.0` (default, all interfaces) or a specific address; IPv6 too.
- TLS: `ssl` configured, or plain HTTP across the LAN. If a reverse proxy fronts the UI, whether
  `proxyHost` is set and whether the proxy adds its own authentication.
- Router port forwards, UPnP mappings, tunnels, or VPN routes that reach the UI or any HAP port from the
  internet. Homebridge doesn't need inbound internet access for Apple Home remote access; that goes
  through a home hub (Apple TV, HomePod) and Apple's servers.
- Network segment: which devices can reach the host. Plugins often need to reach devices on an IoT
  segment and cloud services; the UI only needs to be reachable from admin devices.
- Host firewall rules for 8581 and the HAP ports.

#### D. Plugins and supply chain

- Every installed plugin: npm package name, publisher, version, "verified" status, last release date,
  repository activity, weekly downloads, and whether it is still needed.
- Flag: unverified plugins with few users; abandoned plugins; plugins installed from a tarball, git URL,
  or private registry; scoped or misspelled names that imitate popular plugins; plugins with postinstall
  scripts the user hasn't reviewed (the [docker](../../containers/docker/SKILL.md) skill's supply-chain
  thinking applies).
- Plugins that start their own web servers or open listening ports (some expose dashboards, webhooks, or
  camera streams).
- Automatic plugin updates on or off, and whether updates are reviewed.
- Which plugins control safety-relevant devices (locks, garage doors, alarms, heating).
- Child bridges: which plugins run as child bridges (isolates crashes and gives each its own HAP port
  and pairing; it is not a security sandbox, since child bridges still run as the same user).

#### E. HomeKit pairing, setup codes, and insecure mode

- Whether the main bridge and each child bridge are paired to the household's Apple Home, and whether
  any are unpaired (an unpaired bridge on the network can be paired by anyone on the LAN who has its
  setup code or QR code).
- Where the setup code is visible: the UI dashboard shows it to any signed-in user; it sits in
  `config.json`; it may appear in screenshots or forum posts. A setup code that was ever shared publicly
  should be changed (with a re-pair).
- Whether Homebridge runs with `-I` (insecure mode, often enabled for the UI's accessory control).
  Insecure mode plus a known PIN means unauthenticated control from the LAN.
- Apple Home: which people and devices have access to the home (Apple Home's own sharing settings).

#### F. Host, service account, and terminal

- Which user runs Homebridge. Root is a finding. A dedicated service account is expected; an everyday
  user account that also holds the owner's SSH keys or files is a finding.
- `sudo` rights of the service account: the UI's `sudo` option needs passwordless sudo, and Homebridge's
  documentation suggests `homebridge ALL=(ALL) NOPASSWD: ALL` for it. That makes every plugin and UI admin
  root-equivalent. Note what is granted and whether narrower rules would do.
- Web terminal in the UI: available or not on this install type, and who can use it.
- File ownership and permissions of the storage folder: readable by other local users?
- SSH on the host: enabled, key-only, password set on the Raspberry Pi image's local account.
- Docker: `network_mode: host`, `privileged`, device mounts, and who can run Docker on the host.

#### G. Backups and data protection

- The UI's scheduled backups (daily by default; `scheduledBackupPath`, or disabled with
  `scheduledBackupDisable`): where they are written, who can read them, and whether they leave the host.
- Backup archives contain `config.json` (all plugin credentials) and pairing keys. Check that they are
  stored encrypted or in an access-restricted location, not on a widely shared NAS folder or cloud
  drive.
- A restore test: can the household rebuild Homebridge without re-pairing every accessory? (A tested
  restore is the difference between a ten-minute and a weekend outage.)
- SD-card health on Raspberry Pi installs (cards fail; backups matter).

#### H. Monitoring and logging

- Logs (the UI log view, `journalctl -u homebridge`, or the container log): who can read them, whether
  plugins write credentials or tokens to them (some do in debug mode), and whether debug mode is left on.
- Notifications for UI logins or plugin changes (usually none; the UI's audit features are limited, so
  host-level logging and file-change monitoring matter more).
- Time sync on the host.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Apple Home automations and scenes** depend on accessories keeping their identity. Changing the bridge
  username (MAC-style ID), resetting pairing, or moving plugins between the main bridge and child bridges
  can make accessories reappear as new ones and break every automation, scene, and room assignment.
- **Plugins with cloud accounts** may lock the account or need re-authentication if credentials change.
- **Home Assistant or other tools** that call Homebridge (or the UI's accessory-control API) break if
  insecure mode is turned off.
- **Network changes:** moving the host to another segment needs mDNS reflection to the home hubs' network
  and rules to the devices the plugins control.
- **Service-account and sudo changes** can break UI-driven updates, restarts, and plugin installs that
  relied on passwordless sudo.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Default `admin` password | Create a named admin with a strong password; remove or change `admin`. | Update any saved logins. |
| `auth: none` | Set `auth` back to `form`. | Users must sign in. |
| UI on all interfaces over HTTP | Bind to the admin network or put it behind an authenticated HTTPS reverse proxy; or enable TLS. | Bookmarks change; proxy needs maintenance. |
| UI or HAP port reachable from internet | Remove the forward or tunnel; use a VPN for remote admin. | Remote UI access needs a VPN. |
| Insecure mode on | Turn off `-I` unless an integration needs it; if needed, restrict the HAP port to that integration's host. | UI accessory control and some plugins stop working. |
| Unverified or abandoned plugin | Replace with a maintained or verified alternative, or remove. | Accessories from it disappear from Apple Home. |
| Auto-updating plugins blindly | Update deliberately after reading release notes; keep a backup. | More manual work. |
| Passwordless `sudo ALL` | Remove; grant only the specific commands needed, or update from the host. | UI-driven OS actions or installs may stop. |
| Running as root | Move to a dedicated service account (hb-service supports this). | File ownership must be migrated; C2. |
| Unpaired bridge | Pair it to the household's home, or disable it. | None if unused. |
| Setup code exposed | Change the PIN (and bridge username) and re-pair. | Automations for those accessories must be rebuilt. |
| Backups on a shared location | Move to a restricted or encrypted location; prune old ones. | Restore procedure must be documented. |
| End-of-life Node.js | Upgrade Node.js per Homebridge's supported list. | Some old plugins may break. |

Group the plan: immediate containment (if any) → urgent fixes (internet exposure, default credentials,
`auth: none`) → high-priority hardening (insecure mode, sudo, plugin review, backups) → routine
maintenance (updates) → optional defense in depth (TLS, segmentation). Then ask for approval (core: modes
and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Homebridge specifics:

- **Take a UI backup first** (and store it securely), and copy `config.json` before any edit. Restoring
  a backup is the rollback for most changes.
- **Use the UI's settings and the plugin settings forms, or edit `config.json` with a JSON check.** A
  syntax error stops Homebridge from starting. Validate with `jq . config.json` before restarting.
- **Restarts are C2:** every accessory goes "No Response" in Apple Home until Homebridge is back, and
  locks or garage doors can't be operated during the gap. Choose a quiet time.
- **Never change the bridge `username` or PIN casually.** It forces a re-pair and breaks automations
  (C3 for the household's Apple Home configuration). Do it only to fix an exposed setup code, with the
  user's decision.
- **Plugin removal is C2**, and C3 if the plugin's cached accessories and their automations matter.
- **Account changes:** create and test the new admin in a separate browser session before removing the
  old one.
- **Service-account changes** (from root to a service user, sudo rules) are C2: follow Homebridge's
  documented hb-service procedure for the install type, then confirm restarts and updates still work.

After each change, follow the core "after a change" steps: check the UI dashboard shows Homebridge
running, check accessories respond in Apple Home, re-run the affected Discover checks, and record before
and after.

### Hard stops (refer to a specialist or the owner; never automate)

- Deleting `persist/`, `accessories/`, or the cached-accessories files to "fix" a problem: that resets
  pairing and destroys the household's automations.
- Pairing or unpairing the bridge with Apple Home on the user's behalf.
- Installing plugins from outside npm or from unreviewed sources to replace a removed one.
- Uploading `config.json`, logs, or backups to forums, issue trackers, or AI tools without redaction.

---

## Respond

On any P0 indicator (plugins nobody installed, UI users nobody created, `config.json` changes nobody
made, an unknown controller in Apple Home or accessories operating on their own, the UI reachable from
the internet with default or weak credentials, a plugin reported as malicious, or unexpected processes or
outbound connections from the Homebridge host), switch to Respond immediately. Follow the core playbook
plus the Homebridge-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### HB-001: Homebridge UI reachable on the whole LAN with the default password, plus passwordless sudo

**Confidence:** Confirmed
**Priority:** P1. Any device on the LAN, including a compromised IoT device, can sign in to the UI with
a vendor-documented default and use the terminal or a plugin install to run commands as root on the host;
the plugins hold the household's camera and garage-door cloud credentials.
**State:** Open
**Component:** Homebridge on a Raspberry Pi (Raspberry Pi image, apt install); Homebridge UI 5.x.
**Evidence:** Observed 2026-06-08: TCP 8581 open on `192.0.2.30` from `192.0.2.50`; the login page loads
over plain HTTP. The user confirmed (no login was attempted by the agent) that they sign in as `admin`
with the default password. `sudo -l -U homebridge` shows `(ALL) NOPASSWD: ALL`. `config.json` UI block:
`host` not set (defaults to all interfaces), no `ssl`.
**Expected secure state:** a named admin with a strong password; UI reachable only from the admin
network or through an authenticated HTTPS proxy; the service account without blanket passwordless sudo
(Homebridge UI documentation; core principle of least privilege).
**Exposure and prerequisites:** network access to `192.0.2.30:8581`; no other prerequisite.
**Dependencies / blast radius:** the user updates Homebridge from the UI, which relies on sudo; one
Home Assistant automation calls the UI's accessory-control API.
**Recommended remediation:** (1) create a named admin, sign in with it, remove `admin`; (2) restrict the
UI to the admin VLAN with a host firewall rule; (3) replace the blanket sudo rule with apt-based updates
run by the owner over SSH. Review insecure mode separately (HB-002).
**Operation class:** C2 (account and access changes; sudo change affects update workflow).
**Approval required:** Yes, separately for each step.
**Verification:** the old login fails; the new admin works; 8581 refused from a non-admin test host;
`sudo -l -U homebridge` shows no blanket rule; Homebridge restarts and accessories respond.
**Rollback:** restore the UI backup and the saved sudoers file.

---

## Version history

- **1.0** (2026-10-31): Initial version.
