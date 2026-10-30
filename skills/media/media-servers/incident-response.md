# Media Servers and Transcoding: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only media-server-specific steps.

A compromised media server can run code as its service user, read and often write the library and any
shares mounted into it, and hold tokens for the owner's account and for other apps. Known campaigns
against media servers installed credential-stealing plugins (Emby, 2023) and crypto miners and proxy
software (Plex, 2026). A compromised Tdarr server can run commands on every node and rewrite the library.

## Triage and containment

- **Indicators:** unknown admin users or API keys; unknown plugins, plugin repositories, or DLL/.so files
  in plugin or codec folders; transcoder or advanced preferences nobody set; unknown devices or sessions
  on the owner account or the server; high CPU or GPU with nothing playing; unknown processes in the server
  container or under the server's user; outbound connections to unfamiliar hosts; unexpected Tdarr flows,
  plugins, or nodes; media files changed or deleted in bulk; and a vendor advisory saying exposed servers
  on the installed version should be treated as possibly compromised.
- **Contain at the edge first:** turn off Plex Remote Access and remove the router forward or UPnP
  mapping, or remove the proxy route or forward for Jellyfin/Emby/Tdarr. This is reversible and preserves
  evidence. Plex's 2026 advisory also recommends this step.
- **Stop, don't destroy:** if an unknown process or plugin is running, stop the container or service.
  Don't delete the container, its data folder, or its image yet.
- **Pause Tdarr nodes** and stop queues if Tdarr is involved, so no more files are rewritten.
- **Account containment (Plex):** the owner should sign out all devices and change the plex.tv password
  from a clean device, and confirm 2FA. Do this after capturing the device list.
- **If the host may be compromised** (unknown processes outside the server, changed system files), isolate
  the host and assess it with the operating-system skill. Treat any share the server could write as
  possibly altered.

## Evidence to preserve (media-server-specific)

Collect before changing anything, and store copies off the host as secret material:

- A copy of the server data folder (Plex data directory including `Preferences.xml`, Codecs, Plug-ins, and
  logs; Jellyfin/Emby config, plugins, and logs; Tdarr server and node configs and database), taken with
  the server stopped where possible. On Windows Plex, also export the server's registry preferences.
- File listings with timestamps, owners, and hashes for plugin and codec folders; copies of unknown files.
- Server logs and log archives, covering the suspected period (Plex Media Server logs, Jellyfin/Emby
  server and activity logs, Tdarr server and node logs).
- Users, admin flags, API keys (names and dates only), devices, active sessions, and sharing lists
  (screenshots), plus the plex.tv authorized devices list before signing anything out.
- Container metadata: image and digest, creation time, mounts, devices, network mode, environment variable
  names.
- Reverse-proxy, router, and firewall logs for the exposed port; a list of established outbound
  connections from the host (process and destination) while the server is still running, if safe.
- For Tdarr: the flows and plugins list, job history, and node list.

## Scope checks specific to media servers

- Every share and folder mounted into the server or Tdarr nodes, read-write ones first: replaced or
  planted files, ransomware, or bulk deletions.
- The owner account: Plex account sign-ins and devices; reused passwords on other services (the 2022 and
  2025 Plex incidents showed account data can leak independently of the server).
- Integrations that held the server's token or API key (request apps, Tautulli, dashboards): use the
  `media-automation` skill; and the reverse direction, since tokens for those apps may be in the server's
  plugin configs.
- Users who logged in during the compromise: a credential-stealing plugin captures every password typed;
  those users must change their media-server password and any place they reused it.
- Tdarr node hosts and anything they mount; GPU hosts shared with other workloads.
- Other containers and the container host, especially if the server ran with host networking,
  `--privileged`, or the Docker socket.

## Eradication and recovery

- Rebuild from a fresh vendor image or installer on the fixed version. Plex's 2026 guidance for a
  compromised or uncertain server is a clean installation rather than reusing the old Plex data directory;
  apply the same principle to Jellyfin, Emby, and Tdarr when integrity is in doubt.
- If you restore library metadata or settings, restore only from a backup taken **before** the earliest
  plausible compromise, without plugin, codec, or script folders; reinstall plugins from the official
  source after review.
- **Rotate:** the owner account password (sign out all devices), every server user's password if a
  credential stealer is possible, all Jellyfin/Emby/Tdarr API keys and node keys, tokens held by
  integrations, and any credentials stored in plugin configurations or reachable from the server's user.
- Re-check media integrity on writable shares, and restore damaged media from independent copies.
- Before re-enabling remote access: fixed version confirmed, admin separated from daily accounts, 2FA on
  the owner account, no unneeded plugins or repositories, read-only media mounts where possible, no
  privileged container, and logs retained.

## Quick checklist tailored for media servers

Start with the core quick checklist, plus:

- [ ] Turn off remote access and remove forwards or proxy routes; pause Tdarr nodes.
- [ ] Copy the data folder, plugin and codec folders, and logs off the host before changing anything.
- [ ] Capture users, API keys, devices, sessions, and sharing lists; then sign out all devices on the
      owner account and change its password.
- [ ] Check writable shares for changed or deleted media.
- [ ] Rebuild from a clean install on the fixed version and rotate every token and key.
