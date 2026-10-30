---
name: frigate-nvr
description: >-
  Security assessment, hardening, remediation, and incident response for Frigate NVR (Docker, Home
  Assistant app/add-on, and other installs), with notes that carry over to other NVR software. Use when
  auditing a Frigate server, reviewing its authenticated and unauthenticated ports, users and roles, TLS,
  go2rtc restream and WebRTC exposure, camera and MQTT credentials, generative AI integrations, recordings
  retention and storage, or remote access, or when a Frigate server or its recordings may have been
  compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Frigate 0.14 and later (built-in authentication); written against the 0.18 series (verify the live version; settings and API behavior change between releases)"
  audience: "home, homelab, work"
  finding_prefix: "NVR"
  modes: "discover, recommend, remediate, respond"
---

# Frigate NVR Security

Act as a careful, evidence-driven security engineer for a video surveillance server. An NVR concentrates
the most sensitive data in a home or small office (live and recorded video of people, often with audio),
holds the credentials of every camera it reads, and usually sits on two networks at once: the camera
network and the network its users browse from. Identify, explain, prioritize, remediate (only when
authorized), and verify weaknesses in Frigate itself, in how it is published, and in the data it keeps.

## How to use this skill

This skill holds only Frigate-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Frigate-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md). The cameras themselves are covered by the
[ip-cameras](../ip-cameras/SKILL.md) skill; assess them together.

**Other NVR software** (for example Blue Iris, Synology Surveillance Station, or a camera vendor's own NVR
appliance) has the same risk areas: an admin web UI and API, stored camera credentials, restream and
mobile-app ports, cloud relay features, recordings storage, and remote access. Use the domains below as a
checklist for them, but verify every product-specific fact against that product's own documentation;
nothing Frigate-specific here carries over automatically.

## Frigate-specific principles

- **Port 5000 has no authentication.** Frigate's documentation describes port 8971 as the authenticated
  UI and API (the one reverse proxies should use) and port 5000 as an internal, unauthenticated UI and API
  whose access "should be limited". Requests on 5000 are treated as admin. Anyone who can reach port 5000
  can view every camera, change the configuration, and manage users. Treat any reachability of port 5000
  beyond the host, the Home Assistant instance that needs it, or a trusted proxy as a high-priority
  finding.
- **Admin access is close to host access.** Frigate's own release notes for the 0.16 to 0.18 series list
  several fixed advisories in which an authenticated admin (and in some cases a viewer) could run code as
  root inside the container, for example through go2rtc stream sources. Treat Frigate admin rights, and
  anything that grants them (port 5000, a proxy's auth secret, the JWT secret), as equivalent to control
  of the container, and of the host if the container is privileged.
- **The viewer role is a convenience, not a strong boundary.** Several fixed advisories were
  viewer-to-admin or cross-camera authorization bypasses. Keep Frigate current, and don't give viewer
  accounts to people you wouldn't trust with more.
- **The configuration file is a secret.** `config.yml` usually holds camera usernames and passwords inside
  RTSP URLs, MQTT credentials, generative AI API keys, and the Frigate+ key. Never print, paste, or upload
  it whole. Read only what you need and redact it. Logs and the configuration editor in the UI expose the
  same data.
- **The first admin password is printed in the logs.** On first start (and after a password reset)
  Frigate generates an admin password and writes it to the log. Container logs may be shipped to a log
  server or kept by the container runtime; check who can read them, and never print them unfiltered.
- **go2rtc is a second server inside Frigate.** It serves an RTSP restream (8554, unauthenticated by
  default), WebRTC (8555 TCP and UDP), and its own API and web UI (1984). The go2rtc project warns that its
  three ports are reachable from the local network by default, that anyone there can watch the cameras
  without authorization, and that API access leads to full access to the server.
- **Camera recordings are evidence and personal data at the same time.** Deleting them destroys evidence;
  copying them spreads sensitive data. Both need the user's explicit decision.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Docker / Docker Compose** (the documented install) | A `frigate` container from the project's image; a compose file with `/config` and `/media/frigate` mounts and published ports. | Published ports in the compose file decide exposure. Check for `privileged: true` (the example uses it, noting it "may not be necessary for all setups"), device passthrough, `apparmor=unconfined`, host networking, and whether the Docker socket is mounted. Anyone in the host's `docker` group effectively has root. |
| **Home Assistant app (add-on)** | Installed from the Home Assistant app store; variants Frigate, Frigate (Full Access), Frigate Beta, Frigate Beta (Full Access). Config at `/addon_configs/<app-directory>/config.yml`. | The UI is normally opened through Home Assistant ("Open Web UI"). Host port mappings are set on the app's Configuration/Network tab; check whether 5000, 8554, 8555, or 8971 are mapped to the host. The Full Access variants allow turning off Home Assistant's protection mode, which gives the container broad host access. Home Assistant admins can change the app and read its config. |
| **Frigate in an LXC container or VM** (for example on a hypervisor) | Docker inside an LXC or VM. | The vendor says LXC is not officially supported, and common workarounds (privileged LXC, world-readable device files) weaken host isolation. The hypervisor is part of the trust boundary. |
| **NAS or appliance app catalogs** (community-packaged) | Installed from a NAS or home-server app store. | Packaging, default port mappings, and update timing depend on the packager, not the Frigate project. Check which image and version are actually running. |
| **Docker on macOS or Windows** | Docker Desktop. | Windows is not officially supported. On macOS, port 5000 conflicts with the AirPlay receiver and is often remapped to another host port; find the real mapping before checking exposure. |
| **Paired with the Home Assistant integration** | A Frigate integration in Home Assistant pointing at a Frigate URL. | The integration may point at 5000 (no auth) or 8971 (auth). It can also publish notification media through Home Assistant's own URL, so Home Assistant's exposure becomes part of Frigate's. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- TCP 8971: HTTPS by default with a self-signed certificate generated by Frigate; the web UI is titled
  Frigate and shows a login page.
- TCP 5000: plain HTTP Frigate UI with no login page (the unauthenticated internal port). Seeing the
  camera grid without logging in is itself a finding.
- TCP 8554: RTSP (the go2rtc restream). TCP and UDP 8555: WebRTC. TCP 1984: the go2rtc web UI and API, if
  published.
- Often found next to an MQTT broker (TCP 1883, or 8883 with TLS) and Home Assistant (TCP 8123).
- The host is usually a Linux server, NAS, or mini PC running Docker, or a Home Assistant host; there is
  no Frigate-specific MAC vendor. A Coral, Hailo, or GPU accelerator in the inventory is a hint.
- The host makes many long-lived RTSP connections to cameras on the camera network.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer the Frigate UI as an admin user, the user running checks themselves, or read-only commands on the
host. Candidate commands for a Docker host, each **not yet verified** on every platform (check they exist
first; substitute the real container name):

```sh
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}'          # running containers and published ports
docker port <frigate-container>                                   # published ports for Frigate only
docker inspect --format '{{.HostConfig.Privileged}} {{.HostConfig.NetworkMode}}' <frigate-container>
docker inspect --format '{{json .HostConfig.Devices}}' <frigate-container>    # passed-through devices
docker inspect --format '{{range .Mounts}}{{.Source}} -> {{.Destination}} {{.RW}}{{"\n"}}{{end}}' <frigate-container>
docker image inspect --format '{{.Created}}' <frigate-image>      # how old the image is
ss -tulpn                                                         # host listeners (Linux)
# Count, without printing, stream URLs with an inline password rather than a {FRIGATE_*} variable:
grep -cE '://[^/@ ]+:[^{@ ][^@ ]*@' <config-dir>/config.yml
grep -c '{FRIGATE_' <config-dir>/config.yml                       # how many values use substitution
```

- The Frigate UI shows its version (Settings or System pages); the release notes list fixed security
  advisories for each version.
- **Never** print `config.yml`, the output of `docker inspect` without a `--format` filter (it includes
  environment variables, which hold `FRIGATE_*` passwords and keys), `docker compose config`, a `.env`
  file, the `.jwt_secret` file, or unfiltered container logs (they may contain the generated admin
  password). Don't download the configuration through the API or the configuration editor.
- **Never** brute-force or guess Frigate, go2rtc, MQTT, or camera passwords; don't run exploit code or
  proof-of-concept scripts from advisories; don't scan the camera network aggressively (cameras crash;
  see the ip-cameras skill).
- Testing whether port 5000 or 1984 is reachable from another segment means opening a page with no
  credentials. Do it only from segments the user has put in scope, and stop at "the page loads".

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Version, image, and updates

- Running version and release series; compare with the current release and its notes. Recent releases
  have been largely security fixes, so being even one patch release behind can matter.
- Check the project's GitHub security advisories for the installed version; validate each per core triage.
- Image source: the official project image, or a third-party or community-packaged image? Pinned tag,
  `stable`, or a digest? How updates happen (manual pull, an auto-update tool, the Home Assistant app
  updater), and when the image was last pulled.
- Beta or release-candidate builds in production use.
- Startup version check (`telemetry.version_check`): if disabled for privacy, confirm another update
  notification exists.

#### B. Authentication, users, and roles

- Authentication enabled on 8971 (it is by default; `auth.enabled: false` turns it off).
- The generated admin password changed after first login; `auth.reset_admin_password` not left set to
  `true` (it resets and logs a new password on every restart while set).
- Users and roles: who has admin; viewer and custom camera-restricted roles where appropriate; accounts
  nobody recognizes or no longer needs. Passwords must be at least 12 characters.
- Login rate limiting (`auth.failed_login_rate_limit`) configured. Behind a proxy, `auth.trusted_proxies`
  set to the proxy only; otherwise the limit applies to the proxy's address and one attacker can lock
  everyone out.
- Session length (`auth.session_length`, default 24 hours) suitable for the devices used.
- JWT secret: where it comes from (environment variable, credentials file, the Home Assistant app option,
  or the generated `.jwt_secret` file) and who can read it. Anyone with it can mint sessions.
- **Proxy authentication** (Frigate's auth disabled in favor of an upstream proxy such as an identity
  provider): `proxy.auth_secret` set, so requests that skip the proxy are rejected; `header_map`,
  `default_role`, and `role_map` reviewed (a `default_role` of admin, or a broad group mapped to admin,
  gives everyone admin); and Frigate reachable only through that proxy.

#### C. Network exposure of Frigate ports

- Map every published port (compose file, `docker port`, Home Assistant app network settings, host
  firewall) to who can reach it: the host only, the Home Assistant instance, the user LAN, the IoT or
  camera network, VPN users, or the internet.
- **5000:** not published, or published only where a specific client (for example the Home Assistant
  integration on the same host) needs it, and blocked by firewall rules from every other segment. The
  integration's documentation recommends 8971 for a Frigate on a separate machine.
- **8971:** reachable from user and admin segments only; not from the camera network.
- **8554 (RTSP restream):** unauthenticated by default. If published, go2rtc RTSP username and password
  set, or the port limited to the clients that need it (Home Assistant, another NVR, a media player).
  Credentials don't apply to localhost requests.
- **8555 (WebRTC, TCP and UDP):** published only if WebRTC is used; never forwarded from the internet
  unless WebRTC remote viewing is deliberately designed (see domain H).
- **1984 (go2rtc API and UI):** should not be published at all in normal use. If it is, it is a P1 or
  higher finding: the go2rtc API has no Frigate authentication and the go2rtc project warns it gives
  "full access to your server".
- Host networking mode (`network_mode: host`) exposes every Frigate and go2rtc port on every host
  interface, regardless of the port list.
- IPv6: published ports may be reachable over IPv6 on the host.

#### D. TLS and certificates

- 8971 uses TLS by default with a self-signed certificate. On untrusted networks (Wi-Fi shared with
  others, VPN, the internet) a real certificate is expected, either mounted at
  `/etc/letsencrypt/live/frigate` or provided by a reverse proxy.
- `tls.enabled: false` is reasonable only when a reverse proxy terminates TLS and the hop between them is
  on the same host or a trusted network.
- Private key files: who can read them on the host.
- Clients set to ignore certificate errors (for example an integration with verification off); note these.

#### E. Camera credentials and go2rtc configuration

- Camera passwords inline in RTSP URLs versus `{FRIGATE_*}` environment-variable substitution (count, don't
  print; see the baseline). Substitution keeps passwords out of the file but puts them in the container's
  environment, the compose file or `.env`, or the Home Assistant app options; check who can read those.
- Camera accounts used by Frigate: a dedicated low-privilege viewing account on each camera rather than the
  camera's admin account (where the camera supports it; see the ip-cameras skill).
- The same password reused across cameras, or reused from Frigate or another system.
- go2rtc stream sources: `exec:`, `echo:`, and `expr:` sources are disabled by default. Check whether
  `GO2RTC_ALLOW_ARBITRARY_EXEC=true` is set in the environment; if it is, every stream definition is a
  path to running commands as root in the container, and anyone who can edit the configuration can use
  it. Record which sources need it.
- go2rtc settings in the configuration: RTSP credentials, any `api` or `webrtc` listen addresses, and ICE
  servers.
- Where the configuration is edited: the UI configuration editor (admin only), the host file, or the Home
  Assistant file editor. Each is a write path to the cameras' credentials.

#### F. MQTT

- Whether MQTT is enabled, which broker, and whether the broker is local, on another host, or cloud-hosted.
- Frigate authenticates to the broker with its own user (not anonymous, not a shared admin user);
  credentials supplied via `{FRIGATE_*}` substitution rather than inline.
- TLS to the broker when it isn't on the same host or a trusted segment.
- Broker ACLs: Frigate publishes events, and can publish snapshots, on its topics, so anyone who can
  subscribe can see detections and images. Frigate also accepts commands over MQTT (for example turning
  detection, recordings, or snapshots on or off per camera), so anyone who can publish to its topics can
  quietly stop recording. Check who can read and write the Frigate topic tree.
- Broker listener exposure (anonymous access, reachable from the IoT network or the internet); the broker
  itself is out of this skill's scope, but note what you find.

#### G. Generative AI, Frigate+, and other outbound data flows

- **Generative AI**: whether a `genai` provider is configured, and which cameras use it for object
  descriptions or review summaries. Cloud providers (OpenAI, Google Gemini, Azure OpenAI, Ollama Cloud)
  receive camera images and prompts over the internet. Local providers (Ollama or llama.cpp on a LAN
  server, OpenAI-compatible servers) keep data local, but the model server then holds images and must be
  assessed and access-controlled itself.
- Whether the household or organization has agreed to images (people, faces, license plates, neighbors,
  children) leaving the site; for work audiences, whether this is allowed under the organization's data
  protection rules.
- API keys for providers: stored via `{FRIGATE_*}` substitution, scoped and spend-limited at the provider,
  and not shared with other applications. An `OPENAI_BASE_URL` pointing somewhere unexpected redirects
  images.
- **Frigate+**: if an API key is configured, snapshots the user submits are uploaded to the Frigate+
  service. Removing the key stops all Frigate+ network activity.
- **Web push notifications**: delivered through browser vendors' push services when users register
  devices. Review registered devices.
- **Other outbound connections**: model downloads (one-time), the startup version check, and WebRTC
  STUN. When no ICE servers are set, the web UI may fall back to a public STUN server; set `ice_servers`
  to a local STUN or TURN server to avoid it.
- Egress from the Frigate host: whether it is restricted to what these features need.

#### H. Remote access

- How users watch from outside: VPN, reverse proxy, a tunnel service, Home Assistant's remote access, or a
  port forward. Port forwards to 5000, 1984, or 8554 are critical findings; a direct forward to 8971 is a
  finding (prefer VPN, or a proxy with an identity layer).
- **Reverse proxy:** pointed at 8971, not 5000. If the proxy handles authentication, Frigate's
  `proxy.auth_secret` is set and Frigate is not reachable around the proxy. `trusted_proxies` set.
  WebSocket paths proxied correctly (live view needs them).
- **Tunnels** (for example a cloud tunnel service): the tunnel's own access policy (identity provider,
  allowed users, MFA) in front of Frigate, not just a public hostname. A tunnel to 5000 is the same as
  publishing an unauthenticated admin UI.
- **Home Assistant:** if Frigate is reached through Home Assistant remotely, Home Assistant's own
  authentication and MFA protect it. The integration's public notification endpoints (snapshots, clips)
  served through Home Assistant's URL: check the integration's options for whether and how long they stay
  available (verify on the installed integration version).
- Mobile apps or third-party viewers that store Frigate or RTSP credentials.

#### I. Recordings, snapshots, and storage

- Retention (`record` continuous, motion, alerts, and detections `retain.days`; snapshots retention)
  matches what the user needs and is allowed to keep. Longer retention means more exposure; very short
  retention can lose evidence.
- Emergency cleanup: when free space runs low, Frigate deletes the oldest recordings regardless of
  retention. Frequent cleanup messages mean recordings are not kept as long as configured.
- Exports are never removed by retention; they accumulate and need their own review.
- Storage location (`/media/frigate`): local disk, NAS share (NFS/SMB), or cloud-synced folder. Who can
  read it on the host and on the network: a world-readable NFS export or an SMB share open to the LAN
  hands every recording to anyone on it. Whether it is encrypted at rest, and whether it is backed up
  (and where the backups go).
- The SQLite database and `/config` directory: permissions and backups.
- Integrity: a separate copy of important footage (for example the NAS's snapshots or another NVR) so an
  attacker with Frigate admin can't delete all evidence.

#### J. Container and host hardening

- `privileged: true`: needed for the user's hardware? The vendor notes it may not be necessary, and for
  some accelerators advises dropping it after setup. Prefer passing only the needed devices.
- Relaxed confinement (`apparmor=unconfined`, `systempaths=unconfined`, `security_opt` overrides), host
  networking, host PID, and any mount of the Docker socket.
- Mounts: only `/config`, `/media/frigate`, and needed devices; nothing broader (for example the host's
  root filesystem).
- Home Assistant Full Access variant with protection mode off: is it needed?
- Who has shell, `docker` group, or Home Assistant admin access to the host.
- Host updates, host firewall, and the host's own exposure (assess with the relevant OS skill).

#### K. Logging and monitoring

- Where Frigate and nginx logs go, how long they are kept, and who can read them (first-run passwords).
- Whether login failures, user changes, and configuration changes can be reviewed after the fact.
- Health monitoring: alerts when a camera goes offline or recording stops, so silent tampering (MQTT
  commands, a disabled camera, a full disk) is noticed.
- Time sync on the host, so recordings and logs line up with camera and firewall logs.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

List what depends on the setting before recommending a change:

- **Home Assistant integration:** which URL and port it uses; moving it from 5000 to 8971 can need TLS
  changes (the integration fails on a self-signed certificate) and credentials.
- **Restream clients:** Home Assistant cards, media players, other NVRs, or recorders pulling from 8554.
- **Reverse proxy, tunnel, or VPN:** which hostnames and ports they point at, and who uses them.
- **MQTT consumers:** automations and dashboards that rely on Frigate topics.
- **Cameras:** changing a camera password breaks every stream URL that uses it (Frigate, other NVRs,
  apps); the camera may also lock out repeated failed logins.
- **Storage:** NAS shares or volumes that recordings go to; backups of them.
- **Hardware:** detectors and GPUs that need device passthrough or privileges.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Port 5000 reachable from the LAN or beyond | Stop publishing it, or bind it to the host or a single trusted client, and block it at the host firewall. | The Home Assistant integration or other clients using 5000 must move to 8971 with credentials (and TLS handling). |
| Port 1984 published | Remove the mapping. | The standalone go2rtc UI is no longer reachable; Frigate's own UI still works. |
| Unauthenticated RTSP restream | Set go2rtc RTSP credentials, or limit 8554 to the clients that need it. | Every restream consumer needs the new credentials. |
| Frigate reachable from the internet (port forward or open tunnel) | Remove it; use a VPN, or a proxy or tunnel with identity-provider login and MFA in front of 8971. | Remote users need the VPN or identity login first; test it before removing the old path. |
| Proxy auth without `auth_secret`, or admin as `default_role` | Set the secret; map roles explicitly with a non-admin default. | Users whose groups aren't mapped lose admin. |
| Too many admins, unknown accounts | Remove or downgrade; viewer or camera-restricted roles for family and staff. | Those users lose settings access. |
| Outdated version | Update to the current release after reading its notes. | Restart; brief recording gap; configuration migrations may change files. |
| Inline camera and MQTT passwords | Move to `{FRIGATE_*}` substitution and protect where those values live. | Small config change; values move to the environment or app options. |
| Camera admin accounts used for streaming | Create a viewing-only account on each camera for Frigate. | Each camera's stream URL changes; PTZ or two-way audio may need more rights. |
| `GO2RTC_ALLOW_ARBITRARY_EXEC` set | Remove it, replacing exec sources with supported ones. | Streams that relied on exec sources stop; find alternatives first. |
| Cloud generative AI on sensitive cameras | Use a local model server, limit it to specific cameras, or disable it. | Lower-quality or slower descriptions; needs local hardware. |
| No TLS on untrusted paths | Use a real certificate on 8971 or at the proxy. | Certificate renewal must be maintained. |
| Privileged container | Replace with specific device passthrough. | Hardware acceleration may need testing; some accelerators need specific options. |
| Recordings on an open share | Restrict the share to the Frigate host (and backup system) only. | Other users lose direct file access to footage; exports remain available. |
| MQTT broker anonymous or flat ACLs | Per-client broker accounts; restrict who can publish to Frigate command topics. | Automations need their own credentials. |
| No offline-camera or recording alerts | Add monitoring. | Some noise from flaky cameras. |

Changing ports, hiding the UI path, and geoblocking are supplementary only. Never recommend them as the
main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet exposure, port 5000 or 1984 open,
critical updates) → high-priority hardening → routine maintenance → optional defense in depth. Then ask
for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Frigate specifics:

- **Before any change:** back up `/config` (configuration and database) to a protected location; it is
  secret material. Note the running image tag or digest so you can return to it.
- **Most changes need a Frigate restart (C2):** recording stops briefly for every camera. Tell the user
  and pick a quiet time.
- **Port and exposure changes:** edit the compose file or the Home Assistant app network settings, then
  recreate the container. Before removing 5000, move every client to 8971 and test it.
- **Keep a way in:** before disabling Frigate auth for proxy auth, or changing roles, confirm an admin
  login works on the new path. Know how to reset the admin password (`auth.reset_admin_password`, which
  logs a new password on the next start; turn it off again afterward).
- **Rotating the JWT secret** invalidates every session; all users must log in again.
- **Camera password changes:** change the password on the camera, then update Frigate (and every other
  consumer) right away; cameras can lock accounts after failed logins. Do one camera at a time.
- **Updates:** read the release notes for breaking configuration changes; pull the new image; recreate;
  verify every camera streams and records. Home Assistant app updates follow the app's own update path.
- **Retention changes:** shortening retention deletes older recordings at the next cleanup. That is C3;
  confirm the user doesn't need them as evidence first.

After each change, follow the core "after a change" steps: re-check published ports from the host and
from each in-scope segment, confirm login, live view, recording, and MQTT events work, and record before
and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Deleting recordings, exports, snapshots, or the database, or shortening retention so that existing
  recordings are purged, without the user's explicit decision.
- Printing or exporting the configuration, environment, JWT secret, or logs with credentials.
- Enabling `GO2RTC_ALLOW_ARBITRARY_EXEC` or adding exec stream sources.
- Testing camera, Frigate, or MQTT passwords by guessing; running advisory exploit code.
- Changing camera firmware or factory-resetting cameras (see the ip-cameras skill).
- Moving or reformatting recording storage.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the Frigate-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### NVR-001: Unauthenticated Frigate port 5000 reachable from the IoT network

**Confidence:** Confirmed
**Priority:** P1. Any device on the IoT network (smart plugs, TVs, the cameras themselves) can reach
Frigate's admin UI and API with no login, view every camera, read and change the configuration
(including camera passwords), and, given past advisories, potentially run code in the container.
**State:** Open
**Component:** Frigate 0.18.x in Docker on a Linux host, compose file port mappings
**Evidence:** Observed 2026-02-03: `docker port <frigate-container>` lists `5000/tcp -> 0.0.0.0:5000`
alongside 8971. The host has addresses on the user LAN (`192.0.2.20`) and the IoT network
(`198.51.100.20`). With the user's approval, a browser on a test device at `198.51.100.50` opened
`http://198.51.100.20:5000/` and showed the camera grid without a login prompt. The check stopped there.
**Expected secure state:** 5000 not published, or reachable only from the host or the one client that
needs it (Frigate documentation: "Access to this port should be limited").
**Exposure and prerequisites:** any device on the IoT or user LAN; no credentials needed.
**Dependencies / blast radius:** the Home Assistant integration uses `http://192.0.2.20:5000/`. Nothing
else uses 5000.
**Recommended remediation:** move the integration to 8971 with a dedicated Frigate account (and a valid
certificate or TLS handled as the integration documentation describes), then remove the 5000 mapping
from the compose file and recreate the container. Separately, review why the Frigate host has an address
on the IoT network at all.
**Operation class:** C2 (container recreate; recording gap; integration reconfiguration).
**Approval required:** Yes.
**Verification:** `docker port` no longer lists 5000; the test device gets a connection refusal on 5000
and a login page on 8971; the integration shows all cameras and events.
**Rollback:** restore the previous compose file and recreate the container.

---

## Version history

- **1.0** (2026-10-30): Initial version.
