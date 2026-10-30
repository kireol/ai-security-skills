---
name: media-automation
description: >-
  Security assessment, hardening, remediation, and incident response for media-automation stacks: the
  Servarr apps (Sonarr, Radarr, Lidarr, Readarr-style apps, Prowlarr), Bazarr, request apps (Overseerr,
  Jellyseerr, Seerr), Tautulli, usenet downloaders (SABnzbd, NZBGet), torrent clients (qBittorrent,
  Transmission), and helpers such as FlareSolverr. Use when auditing an "*arr" stack, reviewing its
  authentication, API keys, reverse-proxy or tunnel exposure, download-client web UIs, VPN binding, shared
  media/config folder permissions, updates, or backups, or when one of these apps may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Sonarr v4/v5, Radarr, Lidarr, Prowlarr, Bazarr, Seerr and its predecessors, Tautulli, SABnzbd, NZBGet, qBittorrent, Transmission 4.x, FlareSolverr (verify each installed version; settings move between releases)"
  audience: "home, homelab"
  finding_prefix: "ARR"
  modes: "discover, recommend, remediate, respond"
---

# Media Automation (*arr Stack and Downloaders) Security

Act as a careful, evidence-driven homelab security engineer. A media-automation stack is a set of small web
apps that hold each other's API keys, indexer and usenet credentials, and write access to the media and
download folders, and several of them run commands on the host. One weak app is a path into all of them
and often into the host. Identify, explain, prioritize, remediate (only when authorized), and verify
weaknesses in the apps, how they are exposed, how they trust each other, and the folders they share.

This skill is about security. It does not give advice on the legality of any content or on avoiding
copyright enforcement, and it treats VPN binding only as a question of which network path traffic uses.

## How to use this skill

This skill holds only media-automation-specific guidance. It builds on the shared core, which always
applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Media-automation-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and advisories are in [references.md](references.md). Media servers (Plex, Jellyfin, Emby)
and transcoders (Tdarr) are covered by the `media-servers` skill; assess them together when they share
folders or tokens.

## Media-automation-specific principles

- **Admin access to any of these apps is close to code execution on the host.** Servarr apps can run a
  custom script on events (Settings → Connect), torrent clients can run an external program when a
  download finishes, and SABnzbd and NZBGet run post-processing scripts. Combined with the ability to put
  files into a folder the app can read, an attacker with the web UI or API key can usually run commands as
  the app's user. Classify and prioritize accordingly.
- **An API key is an admin password.** A Servarr API key has the same power as the admin login: it can
  read every stored credential the API returns, change download clients and indexers, and add connections.
  Keys are stored in plain text in each app's `config.xml` (Servarr) or settings file, in other apps that
  call them (Prowlarr, Bazarr, the request app, dashboards), in container environment variables, and in
  backups. Never print, paste, or upload a key or a whole configuration file.
- **Trust is transitive.** Prowlarr holds every indexer credential and pushes them to the Servarr apps; the
  request app holds Servarr and media-server tokens; Bazarr and Tautulli hold Servarr keys or the media
  server owner's token. Compromise of the most-exposed app usually means compromise of everything it holds
  keys for. Map the key graph before judging any single app.
- **"Local address" exemptions depend on how the app sees the client's address.** Servarr apps offer
  Authentication Required → *Disabled for Local Addresses*, qBittorrent can bypass login for localhost and
  for whitelisted subnets, SABnzbd treats private ranges as local, and NZBGet's `AuthorizedIP` grants full
  access without a password. Behind a reverse proxy, a tunnel, or a container bridge, every request can
  appear to come from a local address. Sonarr's own advisory (GHSA-h5qx-5hjf-7c9r) is an example: a spoofed
  `X-Forwarded-For` header let callers skip authentication when local exemptions were on.
- **These apps have had a steady stream of serious advisories.** In 2026 alone, several of them published
  authentication-bypass, path-traversal, or remote-code-execution advisories on GitHub. Don't treat an app's
  login page as the only barrier: keep them off the internet, current, and isolated. Check each app's
  advisories live (references.md); never rely on a remembered list.
- **Folders are part of the security boundary.** If the configuration folder sits on a share that other
  users or devices can write, anyone who can write it can change the app's authentication, API key, or
  scripts. The Servarr wiki also warns against keeping the SQLite databases on network shares, because of
  locking and corruption.
- **Some apps are no longer maintained.** Readarr was retired and its repository archived in June 2025, and
  the Overseerr repository is archived (Seerr provides a migration path for Overseerr and Jellyseerr users).
  Unmaintained apps get no security fixes: apply the core end-of-life rule.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Containers on one host** (Docker/Podman, Compose) | Images from the projects or a community image publisher; bind-mounted config and media folders; `PUID`/`PGID`/`UMASK` variables. | Updates are image pulls, not in-app updates. Check published ports, bind addresses, environment variables (secrets often live there), and who can reach the Docker socket. Container user IDs decide folder access. |
| **VPN sidecar or VPN-namespace containers** | The torrent client (and sometimes others) shares the network namespace of a VPN container; its web UI port is published on the VPN container. | The VPN container's firewall is the kill switch. Check that traffic stops when the tunnel drops, that the web UI is reachable only from the LAN side, and that any provider-forwarded port reaches only the peer port. |
| **Native install** (Windows service, Linux package, macOS app) | Services or launch agents; app data folder in the user profile or `/var/lib`. | The in-app updater runs as the app's user and needs write access to its own program files, so that user can modify the app. On Windows the Servarr apps update automatically. |
| **NAS app or package** | Installed from the NAS vendor's app catalog or a community catalog. | Package maintainers may lag upstream security fixes. NAS share permissions and the NAS's own remote access matter (use the NAS skill). |
| **Seedbox or remote VPS** | Apps run on a rented host; the user reaches them over the internet. | Every web UI is internet-facing unless fronted by a VPN or an authenticating proxy. The provider has root on the host. |
| **Published through a reverse proxy or tunnel** | Hostnames such as `sonarr.example.com`; a tunnel agent; a URL base set in the app. | Real client addresses depend on proxy headers and Trusted Networks / known-proxy settings. Local-address exemptions become dangerous. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Vendor-default web UI ports (all HTTP unless TLS was configured): Sonarr 8989, Radarr 7878, Lidarr 8686,
  Readarr 8787, Prowlarr 9696, Bazarr 6767, Overseerr/Jellyseerr/Seerr 5055, Tautulli 8181, NZBGet 6789
  (TLS 6791 when enabled), Transmission RPC and web UI 9091, FlareSolverr API 8191. qBittorrent's web UI
  and SABnzbd both default to 8080, so they collide; containers often remap one of them.
- Page titles and login pages carry the product name (Sonarr, Radarr, Prowlarr, qBittorrent, SABnzbd,
  NZBGet, Transmission Web, Tautulli, Overseerr/Jellyseerr/Seerr). A Servarr login page is the same
  design across Sonarr, Radarr, Lidarr, Readarr, and Prowlarr. Servarr apps also send their API with a
  `/api/v1` or `/api/v3` path.
- Transmission's RPC answers unauthenticated requests on `/transmission/rpc` with an HTTP 409 and a session
  ID header, or a 401/403 when authentication or its address whitelist rejects the caller.
- FlareSolverr answers its API port with a short JSON status message and no login.
- Torrent clients listen on a peer port too (Transmission 51413 by default; qBittorrent picks a port at
  install). A peer port on a host that is not the VPN endpoint is worth noting.
- These apps don't announce themselves with mDNS or SSDP by default. Container hosts usually show many of
  these ports at once; virtual MAC address vendors (container bridges, hypervisors) are common.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer the web UIs (System → Status, Settings pages with "Show Advanced" on), user-run checks, and
read-only API calls the user authorizes. For containers, these are *candidate* read-only commands, **not
yet verified** on every engine and version. Check each exists first.

```sh
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}'      # running containers, images, published ports
docker inspect --format '{{json .HostConfig.PortBindings}}' <container>   # bind address per published port
docker inspect --format '{{json .Mounts}}' <container>       # config, media, and download mounts (rw/ro)
docker inspect --format '{{.HostConfig.NetworkMode}}' <container>   # shares a VPN container's namespace?
docker exec <container> id                                    # user and groups the app runs as
ls -ld <config-dir> <media-root> <downloads-dir>               # owner, group, mode (names only, no contents)
stat -c '%A %U:%G %n' <config-dir>/config.xml                  # who can write the Servarr config file
ss -tlnp                                                       # listening sockets on a native install
```

- `docker inspect` without a `--format` filter prints every environment variable, which often includes API
  keys and passwords. Filter it, or redact before showing output.
- Read single settings from `config.xml` (for example the authentication method and requirement, bind
  address, URL base, branch) with a targeted query, and never the `ApiKey` element. The Servarr apps redact
  API keys in their own logs; keep it that way in your notes.
- Servarr read-only API calls (for example the system status endpoint) need the API key. If the user runs
  them, they should send the key in the `X-Api-Key` header, not in the URL, so it doesn't land in proxy
  logs and shell history.

**Never** do any of these in Discover:

- Print, copy, or upload an API key, `config.xml`, `settings.json`, `qBittorrent.conf`, `sabnzbd.ini`,
  `nzbget.conf`, a backup archive, or `docker inspect` output with environment variables, whole.
- Trigger searches, RSS syncs, grabs, imports, renames, or downloads; test indexers or download clients
  (tests contact third parties with stored credentials); approve or create requests.
- Delete, move, or rename media, downloads, torrents, history, or backups; remove torrents "with data".
- Test default or guessed credentials against any login page or API, or run exploit code to "confirm" an
  advisory.
- Toggle authentication or bypass settings to see what happens.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, versions, and lifecycle

- Every app in the stack, its version, update branch (Servarr: Settings → General → Updates, advanced
  "Branch"), install type, and image source and tag (a pinned old tag never updates).
- Compare against each project's releases and GitHub security advisories (references.md). Note apps with
  open advisories that apply to the installed version.
- Unmaintained apps: Readarr (archived June 2025), Overseerr (archived), forks with no recent releases,
  third-party metadata servers wired into a retired app. These are end-of-life findings.
- Unused apps still running (an old Jackett next to Prowlarr, a second downloader nobody uses).

#### B. Authentication on each app

- **Servarr apps** (Settings → General → Security): Authentication method (Forms is the login page; Basic
  is a browser pop-up; in Sonarr v5 Basic is treated as Forms and OpenID Connect is available; External
  hands authentication entirely to a reverse proxy and can only be set in `config.xml` or an environment
  variable). Authentication Required: *Enabled* is recommended; *Disabled for Local Addresses* needs a
  correct Trusted Networks list and Allowed Hosts. Since Sonarr v4, authentication is mandatory and
  `None` is no longer selectable; an old `config.xml` may still contain it. Verify the exact options on
  each app and version.
- **External** authentication: confirm the app is reachable *only* through the authenticating proxy (bind
  address, published ports, container networks). Otherwise it has no login at all.
- **Trusted Networks / Allowed Hosts:** only the proxy's own address, not a whole LAN or container subnet.
  The hidden "trust CGNAT addresses" option treats the CGNAT range (used by some mesh VPNs) as local;
  note it if set.
- **Prowlarr, Bazarr, Tautulli, request apps:** a login is enabled, the admin account is named and has a
  strong password, and Tautulli's guest access is off or limited.
- **qBittorrent** (Tools → Options → Web UI): a password was set (since 4.6.1 there is no default
  password; a temporary one is printed to the console until you set one), and the "bypass authentication
  for clients on localhost" and "bypass authentication for clients in whitelisted IP subnets" options.
  Behind a proxy on the same host, the localhost bypass means no authentication for everyone.
- **Transmission** (`settings.json`): `rpc-authentication-required` (default false), `rpc-whitelist-enabled`
  and `rpc-whitelist` (default localhost only), and `rpc-host-whitelist-enabled` (DNS-rebinding guard,
  default on). A whitelist of `*.*.*.*` or a disabled whitelist with no password is an open client.
- **SABnzbd** (Config → General): username and password set; External internet access level (from no
  access through "Full Web interface - Only external access requires login"); which networks count as
  local (`local_ranges`); whether "local" in this deployment includes a proxy or tunnel.
- **NZBGet** (Settings → Security): `ControlUsername`/`ControlPassword` changed from the shipped default
  (ask the user; never try logging in), `AuthorizedIP` empty or minimal (the sample config warns not to use
  it behind another web server), and the restricted and add-only users used by other apps instead of the
  control user.
- Whether any app is reached through a dashboard or "homepage" app that embeds its API key and is itself
  unauthenticated.

#### C. API keys and the trust graph

- Draw the graph: which app holds which other app's API key, which apps hold download-client credentials,
  which hold the media server's token (request app, Tautulli, Bazarr). Record names only, never values.
- Key age and reuse: keys never rotated since install, the same key copied into many tools, keys in
  scripts, cron jobs, or chat history.
- Where keys live outside the app: Compose files and `.env` files (in a git repository?), container
  environment variables (for example the Servarr `__AUTH__APIKEY` style variables), dashboards, browser
  bookmarks with `apikey=` in the URL, reverse-proxy access logs.
- NZBGet: other apps use the restricted or add-only user, not the control user. SABnzbd: apps that only
  submit jobs use the NZB key rather than the full API key.
- Request app: which users can request, auto-approve, or administer; whether sign-in is tied to the media
  server's accounts and which of those accounts exist (friends of friends?). Seerr has published
  advisories on unauthenticated registration and on other users' notification credentials leaking; check
  the installed version against them.

#### D. Network exposure and remote access

- Every published port and its bind address. Containers publishing `8989:8989` listen on all host
  addresses; `127.0.0.1:` or a LAN-only address limits that. Servarr Bind Address (`*` means all).
- Internet exposure: router port forwards, UPnP mappings, reverse-proxy routes, tunnels (Cloudflare-style,
  mesh VPN "funnel" features), and the seedbox case. Test from outside only with explicit authorization.
- Which apps are meant for outside users (usually only the request app) and which are admin tools that
  should never be internet-facing (Servarr apps, Prowlarr, downloaders, Bazarr, Tautulli, FlareSolverr).
- For anything published: TLS at the proxy, an authentication layer in front (SSO/forward-auth or VPN),
  the app's own login still enabled where possible, URL base and Trusted Networks set, and the proxy not
  logging full URLs with API keys.
- **FlareSolverr-type helpers:** no authentication by design and the project says not to expose it to the
  internet; it launches a browser for any URL it is given (a server-side request tool). Reachable only by
  Prowlarr, ideally on a private container network with no published port.
- Internal reachability: can IoT or guest segments reach these UIs? Can the apps reach admin interfaces
  they don't need (an SSRF in any of them becomes a LAN scanner)?
- Certificate validation for outbound connections: Servarr Certificate Validation (*Enabled* recommended;
  *Disabled* trusts any certificate), NZBGet `CertCheck` (the sample config ships with it off), SABnzbd
  and qBittorrent versions (qBittorrent before 5.0.1 ignored TLS errors in its download manager).

#### E. Download clients, VPN binding, and kill switch

- Web UI exposure and authentication (domain B). Torrent client web UIs should never be on the internet or
  on the VPN's public side.
- **External program / script hooks:** qBittorrent "run external program" on add or finish, Transmission
  `script-torrent-done-*`, SABnzbd scripts folder and category scripts, NZBGet extension scripts and
  `ShellOverride`, Servarr Connect → Custom Script. List every configured hook and who can write the
  script files. Unknown hooks are a P0 indicator.
- **VPN binding** for torrent clients that must use a VPN: qBittorrent's advanced network interface and
  optional bind-address settings (verify names on the installed version), Transmission `bind-address-ipv4`
  and `bind-address-ipv6`, or a VPN-namespace container. Check IPv6 separately: binding only IPv4 can leave
  IPv6 peers on the normal connection.
- **Kill switch:** what happens when the tunnel drops (client stops, or traffic falls back to the normal
  route)? For VPN containers, a firewall that blocks non-tunnel traffic; for native installs, interface
  binding plus a firewall rule. Ask the user to test with the client paused; don't start downloads to test.
- Provider port forwarding: the forwarded port maps only to the peer port, never the web UI; the web UI
  inside a VPN namespace listens only where the LAN can reach it.
- DNS: whether the client's lookups go through the tunnel or the normal resolver.
- Peer-protocol settings that widen exposure: UPnP/NAT-PMP in the client (opens router ports), and
  encryption preferences.

#### F. Indexer, usenet, and third-party credentials

- Prowlarr holds indexer accounts, API keys, and cookies (and FlareSolverr/proxy settings); Servarr apps
  may hold their own indexers; SABnzbd and NZBGet hold usenet provider logins; Bazarr holds subtitle
  provider logins; list apps (Trakt-style) hold OAuth tokens; notification connections hold webhook URLs
  and bot tokens. Record which exist, not their values.
- Reused passwords: indexer and usenet accounts with the same password as the user's email or other
  services.
- Usenet server connections use TLS (the usenet provider's TLS port) with certificate checking on.
- Indexer and tracker accounts are third-party accounts: if they leak, the user's accounts there can be
  abused or banned. Note this for scoping.

#### G. File permissions and shared folders

- Config folders: owned by the app's user, not world-writable, not on a share that other people or
  devices can write. Writable `config.xml` means anyone can switch authentication to External, change the
  API key, or point scripts elsewhere.
- Media and download folders: the apps need write; other users and devices usually need read only.
  World-writable (`777`) folders and `UMASK` 000 let anything on the share replace media or plant files
  that a script hook later runs.
- NFS exports and SMB shares that hold config or media: which hosts and users can mount them, read-write
  or read-only, root squash on NFS, guest access on SMB. A whole-LAN read-write export of the config
  folder is a finding.
- One shared user ID for every container (common with `PUID`/`PGID`): a compromise of one app can write
  every other app's config. Note it; separate IDs and a shared media group are the stronger pattern.
- SQLite databases on network shares (Servarr warns against it): reliability, plus corruption that looks
  like tampering.
- Script folders: writable only by an administrator, not by the app user or the download folder.

#### H. Updates and supply chain

- Update mechanism per app: Servarr Built-in, Script, or Docker (in containers, pull a new image); Windows
  installs update themselves; the branch (stable vs. develop/nightly).
- Container image sources: the project's own image or a well-known publisher, not a random account; pinned
  to a stable tag or digest with a process to update it.
- Automatic image updaters: they usually need the Docker socket, which is root-equivalent on the host.
  Check how that updater is exposed and authenticated.
- Third-party add-ons: custom indexer definitions, Bazarr providers, community scripts and extensions,
  browser extensions that hold API keys.

#### I. Backups and data protection

- Servarr built-in backups (Settings → General → Backups / System → Backup): folder, interval (default 7
  days), retention (default 28 days). In containers the default folder is inside the config volume, so
  backups die with it.
- Backups contain `config.xml` (API key) and the database (indexer and download-client credentials): they
  are secrets. Check where they are copied and who can read them.
- Other apps: Prowlarr and Bazarr backups, Tautulli database, request-app database, download-client
  settings, Compose files.
- Restore tested at least once; backups kept off the host.

#### J. Logging and monitoring

- Log level (Trace and Debug can include more detail, so don't leave them on), log retention, and whether
  logs or support bundles have been posted publicly with keys or hostnames.
- Reverse-proxy and tunnel access logs: failed logins, requests with `apikey=` in the URL, requests to API
  paths from unexpected addresses.
- Health and notification channels: alerts for failed updates, new download clients, or authentication
  changes, if available.
- Servarr System → Events and History: unexpected grabs, imports, or setting changes.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Everything in the stack is wired together, so list what depends on a setting before changing it:

- **API key consumers:** rotating one app's key breaks every app, dashboard, script, and mobile app that
  uses it until each is updated.
- **Download-client credentials and categories:** Servarr apps and Prowlarr test and use these; a password
  change without updating them stops imports.
- **Reverse-proxy routes, URL base, and tunnels:** mobile apps, the request app, and outside users rely on
  them.
- **The VPN path:** changing binding or the VPN container's network can stop the client or, worse, let it
  fall back to the normal route.
- **Container user IDs and folder permissions:** tightening them can stop imports, hardlinks, or the media
  server's access to new files.
- **Request-app users:** family and friends who sign in with media-server accounts.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Admin app reachable from the internet | Remove the port forward or public route; reach admin UIs over a VPN. Publish only the request app, behind TLS and an authentication layer. | Remote management needs a working VPN first; mobile apps that used the public URL must change. |
| Servarr "Disabled for Local Addresses" behind a proxy | Set Authentication Required to *Enabled*, or keep the exemption only with Trusted Networks limited to the proxy's address and a current version. | Users log in on the LAN too; integrations use API keys and aren't affected. |
| External authentication with a direct path to the app | Remove direct ports so the app is reachable only through the authenticating proxy, or switch to Forms. | Local access without the proxy stops. |
| Download client without a password or with broad bypass | Set a strong password; limit bypass to the specific address of the app that needs it, or remove it. | Servarr download-client settings need the new credentials. |
| Open Transmission RPC | Enable authentication and restrict `rpc-whitelist` to the needed addresses. | Edit with the daemon stopped (or reload as documented), or changes are reverted. |
| NZBGet default control credentials or broad `AuthorizedIP` | Change the control credentials, empty `AuthorizedIP`, give other apps the restricted or add-only user. | Apps using the control user need new credentials. |
| Old, shared, or leaked API keys | Rotate keys app by app and update every consumer. Move keys out of URLs and git-tracked files. | Brief breakage of each integration until updated. |
| FlareSolverr reachable from the LAN or internet | Put it on a private container network with Prowlarr only; no published port. | None for Prowlarr if the network is shared. |
| Unknown script or external-program hooks | Treat as an incident first (Respond). Otherwise remove unused hooks and make script folders admin-writable only. | Post-processing that relied on them stops. |
| Torrent client not bound to the VPN, no kill switch | Use a VPN-namespace container with a firewall kill switch, or bind the client to the VPN interface and add a firewall rule; cover IPv6. | Client stops whenever the VPN is down. |
| World-writable config or media folders, whole-LAN NFS/SMB write | Restrict config folders to the app user; make media read-only for everyone except the apps that write it; restrict exports to specific hosts. | Some devices lose write access; check hardlinks and imports still work. |
| One user ID for every container | Separate user IDs per app with a shared media group. | Permission rework across folders; plan carefully. |
| Certificate validation disabled | Enable it (Servarr, NZBGet `CertCheck`, usenet TLS). | Connections to servers with bad certificates fail and must be fixed properly. |
| Unmaintained app (Readarr, Overseerr) | Migrate to a maintained successor or remove; isolate until then. | Feature loss or migration effort. |
| Backups inside the config volume, unencrypted | Copy backups off the host, encrypted, with restricted access. | Needs a destination; it holds every key. |
| Outdated app or image | Update to the current stable release; check open advisories first. | Brief restart; read release notes for breaking changes (v4 → v5 style upgrades). |

Changing ports or hiding the login page is supplementary only. Never recommend it as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet-exposed admin apps, open download
clients, applicable advisories) → high-priority hardening (authentication, keys, VPN binding, folder
permissions) → routine maintenance → optional defense in depth. Then ask for approval (core: modes and
authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Media-automation specifics:

- **Before any change:** take each affected app's built-in backup (or copy its config folder with the app
  stopped) and store it off the host, treated as a secret. Record the current settings you will change.
- **Use the app's UI or documented API.** Edit `config.xml`, `settings.json`, or `qBittorrent.conf` by hand
  only for documented recovery cases (for example a forgotten Servarr password), with the app stopped, and
  keep a copy of the original. Transmission and qBittorrent overwrite their settings files on exit.
- **Authentication changes are C2:** keep a session open, test login in a second browser, and know the
  documented recovery path before you start. For Servarr, the recovery is editing `config.xml` with the
  app stopped; confirm the user has file access to do that.
- **Rotating an API key:** list every consumer first (domain C), rotate, then update consumers one by one
  and confirm each reconnects (Servarr System → Status and the download-client and app connection pages
  show errors). Don't run tests that trigger searches.
- **VPN binding and kill switch:** apply with the torrent client paused; confirm the client has no route
  when the tunnel is down before resuming anything.
- **Folder permissions:** change one folder at a time; check imports, hardlinks, and the media server's
  access after each. Never run a recursive permission or ownership change on a media root without
  approval for that exact command and path.
- **Updates:** for containers, pull and recreate one app at a time; for major versions (for example Sonarr
  v4 to v5), read the release notes and take a backup first.
- **Exposure changes:** remove a public route only after the replacement path (VPN, authenticated proxy) is
  tested.

After each change, follow the core "after a change" steps: re-read the setting, confirm the login or
exemption behaves as intended, confirm dependent apps reconnect, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Bulk deletion or moving of media, downloads, history, or backups, or removing torrents with their data.
- Recursive `chmod`/`chown` across media or config roots without approval for the exact path.
- Testing logins with default or guessed credentials, or running exploit code against any app.
- Disabling authentication, adding a broad bypass subnet, or switching to External authentication as a
  troubleshooting step.
- Triggering searches, grabs, or indexer tests to "verify" a fix.
- Restoring an app database or config from a backup of unknown age during an incident.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the
media-automation-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### ARR-001: Torrent client web UI open to the LAN and the internet with authentication bypassed

**Confidence:** Confirmed
**Priority:** P1. Anyone on the internet can control the torrent client, including its "run external
program" hook, which runs commands as the client's user on the host.
**State:** Open
**Component:** qBittorrent web UI (container), behind a reverse proxy on the same host
**Evidence:** Observed 2026-02-03: the web UI option "bypass authentication for clients in whitelisted IP
subnets" is on, with the container bridge subnet listed. The reverse proxy publishes the UI at
`torrent.example.com` and connects from that subnet, so every proxied request is exempt. With approval,
an external check from `198.51.100.23` opened the UI without a login. The "run external program on
torrent finished" setting is empty. The client is in a VPN-namespace container, but the UI port is
published on all host addresses (`docker inspect` port bindings show `0.0.0.0`).
**Expected secure state:** a password-protected web UI reachable only from the LAN or a VPN; bypass limited
to the single address of the Servarr app that needs it, or off (qBittorrent web UI options; project
guidance not to expose download clients).
**Exposure and prerequisites:** anyone who can reach `torrent.example.com`; no credentials needed.
**Dependencies / blast radius:** Sonarr and Radarr use the client through the container network with stored
credentials; the user checks the client from a phone through the public hostname.
**Recommended remediation:** remove the public proxy route, set a strong web UI password, turn off the
subnet bypass (or limit it to `192.0.2.10`, the Servarr container's address), publish the UI on the LAN
address only, and use the VPN to check it remotely. Then check the client's history and settings for
signs of misuse (Respond triage), because it was open.
**Operation class:** C2 (removes the user's remote path and changes authentication).
**Approval required:** Yes.
**Verification:** external check no longer reaches the UI; LAN access asks for a login; Sonarr and Radarr
show the download client as healthy; port bindings show the LAN address only.
**Rollback:** restore the previous web UI settings from the saved copy (not recommended; restrict the
bypass instead).

---

## Version history

- **1.0** (2026-10-30): Initial version.
