# Self-Hosted Web Apps and Dashboards: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only steps specific to small self-hosted web apps.

A compromised dashboard or monitor is rarely the end goal. It's a stepping stone: it holds API keys and
passwords for other services, it may have the Docker socket (root on the host), and scanners have raw
network access to the whole LAN. Scope widely, even when the app itself looks unimportant.

## Triage and containment

- **Indicators that point at the app:** admin or user accounts nobody created; a first-user setup
  completed by someone else (you can't log in with your own account, or the app shows a stranger's
  admin); new monitors, scripts, plugins, webhooks, or notification targets; dashboard links that now
  point to unfamiliar sites; settings changed (authentication turned off, sign-up turned on); new
  containers on the host that the user didn't start; unexpected outbound connections from the app's
  container; or the app's logs showing logins from unknown addresses.
- **Cut the path in first:** remove the port forward, reverse-proxy route, or tunnel route to the app,
  or stop publishing its port. That stops new access without destroying evidence.
- **Then stop the container, don't remove it:** `docker stop` keeps its writable layer and logs for
  evidence; `docker rm` or `docker compose down` followed by `up` discards them.
- **Notification servers (ntfy, Gotify):** indicators include phishing-style notifications nobody sent
  ("log in here", "approve this"), new ntfy users, tokens, or ACL entries (especially for `everyone`),
  `auth-default-access` loosened, or new Gotify clients, applications, or plugins. Warn the people who
  get the notifications not to act on links or codes in them until the incident is closed. A new client
  token means someone may have read every past message; a new application token means someone can send
  fake ones.
- **CasaOS:** treat a compromised dashboard as a compromised host (it controls Docker and has a web
  terminal). Look for apps nobody installed, added third-party app-store sources, and new accounts.
  Contain at the host level using the `linux` skill and the core playbook.
- **If the app had the Docker socket, host networking, or privileged mode:** treat the container host as
  compromised (switch to that host's skill or the core playbook) and contain the host, not just the app.

## Evidence to preserve (app-specific)

Collect before changing anything. Treat configuration and data as secret.

- Container logs (`docker logs <container>`), the app's own log files in its volume, and the reverse
  proxy's access logs for the app's hostname. Copy them off the host.
- `docker inspect <container>` (contains environment secrets: store, don't share), `docker diff
  <container>` (files changed in the writable layer), and the image digest.
- A copy of the app's data volume (configuration, SQLite or other database, uploads), taken with the
  container stopped.
- The compose file or platform template as it is now, and the last known-good version (git history or
  backup) to compare.
- For a host with a mounted Docker socket: the list of all containers and images with creation times
  (`docker ps -a`, `docker images`), to find anything the attacker started.
- ntfy: the auth database (`auth-file`), the server config, and the output of `ntfy user list`,
  `ntfy access`, and `ntfy token list` (store securely; tokens are secrets). Gotify: its database
  (SQLite by default) and the list of users, clients, applications, and plugins. CasaOS: its
  configuration directory (`/etc/casaos/`, verify on the installed version), the list of installed apps
  and app-store sources, and the systemd journal for the `casaos*` services.
- From the app's UI or data, if safe: user list, recent logins, and the list of monitors, scripts,
  plugins, and integrations. Screenshot anything unexpected.

## Scope checks specific to self-hosted apps

- **Every service whose key or password was in the app** (dashboard widgets, monitor credentials,
  notification accounts): check those services' logs for use of the key since the earliest plausible
  compromise, and treat their keys as exposed.
- **The container host**, if the app had the Docker socket, privileged mode, or read-write host mounts.
- **The LAN**, if the app was a network scanner with raw-socket capabilities or host networking: look for
  ARP spoofing, new devices, and traffic from the app's host to systems it doesn't normally contact.
- **The identity provider**, if the app used SSO: check for new users or clients created there.
- **Other apps sharing the same volume, network, or `.env` file.**
- **Everything that sent through a notification server:** if messages carried codes, links, or hostnames,
  treat those as disclosed; if the attacker could publish, ask which notifications people acted on.
- **Every app CasaOS installed**, and the host under it.
- **Git repositories** holding the app's configuration, if they also held keys.

## Eradication and recovery

- Redeploy from a known-good image (pinned to a current version, from the official publisher) with a
  clean compose file. Don't reuse the old writable layer.
- Restore app data only from a backup taken before the earliest plausible compromise, or rebuild the
  configuration by hand; check restored data for attacker-added users, scripts, and integrations.
- For ntfy and Gotify, rotate every token and password (all clients and publishers need the new ones),
  revoke tokens nobody recognizes, and set ntfy's `auth-default-access` to `deny-all` before reopening.
- **Rotate every secret the app held:** create new keys at each integrated service and revoke the old
  ones; new admin and user passwords for the app; new session or signing secrets where the app has them;
  new notification credentials and webhook URLs.
- If the project is abandoned or the vulnerability that let the attacker in has no fix, don't redeploy
  it; replace it or retire it.
- Before reopening access: authentication enabled (or an auth proxy with MFA in front), no direct-port
  bypass, no Docker socket or the minimum socket-proxy permissions, read-only keys, not reachable from
  the internet without the auth layer.

## Quick checklist tailored for a self-hosted app

Start with the core quick checklist, plus:

- [ ] Remove the public route or port forward to the app; stop (don't remove) its container.
- [ ] Copy container logs, proxy logs, and the app's data volume off the host.
- [ ] List every service whose key the app held, and check those services for misuse.
- [ ] If the app had the Docker socket or privileged access, treat the whole host as compromised.
- [ ] Redeploy from a clean, current image only after rotating every key the app held.
