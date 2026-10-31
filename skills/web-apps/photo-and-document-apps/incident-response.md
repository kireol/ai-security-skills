# Photo and Document Apps: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only steps specific to Immich and Paperless-ngx.

Two kinds of harm matter here, and they need different first moves: **disclosure** (someone read or
downloaded photos or documents) and **destruction** (originals deleted, encrypted, or altered). For
disclosure, the data can't be taken back, so scoping who saw what drives the response. For destruction,
protecting the remaining copies and backups comes first.

## Triage and containment

- **Indicators:** admin or superuser accounts nobody created; OAuth-provisioned users nobody expected;
  new API keys or tokens; new shared links (especially on whole albums or many documents) created at odd
  times or by an account that doesn't normally share; partner sharing turned on; new mail accounts or
  mail rules, or rules changed to forward or delete; new workflows with webhook or email actions;
  settings changed (auto-login, remote-user auth, sign-ups, metadata on shared links); large downloads
  in proxy logs; mass deletions or trash emptied; unexpected files in the consumption folder; external
  libraries added that point at other host folders.
- **Cut the path in first:** remove the port forward, proxy route, or tunnel route. That also stops share
  links working, which is what you want during containment; tell the user so they can warn recipients.
- **Then stop the app containers, don't remove them** (`docker stop`, not `docker compose down` with
  volume removal), keeping the database container's data intact.
- **Stop data-moving jobs:** pause Paperless mail fetching (stop the worker if needed) so a malicious
  rule can't delete more mail; pause phone auto-backup on users' phones so they don't delete local
  copies after "successful" upload to a tampered server.
- **Protect backups:** disconnect or lock backup destinations the app host can write to, from a clean
  device.

## Evidence to preserve (app-specific)

Collect before changing anything. Don't open or copy user content beyond what the incident requires;
these files are personal data.

- Container logs for every service (`docker logs`), reverse-proxy access logs for the app's hostname
  (downloads and share-link hits by path and client address), and the host's auth logs. Copy them off
  the host.
- A database dump taken with the app stopped (Immich: users, API keys, shared links, albums, sessions;
  Paperless: users, tokens, share links, mail accounts and rules, workflows, document history).
- From the admin views, if safe: user list, API keys or tokens, active share links with their creation
  times, sessions or devices, Paperless mail rules and workflows. Screenshot anything unexpected.
- `docker inspect` (store, don't share; contains secrets), image digests, and the compose and `.env`
  files as they are now, plus the last known-good versions.
- Directory listings with timestamps (not contents) of the upload, media, and consumption folders, to
  establish when files changed.

## Scope checks specific to photo and document apps

- **What was shared or downloaded:** use proxy logs and the share-link list to determine which albums or
  documents were reachable, by whom, and when. Documents with identity, financial, or medical data may
  trigger obligations to notify banks, employers, or authorities; tell the user, and point them to the
  relevant identity-theft resources (core playbook).
- **The mailbox** connected to Paperless: if its password or OAuth grant was in the app, check the
  mailbox's own sign-in history, forwarding rules, and app grants; change the password or revoke the
  grant from a clean device.
- **The identity provider** (if OAuth/OIDC is used): new users, clients, or changed role claims.
- **Every system using an API key or token** from the app (scripts, photo frames, backup jobs).
- **Folders shared over SMB/NFS** that overlap the upload, media, or consumption folders, and the
  devices that can write them (a scanner or workstation may be the entry point).
- **The container host,** if containers ran privileged, mounted the Docker socket, or had broad host
  mounts.
- **Phones:** devices whose sessions were active; whether local photos still exist if the server copy
  was destroyed.

## Eradication and recovery

- Redeploy from the official images at a current, fixed version, with clean compose and `.env` files.
- Restore the database and originals from a backup taken before the earliest plausible compromise. For
  destruction, compare file counts and checksums where the backup tool supports it; restore to a new
  location first, never over the only remaining copy.
- **Rotate:** every user's password, all API keys and tokens, `PAPERLESS_SECRET_KEY`, database and Redis
  passwords, mail credentials and OAuth grants, OAuth client secrets at the identity provider.
- Delete every share link created during the suspected window, and review the rest with their owners.
- Remove attacker-added users, mail rules, workflows, and external libraries, after recording them.
- Before reopening: fixed version; no published supporting services; no direct-port bypass; MFA for
  admins; share-link policy agreed; backups verified with an off-host copy; the initial access path
  closed.

## Quick checklist tailored for photo and document apps

Start with the core quick checklist, plus:

- [ ] Remove the public route; stop (don't remove) the app containers; warn the user that share links
      will stop working.
- [ ] Pause Paperless mail fetching and phones' auto-backup; protect the backup destinations.
- [ ] Copy container and proxy logs and a database dump off the host.
- [ ] List share links, API keys, users, mail rules, and workflows; find what was exposed and when.
- [ ] Check the connected mailbox and identity provider from a clean device.
- [ ] Restore from a pre-compromise backup to a new location, rotate every secret, then reopen.
