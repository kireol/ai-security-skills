---
name: mqtt
description: >-
  Security assessment, hardening, remediation, and incident response for MQTT brokers, primarily Eclipse
  Mosquitto (standalone, in a container, or as the Home Assistant broker app), with generic guidance for
  other brokers. Use when auditing an MQTT broker, reviewing its listeners, anonymous access, password
  files, ACLs, TLS, WebSockets, retained messages, bridges, logging, or the credentials used by Home
  Assistant, Zigbee2MQTT, Frigate, and devices, or when a broker or its clients may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Eclipse Mosquitto 2.0 and 2.1 (verify the live version; 2.1 deprecates several options), other MQTT 3.1.1/5 brokers generically"
  audience: "home, homelab, work"
  finding_prefix: "MQTT"
  modes: "discover, recommend, remediate, respond"
---

# MQTT Broker Security

Act as a careful, evidence-driven IoT security engineer. In a home or lab, the MQTT broker is the control
bus: lights, locks, sirens, heating, cameras, and Zigbee networks take commands from topics, and sensors
report presence and camera snapshots to it. **Anyone who can publish to a command topic controls that
device, and anyone who can subscribe can watch the home.** Identify, explain, prioritize, remediate (only
when authorized), and verify weaknesses in who can connect, what each client may publish and read, and
how traffic and credentials are protected.

## How to use this skill

This skill holds only MQTT-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

MQTT-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation and
advisories are in [references.md](references.md). If Home Assistant uses the broker, also use the
[home-assistant](../home-assistant/SKILL.md) skill.

## MQTT-specific principles

- **Publishing is control.** There is no separate "admin" channel for devices: a client allowed to write
  to `zigbee2mqtt/<device>/set`, `frigate/<camera>/detect/set`, or a Home Assistant discovery topic can
  actuate devices, turn off detection, or create entities. Treat **every publish as a change** (C2 for
  anything that could move or disable something), and never publish to a production broker during
  Discover.
- **Subscribing is data access.** Payloads can include presence, door and lock states, alarm states,
  GPS locations, Zigbee2MQTT configuration, and JPEG camera snapshots. Subscribing to `#` (everything)
  needs explicit approval, should be time-limited, and should print topic names, not payloads.
- **Retained messages are a standing data store.** The broker replays the last retained message on each
  topic to every new subscriber, possibly long after the device stopped publishing, and retained
  commands are replayed to devices when they reconnect.
- **Configuration and password files are secrets.** Mosquitto's configuration can contain bridge
  passwords and PSKs in plain text; password files hold hashes (or plaintext if never converted); the
  dynamic-security JSON holds client definitions. Never print them whole. Read only what you need, with
  secrets redacted.
- **Verify the version before applying option names.** Mosquitto 2.0 changed default authentication
  behavior, and 2.1 (released January 2026) deprecated `per_listener_settings`, `password_file`, and
  `acl_file` in favor of listener options and plugins, to be removed in 3.0. The examples here use the
  long-standing option names; check the installed version's `mosquitto.conf` man page.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Mosquitto from OS packages** | Service `mosquitto`; configuration usually `/etc/mosquitto/mosquitto.conf` plus `conf.d/` (distribution default). | OS updates may lag upstream releases; check the package version against mosquitto.org. Runs as the unprivileged `mosquitto` user after reading configuration as root (2.0+), so runtime files must be readable by that user. |
| **Mosquitto container** (official image) | Container image `eclipse-mosquitto`; configuration usually under `/mosquitto/config/`. | Anyone with Docker access on the host can read the configuration and password files. Port publishing decides exposure (`-p 1883:1883` publishes on all host addresses). |
| **Home Assistant Mosquitto broker app** (add-on) | Installed under Settings → Apps on Home Assistant OS. | Authentication uses Home Assistant users plus the app's `logins` list; anonymous logins are not supported. `homeassistant` and `addons` are reserved users that need full access if ACLs are enabled. Ports: 1883 (MQTT), 1884 (WebSockets), 8883 and 8884 (TLS variants, active only with certificates). Extra configuration and ACLs go in `/share/mosquitto` when `customize` is enabled. |
| **Other brokers** (EMQX, HiveMQ, VerneMQ, NanoMQ, RabbitMQ MQTT plugin) | Product banner, admin dashboard, or `$SYS` topics. | Same model (listeners, authentication, topic ACLs, TLS, bridges), but option names differ, and many ship a web admin dashboard that is its own exposure. Use the product's own documentation. |
| **Cloud broker or bridge target** | A bridge `connection` block, or devices configured with a public hostname. | Data leaves the site; the cloud account and the bridge credentials become part of the trust boundary. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- TCP 1883 (MQTT, plaintext) and TCP 8883 (MQTT over TLS) are the IANA-registered ports. A TLS listener
  presents a certificate; a plaintext one answers an MQTT CONNECT with a CONNACK.
- MQTT over WebSockets has no single default in Mosquitto; it's set per listener. The Home Assistant
  broker app uses 1884 (plaintext) and 8884 (TLS). Other common choices are documented per product.
- Mosquitto publishes broker information under `$SYS/broker/` (including `$SYS/broker/version`) to
  clients allowed to read it.
- DNS-SD service type `_mqtt._tcp` (and `_secure-mqtt._tcp`) may be announced by some brokers or by an
  mDNS responder configured on the host; Mosquitto itself is not known to announce it (verify).
- Other brokers' admin dashboards (for example EMQX's web dashboard on its documented default port) are
  strong hints; check the product documentation.
- Often co-located with Home Assistant, Zigbee2MQTT (frontend on 8080 by default when enabled), and
  Frigate.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer reading the broker's configuration on the host (or through the Home Assistant app configuration
page) over connecting as a client. Configuration tells you who *should* get in; client connections are
only for confirming specific points, with approval. These are *candidate* read-only commands, **not yet
verified** on every version or platform. Check each exists first.

```sh
mosquitto -h | head -n 1                    # prints the broker version (not yet verified on every build)
ss -ltnp | grep -i mosquitto                # listening addresses and ports (Linux); sockstat -l on BSD
# Configuration with comments, blank lines, and secret-bearing lines removed:
grep -hvE '^\s*(#|$)|password|psk' /etc/mosquitto/mosquitto.conf /etc/mosquitto/conf.d/*.conf
ls -l <password-file> <acl-file> <dynsec-json>          # ownership and permissions only
cut -d: -f1 <password-file>                             # usernames only
awk -F: '{print $1, ($2 ~ /^\$/ ? "hashed" : "NOT HASHED")}' <password-file>   # flags plaintext entries
grep -vE '^\s*(#|$)' <acl-file>                         # ACL rules (no secrets in the ACL format)
openssl s_client -connect <broker-host>:8883 -brief </dev/null   # TLS version, certificate, chain
```

- The `grep` above drops `remote_password`, `local_password`, `bridge_psk`, and similar lines; note that
  they exist (bridge with a password) without reading their values.
- For the dynamic-security plugin, list clients, groups, and roles with `mosquitto_ctrl dynsec
  listClients`, `listGroups`, `listRoles`, and `getDefaultACLAccess` (vendor-documented commands; the
  admin credentials they need are full control of the broker, so prefer the user running them).
- **With explicit approval only** (connecting is a client action against a production broker):
  - Broker version from `$SYS`: `mosquitto_sub -h <broker-host> -p 8883 --cafile <ca-file> -u
    <audit-user> -t '$SYS/broker/version' -C 1 -W 5`. Don't put a password on the command line (it's
    visible in the process list and shell history); use an options file readable only by the user, or
    let the user run it.
  - Whether a listener accepts a connection **without credentials**, using the same `$SYS` read with no
    `-u`. This is a check of the user's own configuration, not a credential test: never try usernames
    or passwords.
  - A retained-topic inventory that prints **topic names only**: `mosquitto_sub ... -t '#' --retained-only
    -F '%t' -W 5`. Payloads are still transferred to the client, so run it from a trusted machine and don't
    log the output beyond topic names.
- **Never:** `cat` a password file, dynamic-security JSON, or the full configuration; print bridge or PSK
  values; publish any message (including empty retained messages to "clean up"); subscribe to `#` or to
  camera snapshot topics with payload output; run `mosquitto_passwd` (it modifies files, and `-U` rehashes
  in place and can make an already-hashed file unusable); send `SIGHUP` or restart the broker; try default
  or guessed credentials on any broker or dashboard.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Broker version and lifecycle

- Broker product and version; for Mosquitto, compare with the current release on mosquitto.org and the
  project's security advisories. Versions before 2.0 allowed anonymous access by default and should be
  treated as end-of-life (verify against the project's support statements).
- Packaging (OS package, container image tag, Home Assistant app version) and how it gets updated. A
  pinned container tag or a distribution package that lags upstream may miss security fixes.
- Plugins in use (dynamic security, password-file and ACL-file plugins in 2.1, third-party auth plugins
  such as mosquitto-go-auth) and their versions. Third-party plugins run inside the broker.
- Deprecated options in use on 2.1 (`per_listener_settings`, `password_file`, `acl_file`): not a
  vulnerability, but plan for removal in 3.0.

#### B. Listeners and network exposure

- Every `listener` line: port, bind address or `bind_interface`, protocol (`mqtt`, `websockets`, and on
  2.1 the experimental `http_api`), and `socket_domain`. A listener with no bind address listens on all
  interfaces. The deprecated `port`/`bind_address` options configure an implicit listener; check for them.
- Compare configured listeners with what's actually listening (`ss`, container port publishing, Home
  Assistant app network settings).
- Who can reach each listener: which VLANs/segments (IoT, cameras, guests) and whether any port is
  forwarded from the internet or published by UPnP. An internet-reachable plaintext 1883 is a P1 at least.
- Plaintext listeners left open alongside TLS ones ("we added 8883 but 1883 still works"). In the Home
  Assistant app, insecure ports can be disabled by leaving them blank.
- `http_api` listeners (2.1): the man page says authentication isn't currently possible; they should bind
  to loopback only, behind an authenticating reverse proxy.
- `enable_proxy_protocol`: the man page calls external access to such a listener a security risk.
- Connection limits (`max_connections`, and on 2.1 `global_max_connections`/`global_max_clients`) and
  `max_packet_size` (2.1 default 2,000,000 bytes) for basic resilience.

#### C. Authentication

- **Anonymous access:** Mosquitto 2.0+ refuses anonymous clients on configured listeners unless
  `allow_anonymous true` (or, on 2.1, `listener_allow_anonymous`) is set. With no listener configured at
  all, it accepts anonymous connections on loopback only. Check every listener's effective setting,
  including `per_listener_settings` interactions. Any anonymous listener reachable from the LAN is a
  finding unless it's read-only by ACL and justified.
- **Password file:** exists, used by every non-anonymous listener, entries all hashed (no plaintext),
  usernames recognized (one per client, no shared "devices" account), file owned by the broker user and not
  world-readable. `mosquitto_passwd` currently defaults to argon2id, with sha512-pbkdf2 also available and
  plain sha512 only for Mosquitto 1.6 compatibility; verify the default for the installed version.
- **Dynamic security:** clients (enabled/disabled), groups, roles, the anonymous group (2.1 creates an
  `unauthenticated` group), and who holds `$CONTROL/dynamic-security/#` access (equivalent to broker admin).
  Remove any leftover generated-password `.pw` file once passwords are known (vendor advice).
- **Certificates and PSK:** `require_certificate`, `use_identity_as_username` / `use_subject_as_username`
  (with these, the password file isn't used for that listener, and any certificate signed by the
  configured CA gets in), CRL in use, `disable_client_cert_date_checks` (accepts expired certificates).
  PSK files: identities and key strength (don't read keys).
- **Home Assistant app:** Home Assistant users that are used as MQTT logins (any Home Assistant user can
  authenticate to the broker), entries under `logins`, and whether `password_pre_hashed` is used.
- `use_username_as_clientid`: helps stop one client disconnecting another by reusing its client ID.
- Other brokers: default admin/dashboard accounts changed (ask; never test), and auth backends.

#### D. Authorization (ACLs)

- **Is there any ACL at all?** Without `acl_file`, an ACL plugin, or dynamic security, every authenticated
  client can read and write every topic, so any device credential controls every device.
- With an ACL file: per-`user` blocks, `pattern` lines with `%u`/`%c`, and the top-of-file rules that
  apply to anonymous clients. When an ACL file is set, only listed topics are allowed; `topic` with no
  access type means read/write; `deny` rules are evaluated first.
- Least privilege per client: a sensor should only write its own state topic; Zigbee2MQTT needs its own
  base topic (default `zigbee2mqtt`) and the Home Assistant discovery prefix; Frigate needs its own prefix
  (default `frigate`); Home Assistant needs broad access but nothing else should.
- **Who can write command topics:** list every client that can publish to `.../set`, Zigbee2MQTT's
  `bridge/request/#` (permit join, options, device removal, OTA updates, restart, raw actions, and the
  `backup` request that returns a zip of the data folder), Frigate's `/set`, `ptz`, and notification
  topics, and the Home Assistant discovery prefix (default `homeassistant`) and status topic
  (`homeassistant/status`). Each one is a control path.
- **Who can read sensitive topics:** camera snapshot topics (Frigate publishes JPEGs on
  `frigate/<camera>/<object>/snapshot`), Zigbee2MQTT `bridge/info` (full configuration except the network
  key), `bridge/response/#` (including backup responses), presence and location topics, lock and alarm
  states.
- `$SYS` read access (version and client counts help attackers fingerprint; restrict to admins).
- Wildcard grants (`#`, `+/#`) to non-admin users, and `readwrite` where `read` or `write` would do.
- Dynamic security default ACL access (on first configuration: publish-send deny, publish-receive allow,
  subscribe deny, unsubscribe allow): check it hasn't been loosened.

#### E. Encryption (TLS)

- Whether credentials cross untrusted segments in plaintext (1883 or plaintext WebSockets). On a shared or
  IoT segment, a passive listener gets every username, password, and payload.
- TLS listeners: `certfile`/`keyfile` (key readable only by the broker user), certificate validity and
  name, `tls_version` (2.0+ treats it as a minimum; TLS 1.0 removed), ciphers.
- Clients actually using TLS and validating the server: Home Assistant ("Ignore broker certificate
  validation" off), Zigbee2MQTT (`mqtts://` and `reject_unauthorized` left at its default `true`), Frigate,
  and device firmware (many cheap devices can't do TLS; isolate those instead).
- Client certificates where devices support them, and how they're issued and revoked.

#### F. WebSockets listeners

- Every `protocol websockets` listener: plaintext or TLS, bind address, and who can reach it. Browsers and
  dashboards use these, so they're often exposed more widely than 1883.
- `websockets_origin` (2.1) to restrict browser origins, if web clients are expected.
- Whether a reverse proxy fronts it and adds authentication; whether the proxy passes the real client
  address (and if `enable_proxy_protocol` is used, that only the proxy can reach the listener).
- Same authentication and ACLs as the MQTT listeners (check `per_listener_settings` doesn't give the
  WebSockets listener weaker settings).

#### G. Retained messages and persistence

- With approval, the retained-topic inventory (topic names only). Look for: retained **command** topics
  (`.../set` retained means the command replays every time the device reconnects), retained snapshots,
  retained presence/location, and stale discovery messages (Home Assistant warns retained discovery
  messages "can create ghost entities that keep coming back").
- Persistence: whether `persistence true` is set and where `persistence_location`/`mosquitto.db` is.
  The persistence file holds retained messages and queued messages, so protect and back it up like data.
- `persistent_client_expiration` (never by default): long-gone clients' queued messages pile up.
- `retain_available` and `check_retain_source` (default true: re-checks the publisher's access before
  delivering a retained message after an ACL change). Confirm it hasn't been turned off.

#### H. Integration and device credentials

- **Home Assistant:** broker username (dedicated, not shared with devices), TLS, birth/will settings, and
  where the credentials live (Home Assistant `.storage`). With the broker app, Home Assistant connects as
  the reserved `homeassistant` user.
- **Zigbee2MQTT:** MQTT `user`/`password` in `configuration.yaml` or moved to `secret.yaml` via `!secret`;
  its frontend (default port 8080 when enabled; 8099 through the Home Assistant app ingress) is
  **unauthenticated unless `auth_token` is set**, and the frontend can do everything the bridge request
  topics can (permit join, remove devices, OTA). Network key and coordinator backups in its data folder.
- **Frigate:** MQTT user/password in its configuration (check whether environment-variable substitution
  is used instead of literal values), and whether its prefix is protected by ACL.
- **Devices:** Tasmota, ESPHome, Shelly, and similar firmware store MQTT credentials on the device; anyone
  with access to the device's web UI can read or change them. Shared credentials across many devices mean
  one compromised plug controls everything.
- **Other clients:** Node-RED, dashboards, scripts, mobile apps, AI/MCP integrations with publish rights.

#### I. Bridges

- Every `connection` block: remote `address`, direction of each `topic` line (`out` is the default, `in`
  brings remote messages into the local broker, `both` does both), and the local/remote prefixes. An `in`
  or `both` bridge with a broad pattern lets the remote side publish local commands.
- TLS to the remote: `bridge_cafile`/`bridge_capath`/`bridge_tls_use_os_certs` set (otherwise the bridge
  is plaintext), `bridge_insecure` false (the man page says it should always be false in production),
  `bridge_tls_version`.
- Credentials: `remote_username`/`remote_password` or `bridge_psk` stored in the configuration (note the
  file's permissions; don't read the values). The cloud account behind them and what else it can do.
- What leaves the site: topics bridged `out` (presence, snapshots, alarm states) to a cloud broker or a
  third party.

#### J. Logging and monitoring

- `log_dest` (file, syslog, stdout under a container, `topic`), `log_type`, and `connection_messages`
  (connects and disconnects, with client ID and source address: the main evidence source).
- `log_type all` or `subscribe`/`unsubscribe` logging left on long term, and the Home Assistant app's
  `debug` option, which the vendor says logs sensitive information.
- `log_dest topic` publishes logs to `$SYS/broker/log/...`; check who can read that.
- Retention, rotation, off-host forwarding, and alerting on repeated authentication failures or unknown
  client IDs.

#### K. Host, files, and availability

- File ownership and permissions for configuration, password, ACL, dynamic-security, PSK, TLS key, and
  persistence files; the broker refuses symbolic links to sensitive files by default (don't recommend the
  `MOSQUITTO_UNSAFE_ALLOW_SYMLINKS` override).
- Broker not running as root (2.0+ drops to `mosquitto` by default; running as root is strongly
  discouraged by the vendor).
- Backups of configuration and dynamic-security files (contain hashes) and their protection.
- What stops working if the broker is down (Zigbee devices through Zigbee2MQTT, camera events, alarm
  integrations).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Every client that connects depends on the broker's listeners, credentials, and ACLs, so list them before
recommending a change:

- **Clients and their credentials:** Home Assistant, Zigbee2MQTT, Frigate, Z-Wave JS UI, Node-RED, device
  firmware, dashboards, scripts. Many devices can't be reconfigured remotely; changing their password or
  port means visiting each one.
- **Topics each client needs:** an ACL that's too tight silently drops publishes or subscriptions; devices
  look "unavailable" rather than erroring.
- **TLS capability:** which clients can do TLS and validate certificates, and which can't.
- **Bridges and cloud services:** what the remote side expects.
- **Retained state:** removing retained messages changes what devices and dashboards see on reconnect.
- **Automations:** Home Assistant automations that react to MQTT topics (some unlock or disarm).

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Anonymous access on a LAN-reachable listener | Disable it; give every client its own username. | Every anonymous client stops until configured with credentials. |
| Broker reachable from the internet | Remove the port forward/UPnP mapping; use a VPN or a TLS bridge. | Remote devices or apps must use the VPN. |
| No ACLs | Add per-client ACLs, starting with read-only defaults and explicit write grants for command topics. | Mistakes make devices silently stop; roll out per client and watch logs. |
| Shared device credentials | One username per device or integration. | Each device must be reconfigured; inventory first. |
| Plaintext on untrusted segments | Add a TLS listener, move capable clients, then restrict or remove 1883 to trusted segments or loopback. | Clients without TLS need a separate, isolated listener or replacement. |
| Plaintext WebSockets reachable widely | Use TLS WebSockets, restrict bind address and origins, or front with an authenticating proxy. | Browser dashboards need the new URL. |
| Plaintext entries in password file | Re-create those entries with `mosquitto_passwd` (not `-U` on a mixed file). | Clients keep working if passwords are unchanged; reload needed. |
| Command topics writable by sensors/devices | Restrict write on `.../set`, `bridge/request/#`, `frigate/+/+/set`, and the discovery prefix to the integrations that need it. | Devices that legitimately control others (wall switches) need explicit grants. |
| Zigbee2MQTT frontend without `auth_token` | Set `auth_token` and limit who can reach the frontend. | Users must enter the token; proxies must pass it. |
| Retained command messages | Fix the publisher not to retain commands; clear the retained message with approval. | The device may change state when cleared or reconnected. |
| Bridge `in`/`both` with broad patterns | Narrow to needed topics, prefer `out`; TLS with verification. | The remote side loses topics it was using. |
| `bridge_insecure true` or no bridge CA | Enable verification with the correct CA. | The bridge fails if the remote certificate is wrong; check first. |
| Debug or full logging long term | Return to default log types plus `connection_messages`. | Less detail for troubleshooting. |
| Broker outdated | Update to the current release; read the changelog for option deprecations. | Restart; 2.0-era configs may need changes on 2.1 (and before 3.0). |

Changing the broker's port is supplementary only. Never recommend it as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet exposure, anonymous access, no
ACLs on command topics) → high-priority hardening (per-client credentials, TLS, bridges, frontends) →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Mosquitto specifics:

- **Before any change:** copy the configuration directory, password file, ACL file, and dynamic-security
  JSON to a protected backup location; note file ownership and permissions.
- **Validate before reloading.** On 2.1, invalid password or ACL file contents make the broker quit on
  reload. Check syntax carefully, and keep a console or shell session on the broker host.
- **Reload versus restart:** password and ACL file changes take effect on `SIGHUP`; listener changes
  generally need a restart. Restarting disconnects every client. Both are C2.
- **Roll out ACLs gradually:** add rules for one client, reload, confirm its devices still work and the
  log shows no denials, then move to the next. Keep Home Assistant's account (and, in the app, the reserved
  `homeassistant` and `addons` users) at full access until its needs are mapped.
- **Disable anonymous access last,** after every client has working credentials, and watch
  `connection_messages` for refusals.
- **TLS migration:** add the TLS listener alongside plaintext, migrate clients one at a time, then restrict
  or remove plaintext.
- **Password changes:** use `mosquitto_passwd` interactively (not `-b`, which leaves the password in shell
  history and the process list); never run `-U` on a file that may already contain hashes.
- **Clearing retained messages** means publishing an empty retained message to that topic: that's a
  publish, so treat it as C2, confirm the topic with the user, and know what the device will do.
- **Home Assistant app:** change settings through the app's configuration page; files in `/share/mosquitto`
  only take effect with `customize` enabled.
- **If clients break:** restore the backed-up files and reload or restart.

After each change, follow the core "after a change" steps: re-read the effective configuration, check
`ss` output, watch the broker log for denials and refusals, and confirm with the user that devices,
dashboards, and automations respond.

### Hard stops (refer to a specialist or do manually; never automate)

- Publishing to command topics, Zigbee2MQTT `bridge/request/#`, or discovery topics to "test" ACLs.
- Mass-clearing retained messages or deleting the persistence file.
- Changing device firmware MQTT credentials remotely across many devices at once.
- Re-keying a Zigbee network or removing devices through Zigbee2MQTT as part of broker hardening.
- Running `mosquitto_passwd -U` on an existing password file, or deleting the password or dynamic-security
  files.
- Exposing the broker or any `http_api` listener to the internet for any reason.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the MQTT-specific steps
in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### MQTT-001: Anonymous LAN listener with no ACLs lets any device publish Zigbee commands

**Confidence:** Confirmed
**Priority:** P1. Any device on the LAN, including the IoT and guest segments, can connect without
credentials and publish to every topic, including Zigbee2MQTT's lock and permit-join topics and Frigate's
detection switches.
**State:** Open
**Component:** Mosquitto 2.0.x listener on TCP 1883, standalone container
**Evidence:** Observed 2026-01-16: the configuration (secret lines redacted) contains `listener 1883` with
no bind address and `allow_anonymous true`, and no `password_file`, `acl_file`, or plugin. `ss -ltnp`
shows the broker listening on `0.0.0.0:1883`. With approval, a connect-only read of `$SYS/broker/version`
without credentials from `192.0.2.40` (a laptop on the guest Wi-Fi) succeeded. The user confirmed the
guest Wi-Fi is not separated from the LAN.
**Expected secure state:** every client authenticates with its own credentials; ACLs limit each client
to its topics; command topics writable only by the integrations that need them (Mosquitto
authentication and ACL documentation).
**Exposure and prerequisites:** any device on the LAN or guest Wi-Fi; no credentials needed.
**Dependencies / blast radius:** Home Assistant, Zigbee2MQTT, Frigate, and eleven plugs with
device-stored settings connect anonymously today; two plugs can't be updated without physical access.
**Recommended remediation:** (1) create one user per client with `mosquitto_passwd`; (2) configure each
client and confirm it connects with credentials; (3) add a `password_file` and an ACL file granting each
client only its topics; (4) set `allow_anonymous false` and restart; (5) separately, isolate guest
Wi-Fi from the LAN at the firewall.
**Operation class:** C2 (every client must reconnect with new credentials; a restart disconnects all).
**Approval required:** Yes, per step.
**Verification:** the anonymous `$SYS` read from `192.0.2.40` is refused; the broker log shows every
expected client connecting with its username; devices respond in Home Assistant; no ACL denials for
legitimate topics.
**Rollback:** restore the backed-up configuration and restart (re-opens the exposure; use only to
recover a broken client, then retry).

---

## Version history

- **1.0** (2026-10-30): Initial version.
