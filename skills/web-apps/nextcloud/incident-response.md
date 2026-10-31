# Nextcloud: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only Nextcloud-specific steps.

A compromised Nextcloud exposes far more than files: calendars, contacts, photo backups from phones,
stored passwords for external storage, and every sync client's session. In AIO, an attacker in the
AIO interface or mastercontainer controls the Docker host.

## Triage and containment

- **Indicators that point at Nextcloud:** integrity-check failures or unknown files in the server or app
  directories; admins or `admin`-group members nobody added; 2FA disabled for an account or enforcement
  turned off; apps installed or enabled that nobody chose; new public share links on whole folders, or
  links created by an account at odd times; new trusted servers or federated shares; brute-force
  protection turned off or the allowlist widened; new external-storage mounts; mass file changes,
  renames, or deletions synced from one client; logins from unknown addresses in `nextcloud.log`.
- **Cut the path in first, without wiping state:** remove the port forward, proxy route, or tunnel, or
  put the instance in maintenance mode (`occ maintenance:mode --on`), which stops users and sync clients
  while keeping everything in place. For AIO, also block the AIO interface ports (8080/8443) from all
  but the responder's management path.
- **Stop sync spreading damage.** If files are being encrypted or deleted, maintenance mode stops sync
  clients from pulling the changes. Tell users to disconnect desktop sync clients (don't let them
  "fix" by re-syncing).
- **Don't run an AIO update, AIO backup, or `files:scan` yet.** An update replaces containers (losing
  evidence in their writable layers), and a new backup may rotate out the last clean archive if
  retention is short.
- **If the AIO mastercontainer, the Docker socket, or the host is suspected:** treat the Docker host as
  compromised and switch to the host's skill and the [docker](../../containers/docker/SKILL.md) skill.

## Evidence to preserve (Nextcloud-specific)

Collect before changing anything. Treat logs, config, and data as sensitive.

- `nextcloud.log` (in the data directory or as configured), `audit.log` if the admin audit app is on,
  web-server and reverse-proxy access logs, copied off the host.
- `occ status`, `occ app:list`, `occ user:list`, `occ group:list`, admin-group members, and
  `occ integrity:check-core` output; integrity output for each enabled app.
- `occ config:list system` (redacted default output) and a protected copy of `config.php`, stored, not
  shared.
- The list of public and federated shares (from the admin's tools or a read-only database query),
  trusted servers, and external-storage mounts.
- Each affected user's *Devices & sessions* list (screenshots), and the activity stream for affected
  users.
- For AIO: `docker ps -a`, image digests of all `nextcloud-aio-*` containers, `docker logs` for the
  mastercontainer and the nextcloud container, and the AIO interface's backup list (screenshot).
- A database dump and a snapshot or copy of the data directory, taken in maintenance mode, kept separate
  from the existing backups.

## Scope checks specific to Nextcloud

- **Every device with a sync client or app password**: a stolen app password works without 2FA. Revoke
  and re-issue after eradication.
- **External storage back-ends** whose credentials Nextcloud stored (NAS shares, SFTP, object storage):
  check their logs for access from unexpected places and rotate their credentials.
- **Recipients of public links** created during the suspected window: assume the data behind them was
  read.
- **Federated partners and trusted servers.**
- **Phones' contacts and calendars** synced from the instance, if tampering with CalDAV/CardDAV data is
  possible.
- **The identity provider**, if SSO is used: new users, clients, or changed MFA there.
- **The Docker host and other containers on it**, for AIO and any container deployment.
- **Backups** reachable from the instance: the AIO Borg repository, NAS shares, cloud buckets. An admin
  in AIO could have deleted or replaced archives.

## Eradication and recovery

- Rebuild on a supported, current major from official sources (AIO mastercontainer image, official
  image, or vendor archive), not by cleaning the old install in place. Re-apply only reviewed
  configuration.
- Restore data from a backup taken before the earliest plausible compromise. For AIO Borg restores, the
  backup encryption key is required; for SSE, the encryption keys and the original `secret` are required.
  Check restored data for attacker-added shares, users, apps, and external mounts.
- **Rotate every secret:** database, redis, and mail passwords; external-storage credentials; all admin
  and user passwords; all app passwords and sessions; SSO client secrets; the AIO passphrase. Treat the
  instance `secret` as exposed too, but don't change it on a rebuild that restores old data without
  vendor guidance: stored credentials and server-side encryption depend on it.
- Re-review apps: reinstall only needed ones from the app store, at current versions.
- Before reopening: supported version, integrity check clean, 2FA enforced for admins at least, AIO
  interface not public, brute-force protection on with a minimal allowlist, link-share policy with
  passwords and expiry, the initial access path closed, and a fresh backup with an off-host copy.

## Quick checklist tailored for Nextcloud

When the user says "I think my Nextcloud has been hacked," start with the core quick checklist, plus:

- [ ] Put the instance in maintenance mode or remove its public route; block the AIO interface ports.
- [ ] Tell users to pause desktop sync and phone auto-upload.
- [ ] Copy `nextcloud.log`, proxy logs, and the app, user, and admin lists off the host; run the
      integrity check.
- [ ] Don't update, back up over, or rescan anything yet; protect the existing backups.
- [ ] List public shares, trusted servers, and external-storage mounts, and check those back-ends.
- [ ] Plan the rebuild and the rotation of every password, app password, and stored credential.
