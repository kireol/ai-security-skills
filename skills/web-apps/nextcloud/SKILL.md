---
name: nextcloud
description: >-
  Security assessment, hardening, remediation, and incident response for Nextcloud Server and Nextcloud
  All-in-One (AIO). Use when auditing a Nextcloud instance, reviewing its security and setup warnings,
  trusted domains and proxies, brute-force protection, two-factor enforcement, installed apps, public
  share links, federated sharing, server-side encryption, background jobs, updates, or the AIO
  mastercontainer and its admin interface, or when a Nextcloud instance may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Nextcloud Server (supported major versions; verify on the vendor's maintenance schedule) and Nextcloud All-in-One; also the community Docker image, snap, and NAS/appliance packages"
  audience: "home, work, homelab"
  finding_prefix: "NXC"
  modes: "discover, recommend, remediate, respond"
---

# Nextcloud Security

Act as a careful, evidence-driven Nextcloud security engineer. A Nextcloud instance is often the
household's or small office's file server, calendar, contacts, and photo backup at once, and it is
usually reachable from the internet because phones sync to it. Identify, explain, prioritize, remediate
(only when authorized), and verify weaknesses that could expose that data through the web interface,
share links, sync clients, installed apps, the host, or the AIO management layer.

## How to use this skill

This skill holds only Nextcloud-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Nextcloud-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

Related skills: the reverse proxy and TLS in front of Nextcloud are assessed with
[web-servers](../../web/web-servers/SKILL.md); the container host with
[docker](../../containers/docker/SKILL.md); tunnels and edge access with
[tunnels](../../edge/tunnels/SKILL.md) and [cloudflare](../../edge/cloudflare/SKILL.md); SSO with
[identity-providers](../../identity/identity-providers/SKILL.md); off-host backups with
[backup-tools](../../storage/backup-tools/SKILL.md).

## Nextcloud-specific principles

- **The admin overview is an input, not the verdict.** *Administration settings → Overview* shows
  "Security & setup warnings" (the same checks as `occ setupchecks`). Run it, record every warning, and
  validate the important ones independently. It doesn't see router exposure, the AIO interface, share
  links, or backup independence.
- **`config.php` holds secrets.** It contains the instance `secret`, `passwordsalt`, database and
  mail credentials, and object-storage keys. The `secret` decrypts stored credentials (for example the
  login passwords kept with app tokens and external-storage passwords). Read only the keys you need, and
  never print the file whole.
- **Use `occ`, the admin UI, or AIO's interface to change settings.** Hand-editing `config.php` is
  supported for some keys, but a syntax error takes the instance down. In AIO, many settings are managed
  by the mastercontainer and are overwritten on restart; change them the AIO way.
- **AIO adds a second, more powerful admin plane.** The AIO mastercontainer mounts the Docker socket so
  it can create and update the other containers. Whoever controls the AIO interface controls every
  Nextcloud container, the backups, and, through the socket, effectively the Docker host.
- **Apps are code running with the server's rights.** Signed apps prove who published an update, not
  that anyone reviewed the code. Each enabled app is attack surface; non-official apps are the weakest
  link.
- **Share links are credentials.** Anyone holding a public link has the access it grants. Treat the list
  of active public shares as part of the access-control review, not as user content.
- **Verify against the installed major version.** Settings names, defaults, and menus change between
  majors, and only recent majors receive security fixes. Check the vendor maintenance schedule rather
  than assuming.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Nextcloud AIO** | A `nextcloud-aio-mastercontainer` container plus `nextcloud-aio-*` containers (apache, nextcloud, database, redis, and optional ones such as talk, collabora, imaginary, borgbackup). AIO interface on port 8080 (self-signed) or 8443. | Updates, backups, and optional services are driven from the AIO interface. The mastercontainer has the Docker socket. Some `config.php` values are managed by AIO. Built-in BorgBackup holds an encryption key shown only in the AIO interface. |
| **AIO behind a reverse proxy** | AIO started with `APACHE_PORT` (the docs use `11000` as the example) and `APACHE_IP_BINDING`; no AIO-managed ports 80/8443. | The proxy terminates TLS and must pass the right forwarded headers. If `APACHE_IP_BINDING` is `0.0.0.0`, the Apache port is reachable directly from the LAN, bypassing the proxy. The AIO interface on 8080 still needs its own restriction. |
| **Community Docker image** (`nextcloud`, Apache or FPM variants) | A `nextcloud` image with a separate database (and often redis) container, usually behind a proxy. | Updates mean pulling a new image and letting the upgrade run; skipping major versions is not supported. Cron must be set up separately (sidecar container or host cron). |
| **Bare-metal / VM install** (web server + PHP + database) | Nextcloud files under the web root; `occ` run as the web-server user. | PHP, web server, and OS patching are the operator's job. Data and config locations relative to the web root matter. |
| **Snap, NAS package, or appliance** (snap, TrueNAS/Unraid apps, NAS package centers, prebuilt images) | Platform-managed install; paths and `occ` wrappers differ. | Updates and file locations depend on the packager, who may lag upstream. Assess the platform with its own skill. |
| **Managed hosting** | Instance hosted by a provider. | Server, PHP, and update hardening are the provider's; users, apps, sharing, 2FA, and shares remain the customer's. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- An HTTP/HTTPS service whose login page title is the instance name or "Nextcloud", with Nextcloud
  assets under `/core/` and `/apps/`.
- `GET /status.php` returns JSON with `installed`, `version`, `versionstring`, and `productname`. It
  answers without login and is the fastest way to read the version.
- CalDAV/CardDAV discovery redirects at `/.well-known/caldav` and `/.well-known/carddav` to
  `/remote.php/dav/`.
- **AIO:** the AIO interface on port 8080 with a self-signed certificate, or 8443 with a valid
  certificate; Nextcloud itself on 443 (TCP, and UDP for HTTP/3); the Talk TURN server on 3478 TCP/UDP
  (changeable with `TALK_PORT`); port 80 for the ACME HTTP challenge. Behind a proxy, the Apache
  container on whatever `APACHE_PORT` is set to.
- Container names starting with `nextcloud-aio-` or images named `nextcloud`.
- MAC address vendors don't help: Nextcloud runs on general-purpose hosts, VMs, containers, and NAS
  devices.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the admin UI and `occ`. These are *candidate* read-only commands. `setupchecks`,
`security:bruteforce:attempts`, `background-job:list`, and `status` are **vendor-documented**; the
others are listed in the vendor occ reference but **not yet verified** on every major version, so check
`occ list` first.

```sh
# Run occ as the web-server user. Bare metal: sudo -E -u www-data php occ <cmd>
# AIO: sudo docker exec --user www-data -it nextcloud-aio-nextcloud php occ <cmd>
# Community image: docker exec --user www-data <container> php occ <cmd>
occ status --output=json_pretty          # version, maintenance mode, installed
occ setupchecks --output=json_pretty     # same checks as "Security & setup warnings"
occ app:list                              # enabled and disabled apps, with versions
occ user:list                             # accounts
occ group:list                            # groups (who is in "admin")
occ twofactorauth:state <uid>             # 2FA status for one user
occ background-job:list --limit 50        # queued background jobs
occ security:bruteforce:attempts <ip>     # throttle state for one address
occ config:list system                    # system config; sensitive values are redacted by default
occ integrity:check-core                  # code integrity against signatures
occ update:check                          # available server and app updates
curl -s https://<nextcloud-host>/status.php
```

- **Never pass `--private` to `occ config:list`.** It prints passwords and secrets. Confirm on the
  installed version that the default output redacts them before sharing it.
- Read `config.php` keys individually (`occ config:system:get <key>`) for non-secret values such as
  `trusted_domains`, `trusted_proxies`, `overwriteprotocol`, `allowed_admin_ranges`, and `loglevel`.
- **Never** during Discover: enable or disable apps, change sharing or 2FA settings, run
  `maintenance:repair`, `files:scan`, `encryption:*`, or upgrade commands; log in to the AIO interface
  with the passphrase without the user present; trigger AIO backups or updates; open other users'
  files; or create share links to "test" them.
- The vendor's online security scan checks a public instance from outside using public information
  only. Running it sends the hostname to a third party; ask first.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, version, and lifecycle

- Deployment variant, Nextcloud major and minor version, PHP version, database type and version, and the
  OS or image underneath.
- Installed major vs. the vendor maintenance schedule: majors are released several times a year and each
  is supported for about one year; an end-of-life major gets no security fixes (core triage,
  end-of-life). Verify the current list on the schedule page.
- Pending server and app updates (`occ update:check`, admin overview). Nextcloud security advisories
  (the vendor's GitHub advisory repository) for the installed server and app versions.
- `occ integrity:check-core` and app integrity warnings in the admin overview: unexpected modified or
  extra files are a possible tamper indicator (P0 if not explained by a manual patch).
- All "Security & setup warnings": missing HTTPS, missing security headers, `.well-known` redirects,
  outdated PHP, the data directory reachable from the web, missing background-job runs, and similar.

#### B. Identity, administration, and 2FA

- Members of the `admin` group and any group delegated admin rights (*Administration privileges*).
  Shared admin accounts, admins who also use the account daily, stale admins.
- **2FA:** which providers are enabled (TOTP, WebAuthn/passkeys, backup codes); whether 2FA is
  *enforced* (*Administration settings → Security*), for everyone or for selected groups, and which
  groups are excluded. Admins should never be excluded.
- App passwords and sync-client sessions per user (*Personal settings → Security → Devices &
  sessions*): count and age, not values. App passwords are how sync clients authenticate; old ones from
  lost phones are live credentials.
- SSO (OIDC/SAML apps): which identity provider, whether it enforces MFA, whether local password login
  remains available for everyone or only for a break-glass admin, and whether auto-provisioning creates
  accounts for anyone the provider authorizes.
- `allowed_admin_ranges`: restricts admin actions to listed networks (documented hardening option).
- Self-registration apps (for example a registration app) or guest-account apps: enabled? Who can sign
  up?
- Password policy app settings (minimum length, breached-password check). Never test users' passwords.
- Login history in the log or activity stream: unfamiliar sources, failures, new devices.

#### C. Network exposure, trusted domains, and proxies

- Every path in: port forwards, reverse-proxy routes, tunnels, VPNs, IPv6, and the AIO ports. Which
  are reachable from the internet, the LAN, and guest/IoT segments.
- **AIO interface (8080/8443):** should never be reachable from the internet. The vendor recommends
  putting it behind a VPN or limiting its exposure. The direct passphrase login is blocked while
  Nextcloud runs (and after a login, 5 minutes, or 5 wrong passphrases), but that is not a reason to
  expose it. Check the host firewall and router for 8080/8443.
- **`trusted_domains`:** lists only the names users really use; no wildcard catch-alls or stray IPs
  from setup. A "Trusted domain error" in logs means someone used a name not on the list.
- **`trusted_proxies` and `forwarded_for_headers`:** list only proxies you control. Wrong values let
  clients spoof their address (defeating brute-force protection and logs); missing values make every
  request appear to come from the proxy, so brute-force throttling hits everyone.
- `overwriteprotocol`, `overwritehost`, `overwrite.cli.url` consistent with the public URL; HTTP
  redirected to HTTPS; HSTS sent (the vendor example is `max-age=15552000; includeSubDomains`).
- **Bypass paths:** the Apache/PHP container or port reachable directly (AIO `APACHE_IP_BINDING=0.0.0.0`,
  a published container port) when access is meant to go through the proxy.
- Talk TURN port (3478) exposed only if Talk is in use.
- Data directory not reachable over HTTP (the setup check tests this) and, on bare metal, outside the
  web root.

#### D. Brute-force protection and logging of logins

- Brute-force protection is on by default; `auth.bruteforce.protection.enabled` set to `false` is a
  finding on any reachable instance.
- Brute-force allowlist (*Administration settings → Security*, from the `bruteforcesettings` app):
  should contain only specific trusted addresses, never a whole LAN or a proxy address that every
  request comes through.
- `loglevel` at 2 (warning) or lower so failed logins reach `nextcloud.log`, which fail2ban or CrowdSec
  can read. `audit.log` (admin audit app) logs successful logins only.
- Whether fail2ban, CrowdSec, or the proxy adds rate limiting in front.

#### E. Apps

- Every enabled app (`occ app:list`): needed? Official, or from a third-party developer? Maintained for
  the installed major? Pending updates? Apps installed outside the app store (copied into an `apps`
  directory)?
- High-risk app types: external storage (stores credentials for SMB, SFTP, S3, and other back-ends),
  apps that run commands or workflows, apps that add public endpoints or registration, office or media
  integrations that call other servers, and AI assistant apps that send content to an external provider.
- Apps disabled by an upgrade because they're incompatible: still installed, may be re-enabled with old
  code.
- App-store channel (beta or experimental apps enabled?).

#### F. Sharing: public links, internal, and federated

- *Administration settings → Sharing*: public link sharing allowed? **Enforce password protection** on
  links? **Default and enforced expiration** for link shares? **Public uploads** allowed? Resharing
  allowed? Groups excluded from creating link shares?
- The inventory of existing public shares: count, owners, links without passwords or expiry, links to
  whole folders or to the root of a user's files, upload-enabled links (File Drop), and very old links.
  Use the admin's tools or the database read-only; don't open the shared content.
- **Federated sharing:** outgoing and incoming federated shares allowed? Which *trusted servers* are
  listed (they exchange user directories)? Automatic acceptance of incoming shares? Whether user data is
  published to a lookup server (verify the setting name on the installed version).
- Email sharing and the "share with users not in my groups" restrictions.
- Guest or "talk public conversation" features that grant access without an account.

#### G. Server-side encryption, data location, and secrets

- **Server-side encryption (SSE):** enabled? Master-key (default) or per-user keys? SSE protects mainly
  against an external storage provider reading the data. It does not protect against a Nextcloud admin
  or a compromised server, and it doesn't encrypt file names, folder structure, previews, versions, or
  trash. Losing the keys or the instance `secret` loses the data permanently.
- Whether encryption keys (`data/files_encryption`, `data/<user>/files_encryption`) and `config.php` are
  in the backups, and whether a restore from an encrypted backup has been tested.
- End-to-end encryption app: in use for specific folders? (Recovery depends on users' mnemonic keys.)
- Data directory: on which volume, permissions (web-server user only), and whether other services mount
  it (a share exported over SMB/NFS lets clients bypass Nextcloud's access control entirely).
- `config.php` permissions and whether it or `.env`/compose files with database passwords sit in
  readable locations or in git.

#### H. Background jobs, cron, and maintenance

- Background job mode: **Cron** is the vendor-recommended mode; AJAX (the default) runs jobs only when
  pages load and is unreliable beyond a single user; Webcron requires an externally reachable
  `cron.php`. Last successful run time (admin overview warns if stale). Stale jobs mean expired shares
  aren't cleaned, brute-force records aren't expired, and trash and versions grow.
- Who and what runs cron: the web-server user only; the cron entry or sidecar not writable by others.
- `maintenance_window_start` set so heavy jobs run off-hours (cron mode only).

#### I. Updates, backups, and recovery

- How updates arrive: AIO interface (optionally automatic after a daily backup), image pulls, the
  built-in updater, the package manager, or the platform. App updates separately.
- **AIO BorgBackup:** enabled? Destination on another disk or host? Last successful backup and the
  check result? The Borg encryption key saved outside the AIO host (without it, restores are
  impossible)? A test restore ever done? Can the Nextcloud host's admin delete every copy?
- Non-AIO: database dump plus data directory plus `config.php` plus encryption keys, taken consistently
  (maintenance mode or snapshot), with an off-host copy (see
  [backup-tools](../../storage/backup-tools/SKILL.md)).
- Recovery documentation: how admin access is regained if 2FA, SSO, or the proxy breaks.

#### J. Host and container layer (AIO and Docker)

- AIO mastercontainer: Docker socket mounted (required by design; the `:ro` flag doesn't limit the
  Docker API). That makes the AIO interface and the mastercontainer image part of the host's trust
  boundary. Its image pulled from the official publisher?
- `nextcloud_aio_mastercontainer` volume name unchanged (built-in backups depend on it).
- Community image: containers running as root vs. `www-data`, bind mounts, published ports, secrets in
  compose files (assess with [docker](../../containers/docker/SKILL.md)).
- Database and redis not published on host ports; database password not the example value.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Sync clients and mobile apps** (desktop sync, phone auto-upload, CalDAV/CardDAV on phones): they use
  app passwords or login flow tokens. Revoking sessions, enforcing 2FA, or changing the URL or proxy
  forces every device to re-authenticate; some older clients may not support new flows.
- **Recipients of existing share links:** enforcing passwords or expiry may not apply retroactively, or
  may break links in use; verify how the installed version treats existing shares and tell the user who
  will be affected.
- **External storage mounts and the other systems they reach** (NAS shares, object storage).
- **Federated partners** and trusted servers.
- **Integrations:** Collabora/OnlyOffice, Talk, calendar subscribers, scripts using WebDAV with app
  passwords, home automation or backup jobs reading files.
- **The reverse proxy and auth provider**, shared with other apps (use `web-servers` and
  `identity-providers`).
- **AIO:** changes in the AIO interface can restart every Nextcloud container at once.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| End-of-life major or pending security release | Upgrade one major at a time, after a verified backup, following release notes. | Apps may be disabled as incompatible; plan app replacements first. |
| Integrity check failures | Investigate before anything else (possible tampering); restore official files. | May reveal local patches that need re-applying properly. |
| AIO interface reachable from the internet | Block 8080/8443 at the router and host firewall; reach it over VPN or from the LAN only. | Remote administration needs the VPN. |
| 2FA not enforced | Enforce 2FA for all users, or at least the `admin` group first; ensure each user has backup codes. | Every user must enroll on next login; sync clients keep working with app passwords. |
| Stale app passwords and sessions | Revoke sessions for lost or retired devices. | Those devices must log in again. |
| Brute-force protection disabled or allowlist too broad | Re-enable; reduce the allowlist to specific addresses. | Fix `trusted_proxies` first, or users behind the proxy get throttled. |
| `trusted_proxies` / forwarded headers wrong | Set only the real proxy addresses and the header that proxy sets. | Wrong values can lock everyone out via throttling; test from outside. |
| Broad `trusted_domains` | Reduce to the names actually used. | Clients using a removed name stop working. |
| Public links without password/expiry | Enforce passwords and a default expiry for new links; review and expire old links with their owners. | Recipients need the password; owners must re-share some links. |
| Public uploads allowed | Disable unless File Drop is needed; if needed, limit to specific groups. | File-request workflows stop. |
| Unneeded or unmaintained apps | Disable, then remove after confirming no data dependency. | Features disappear; removal may delete app data (C3). |
| Federated sharing not used | Disable incoming and outgoing federation; remove trusted servers. | Existing federated shares stop working. |
| SSE enabled expecting protection from server compromise | Explain what SSE does; back up keys and `secret`; don't disable without the decrypt-all procedure. | Disabling requires `occ encryption:decrypt-all` in maintenance mode (C2/C3 risk). |
| Background jobs on AJAX | Switch to system cron (or the image's cron sidecar) every 5 minutes. | Needs a cron entry or container; small extra load. |
| No backup / no off-host copy / Borg key not saved | Enable AIO backup to another disk, add an off-host copy, store the Borg key in the password manager; test a restore. | Storage and time; restore tests take a maintenance window. |
| Data directory shared over SMB/NFS | Stop exposing it; use Nextcloud's own clients or external storage instead. | Clients that used the share directly must change. |

Changing ports, obscure hostnames, and geoblocking are supplementary only. Never recommend them as the
main fix.

Group the plan: immediate containment (if any) → urgent fixes (end-of-life or vulnerable version on an
exposed instance, AIO interface public, integrity failures, admins without 2FA) → high-priority hardening
(2FA enforcement, proxies and brute-force, share-link policy, apps) → routine maintenance (cron, updates,
backups) → optional defense in depth (`allowed_admin_ranges`, fail2ban). Then ask for approval (core:
modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Nextcloud specifics:

- **Back up first:** database dump, `config.php`, data directory (or a snapshot), and encryption keys if
  SSE is on. In AIO, run a backup from the AIO interface and confirm it succeeded.
- **Use `occ`, the admin UI, or the AIO interface.** Capture the prior value with
  `occ config:system:get <key>` or `occ config:app:get <app> <key>` before setting a new one. In AIO,
  don't hand-edit values AIO manages; check the AIO documentation for the supported variable.
- **2FA enforcement:** confirm at least one admin is enrolled and holds backup codes, and keep a second
  admin session open, before enforcing. Enforcement and SSO changes are **C2**.
- **Proxy and brute-force settings:** change `trusted_proxies` and `forwarded_for_headers` together, then
  check from an external address that the real client IP appears in the log. Wrong values can throttle
  every user (**C2**).
- **Upgrades:** one major at a time; read the release notes and app compatibility; maintenance mode is
  set by the upgrader. Never skip majors or downgrade as a fix. AIO handles the order itself; let it.
- **Apps:** disabling is **C1**; removing an app may delete its data (**C3**). Check first.
- **Share links:** changing the policy is C1; expiring or deleting existing links is C2 for the
  recipients; agree on the list with the share owners.
- **Encryption:** enabling SSE or running `encryption:decrypt-all` is a large, slow, data-touching
  operation; treat as **C3** with a verified backup and a maintenance window, and never run it as a
  routine hardening step.
- **AIO interface exposure:** close 8080/8443 at the router and host firewall; confirm the interface is
  still reachable from the management path (LAN or VPN) before ending the session.

After each change, follow the core "after a change" steps: re-run the admin overview's checks, test login
and sync from a client, check `nextcloud.log` for new errors, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Running `occ encryption:decrypt-all`, `encryption:enable`, key migration, or deleting
  `files_encryption` directories as part of security remediation.
- Resetting an AIO instance (removing its containers and volumes), or changing the
  `nextcloud_aio_mastercontainer` volume name; the vendor's reset steps delete all data.
- Restoring a Borg backup over a running instance without the user's explicit, fresh approval.
- Editing the database directly to change users, shares, or app settings.
- Deleting users or their files; transferring ownership of files without the owners' knowledge.
- Setting or resetting users' passwords or 2FA on their behalf without the user present (the admin may
  do it; the agent guides).
- Running `files:scan --all` or `maintenance:repair` on a large instance during an incident (it changes
  state that may be evidence).

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the Nextcloud-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### NXC-001: AIO interface reachable from the internet and admins not required to use 2FA

**Confidence:** Confirmed
**Priority:** P2. The AIO interface controls every Nextcloud container and, through the Docker socket,
the host; it is publicly reachable, and the two admin accounts have no second factor.
**State:** Open
**Component:** Nextcloud AIO (version as reported by `occ status`), AIO interface on port 8443,
`cloud.example.com`
**Evidence:** Observed 2026-03-04: the router forwards TCP 8443 to the AIO host `192.0.2.20`. With
approval, a request from `198.51.100.9` to `https://cloud.example.com:8443/` returned the AIO login page.
*Administration settings → Security* shows 2FA not enforced; `occ twofactorauth:state` for both members
of `admin` shows no provider enabled. The vendor AIO documentation recommends placing the AIO interface
behind a VPN or limiting its public exposure.
**Expected secure state:** AIO interface reachable from the LAN or VPN only; 2FA enforced at least for
the `admin` group.
**Exposure and prerequisites:** anyone on the internet who obtains or guesses the AIO passphrase while
Nextcloud is stopped, or any admin password, gains control.
**Dependencies / blast radius:** the owner uses the AIO interface from a laptop on the LAN; no one uses it
remotely. Both admins sync phones with app passwords, which keep working after 2FA enrollment.
**Recommended remediation:** remove the 8443 port forward (and 80 if it was only for the AIO
certificate); enforce 2FA for the `admin` group after both admins enroll and save backup codes; later,
enforce for all users.
**Operation class:** C2 (remote access path and authentication change).
**Approval required:** Yes.
**Verification:** external request to 8443 times out; LAN request still reaches the AIO interface; admin
login prompts for the second factor; phone sync still works.
**Rollback:** restore the port-forward rule from the captured router config (not recommended); disable
group enforcement in *Security* settings.

---

## Version history

- **1.0** (2026-10-31): Initial version.
