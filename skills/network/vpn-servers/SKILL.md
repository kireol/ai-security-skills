---
name: vpn-servers
description: >-
  Security assessment, hardening, remediation, and incident response for standalone WireGuard and OpenVPN
  servers on Linux or other hosts, including common wrappers (wg-easy, PiVPN, OpenVPN Access Server). Use
  when auditing a self-hosted VPN server, reviewing its peers, keys, certificates, revocation, routing
  scope, tunnel firewalling, 2FA, management web UI, client config handling, logging, or site-to-site
  links, or when a VPN server or one of its client credentials may have been compromised. VPNs built into
  a firewall (OPNsense, pfSense) are covered by that firewall's skill.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "WireGuard (Linux kernel module and wireguard-tools), OpenVPN community 2.6/2.7, wg-easy v15, PiVPN 4.x, OpenVPN Access Server 3.x (verify the live versions; wrapper menus and defaults change between releases)"
  audience: "home, work, homelab"
  finding_prefix: "VPN"
  modes: "discover, recommend, remediate, respond"
---

# WireGuard and OpenVPN Server Security

Act as a careful, evidence-driven network security engineer. A VPN server is a door into the network from
anywhere on the internet: every peer key, client certificate, and exported config file is a credential
that opens it, and whatever the tunnel interface is allowed to reach is what an attacker gets with one
stolen laptop or phone. A bad change can also cut off every remote user at once, including the user (and
the agent) if they are connected through the tunnel. Identify, explain, prioritize, remediate (only when
authorized), and verify weaknesses in the VPN server, the credentials it accepts, and the access it grants.

## How to use this skill

This skill holds only VPN-server-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

VPN-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation and
advisories are in [references.md](references.md).

If the VPN runs on a firewall (OPNsense, pfSense, a router's built-in VPN), use that firewall's skill
instead, for example [the OPNsense skill](../opnsense/SKILL.md); its VPN domain covers the same ideas in
that product's terms. Use this skill for the host OS only as far as it affects the VPN; the host itself
(patching, SSH, accounts) belongs to the relevant operating-system skill.

## VPN-specific principles

- **Every peer and every client certificate is a credential.** Treat the peer list and the issued
  certificate list like a user list: each entry should map to one named person and one device, have a
  known purpose, and be removable. "Shared" configs used by several people or devices can't be revoked
  for one of them without breaking all of them.
- **Private keys never appear in output.** WireGuard server and client configs, OpenVPN `.ovpn` profiles
  with inline `<key>` or `<tls-crypt>` blocks, QR codes, wrapper databases, and backup archives all contain
  private key material. Never print, paste, upload, or render one. Read only the specific lines you need,
  using filters that exclude key lines.
- **WireGuard has no revocation list.** A WireGuard peer is revoked only by removing its public key from
  the server (both the running interface and the persistent config). There's no certificate expiry, so a
  forgotten peer stays valid forever. WireGuard also has no built-in second factor.
- **OpenVPN revocation depends on a current CRL.** Revoking a certificate in the PKI does nothing until the
  server loads an updated CRL. The vendor manual notes that if the CRL file is missing, OpenVPN logs a
  warning but still allows the connection. A CRL also has a next-update date; how an expired CRL is
  handled depends on version and TLS library, so verify on the installed version.
- **AllowedIPs means different things on each side.** On the server, a peer's `AllowedIPs` is the set of
  source addresses that peer may use inside the tunnel and the destinations the server routes to it (so it
  should normally be one `/32` and one `/128`). On the client, `AllowedIPs` decides what the client sends
  into the tunnel (split versus full tunnel). It is **not** an access control on what the client can
  reach behind the server; only the host firewall does that.
- **The tunnel interface needs its own firewall policy.** Traffic from `wg0` or `tun0` is forwarded by the
  host's packet filter. Many install scripts and wrappers add a blanket forward-and-masquerade rule, which
  gives every peer the whole LAN. OpenVPN's `client-to-client` option routes client-to-client traffic
  inside the OpenVPN process, so it never reaches the host firewall at all.
- **Wrapper web UIs are part of the VPN's attack surface.** Anyone who can log in to wg-easy or the
  OpenVPN Access Server admin UI can create a peer or user and walk into the network. Treat those UIs as
  more sensitive than the VPN port itself.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Plain WireGuard** (`wg-quick` or systemd-networkd) | `/etc/wireguard/<if>.conf`, `wg-quick@<if>` service, or `.netdev` files. | Configuration is hand-managed. Check `SaveConfig`: when true, `wg-quick down` writes the running state back to the file, overwriting manual edits. `PostUp`/`PreUp` hooks run arbitrary commands as root. |
| **Plain OpenVPN community** | `openvpn-server@<name>` or `openvpn@<name>` service, `/etc/openvpn/server/`, an Easy-RSA PKI directory. | The PKI (CA key, issued certs, CRL) is the crown jewel. Check where the CA private key lives; ideally not on the VPN server. |
| **PiVPN** | `pivpn` command; installs plain WireGuard or OpenVPN; often on a single-board computer. | A shell-script installer and manager, not a daemon. The project states it's maintained on a best-effort basis. Generated client configs (with private keys) are kept on the server; check the location on the installed version. |
| **wg-easy** (container) | A container with a web UI (TCP 51821 by default) and WireGuard (UDP 51820 by default). v15 is the current major series. | The web UI can create peers and show their private keys and QR codes. The container's data volume holds every key. It needs elevated network capabilities on the host. |
| **OpenVPN Access Server** (commercial) | `sacli` command; Admin Web UI at `/admin`; `openvpnas` service. | Own user database, MFA, access rules, and firewall management. Admin and client web services listen on all interfaces by default. Check its release notes, not the community OpenVPN ones. |
| **Site-to-site** | A peer or client whose `AllowedIPs` / `iroute` covers a whole remote subnet. | The remote site's whole network becomes a source of traffic. Assess what it can reach as if it were an untrusted segment. |
| **Behind a firewall or router** | The server has a private address; a port forward exists upstream. | Real exposure depends on the upstream port forward. Check that only the VPN port is forwarded, not the wrapper web UI. |
| **Container or VM** | Container runtime or hypervisor. | The container host or hypervisor admin controls the VPN and its keys. Volume backups and snapshots contain private keys. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **WireGuard:** UDP 51820 is the conventional default. WireGuard doesn't answer unauthenticated packets,
  so scanners report the port as `open|filtered` and no banner exists. It usually can't be fingerprinted
  from the network; confirm with the user or from the host (`wg show`, a `wg0` interface).
- **OpenVPN community:** UDP 1194 by default (TCP 1194 or TCP 443 also common). A server with
  `tls-auth` or `tls-crypt` ignores packets without the right key and looks silent; one without them
  answers a protocol probe, which some scanners identify as OpenVPN.
- **wg-easy:** web UI on TCP 51821 by default, plain HTTP unless a reverse proxy sits in front. The page
  shows wg-easy / WireGuard branding (verify the exact title on the installed version).
- **OpenVPN Access Server:** TCP 943 for the Admin Web UI (`/admin`) and Client Web UI (`/`), TCP 443
  shared between the client web UI and the OpenVPN TCP daemon, UDP 1194 for tunnels. Upgraded systems may
  still listen on TCP 945 (legacy interface). A self-signed certificate on a fresh install.
- **PiVPN:** no network-visible service beyond the WireGuard or OpenVPN port it installs; often runs on a
  Raspberry Pi, so a Raspberry Pi OUI is a weak hint.
- No mDNS/DNS-SD or SSDP announcements are expected from these servers. MAC vendors aren't useful: this
  is software running on generic hardware, VMs, or containers.
- On a host, interfaces named `wg*` or `tun*`/`tap*`, and routes to a tunnel subnet, are the strongest
  signs.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer user-run checks or a read-only shell session. Most commands need root. Labels follow the core tool
contract: **vendor-documented** commands are from the WireGuard, OpenVPN, PiVPN, or Access Server docs;
everything else is **not yet verified** on every distribution. Check each exists first.

```sh
# WireGuard (vendor-documented: wg(8))
wg show                                # peers, endpoints, allowed IPs, last handshake; keys shown as (hidden)
wg show all latest-handshakes          # per-peer handshake time (epoch seconds; 0 = never)
wg show all allowed-ips                # per-peer allowed IPs
wg show all endpoints                  # per-peer last source address and port
# Config without key lines (not yet verified; adjust the interface name)
grep -E '^\s*(\[|ListenPort|Address|AllowedIPs|Endpoint|DNS|Table|MTU|SaveConfig|PreUp|PostUp|PreDown|PostDown)' /etc/wireguard/<if>.conf
ls -l /etc/wireguard/                  # file names and permissions only

# OpenVPN community (not yet verified; paths vary by distribution)
openvpn --version
grep -E '^\s*(port|proto|dev|server|topology|push|route|client-to-client|duplicate-cn|crl-verify|tls-auth|tls-crypt|tls-crypt-v2|data-ciphers|cipher|tls-version-min|verify-client-cert|remote-cert-tls|plugin|auth-user-pass-verify|auth-gen-token|username-as-common-name|client-config-dir|management|script-security|status|log|log-append|verb|user|group)\b' /etc/openvpn/server/*.conf
openssl crl -in <crl.pem> -noout -lastupdate -nextupdate     # CRL age and expiry
openssl x509 -in <issued-cert.crt> -noout -subject -enddate  # public certificate only

# PiVPN (vendor-documented)
pivpn -l                               # clients and their public keys
pivpn -c                               # connected clients

# OpenVPN Access Server (not yet verified; check sacli help on the installed version)
sacli status
sacli VPNStatus                        # connected users

# Host (not yet verified)
ss -lntup                              # listening sockets, including web UIs
ip -br addr; ip route; ip -6 route; ip rule
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
nft list ruleset                       # or: iptables -S; iptables -t nat -S; ip6tables -S
systemctl list-units 'wg-quick@*' 'openvpn*' --all
docker ps; docker port <container>     # wg-easy: published ports
```

**Never run** these, because they print or export private keys or secrets:

- `wg showconf <if>`, `wg show <if> private-key`, `wg show <if> preshared-keys`, `wg show <if> dump`, or
  anything with `WG_HIDE_KEYS=never`.
- `cat`, `less`, or `grep` without a key-excluding filter on `/etc/wireguard/*.conf`, OpenVPN server or
  client configs (inline `<key>`, `<tls-auth>`, `<tls-crypt>`, `<tls-crypt-v2>` blocks), `*.key` files,
  the Easy-RSA `pki/private/` directory, or the wg-easy data volume or database.
- `pivpn -qr` or any command or UI action that renders a client config or QR code.
- `docker inspect` or `docker compose config` on the wg-easy container without redaction (environment
  variables can hold initial passwords).
- Creating backups (`pivpn -bk`, configuration exports), which writes an archive of every key.

Also never run `easyrsa init-pki`, `easyrsa build-ca`, `wg genkey` into a live config path, or `pivpn -u`;
they are C3, not R (see hard stops).

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, versions, and lifecycle

- Which variant (see above), and the versions of WireGuard tools, the kernel, OpenVPN, the TLS library,
  and any wrapper. Check each against the vendor's current release and security announcements (core
  triage); OpenVPN publishes security announcements on its community wiki and Access Server publishes
  them in its release notes.
- OpenVPN community: whether the installed 2.x series is still supported (check the project's supported
  versions page). Access Server: whether the 2.x or 3.x line is in use and current.
- wg-easy: major version (v14 and v15 differ substantially; v15 has a migration guide), image tag (a
  pinned tag versus `latest`), and how the image is updated.
- PiVPN: version, and that the host OS packages (which actually ship WireGuard and OpenVPN) receive
  updates. PiVPN's own maintenance is best-effort.
- How the server is updated, and who is notified of new releases.

#### B. Peer and client inventory (credentials)

- Full list of WireGuard peers (public key, allowed IPs, last handshake, endpoint) and, for wrappers, the
  names attached to each. Map every peer to a person and a device. Unknown peers are a finding; a peer
  that nobody can identify is a potential incident (Respond).
- Peers with no handshake for a long time (`latest-handshakes` of 0 or months old): candidates for
  removal.
- Peers shared between devices or people (one config on several phones), visible as one peer whose
  endpoint jumps between unrelated networks.
- OpenVPN: issued certificates (Easy-RSA `pki/index.txt` lists status, expiry, and subject; reading it
  doesn't expose keys) versus who should have one. Certificates for departed users or lost devices that
  aren't revoked.
- `duplicate-cn` enabled: one certificate can be used by many clients at once, so a copied profile is
  indistinguishable from the owner.
- Access Server: local users, group membership, admin users, and whether the bootstrap admin account is
  still active with its install-time password.
- wg-easy: which accounts can log in to the web UI; disabled versus deleted clients; client expiry dates
  if the installed version supports them.

#### C. Keys, certificates, and revocation

- **WireGuard:** server key age (rotating it means reissuing every peer config, so it's usually rotated
  only after compromise); whether peers use a `PresharedKey` (an extra symmetric layer the vendor
  recommends for post-quantum resistance); whether any two peers share a key; file permissions on
  `/etc/wireguard` (root only; PiVPN documents `700`).
- Where client private keys were generated. If the server or wrapper generated them, the server holds
  every client's private key (wg-easy and PiVPN work this way), so a server compromise exposes every
  client identity as well. Generating keys on the client and registering only the public key avoids that.
- **OpenVPN PKI:** where the CA private key lives (ideally offline or on a separate system, not on the VPN
  server); whether it is passphrase-protected; CA and server certificate expiry dates; key sizes and
  signature algorithms.
- **CRL:** `crl-verify` present in the server config; the CRL file exists, is readable by the OpenVPN
  process after it drops privileges, and was regenerated after the last revocation; its next-update date
  is in the future, with a plan to regenerate it before then.
- `remote-cert-tls server` (or equivalent name verification) in client profiles, so a client can't be
  pointed at a rogue server holding any certificate from the same CA.
- `tls-crypt` or `tls-crypt-v2` (preferred) or `tls-auth` in use. They hide the server from scanners and
  reduce denial-of-service exposure. With `tls-crypt` (v1), every client shares one key, so one leaked
  profile lets anyone reach the TLS handshake; `tls-crypt-v2` uses per-client keys.
- `data-ciphers`: the 2.6 default is AES-256-GCM, AES-128-GCM, and CHACHA20-POLY1305. Legacy ciphers
  (BF-CBC and similar) listed for old clients, `cipher` used without `data-ciphers`, or compression
  enabled (`compress`, `comp-lzo`, `allow-compression yes`) are findings. Newer releases remove or reject
  some of these; check the release notes for the installed version.

#### D. Routing scope and allowed IPs

- **Server side (WireGuard):** each peer's `AllowedIPs` should be its own tunnel address only. A peer with
  a whole subnet is a site-to-site link and must be documented as one (domain I). A peer with
  `0.0.0.0/0` or `::/0` on the server attracts the server's routes for those destinations; that's a
  serious misconfiguration or an attack.
- **Client side:** full tunnel (`0.0.0.0/0, ::/0`) versus split tunnel (specific subnets). Neither is
  automatically right: full tunnel protects users on hostile networks but sends all their traffic through
  the server; split tunnel leaves the client's local network and internet path outside the VPN. Record
  which is in use and whether it matches the user's intent. A "full" tunnel that lists `0.0.0.0/0` but
  not `::/0` sends the client's IPv6 traffic outside the tunnel.
- **OpenVPN:** `push "route ..."` and `push "redirect-gateway ..."` statements; per-client
  `client-config-dir` files (`iroute`, fixed addresses, extra pushed routes); `topology`.
- DNS pushed to clients (`DNS =` in WireGuard configs, `push "dhcp-option DNS ..."` in OpenVPN): does it
  point at an internal resolver the user controls, and is the tunnel allowed to reach it?
- IP forwarding on the host: enabled only if peers need to reach beyond the server itself.

#### E. Tunnel firewalling (what VPN clients can reach)

- The host packet filter (`nft list ruleset` or `iptables -S`) for traffic arriving on `wg*` / `tun*`:
  is there a blanket `accept` on the forward path and a masquerade for the whole tunnel subnet? That
  gives every peer everything the server can reach: the LAN, admin interfaces, the NAS, the hypervisor.
- WireGuard `PostUp`/`PostDown` hooks and wrapper-generated rules: wg-easy and PiVPN add forwarding and
  NAT rules at startup. Read what they actually load, not just the config.
- Whether access is restricted per peer or per group (source address in the tunnel subnet matched to
  allowed destinations). Access Server has its own access rules per user and group; read those and the
  generated rules.
- OpenVPN `client-to-client`: if enabled, clients can reach each other without passing the host
  firewall. It's rarely needed.
- Whether VPN clients can reach the server's own management services (SSH, the wrapper web UI, the
  Access Server admin UI) and other admin interfaces on the network. Ideally only named admin peers can.
- IPv6: forwarding and filter rules for IPv6 exist and match the IPv4 policy; a tunnel with IPv6
  addresses and no IPv6 filter is a common gap.
- If the VPN server sits on a separate VLAN, the network firewall rules for that VLAN (cross-reference the
  firewall skill).

#### F. Authentication strength and 2FA

- **WireGuard:** key only, no second factor and no user login. Compensate with one peer per device,
  narrow per-peer firewall rules, prompt removal of lost devices, and device-level protection (screen
  lock, disk encryption). A wrapper's 2FA (for example wg-easy's TOTP) protects its web UI, not the
  tunnel.
- **OpenVPN community:** certificate plus a second factor where possible, typically through a plugin or
  `auth-user-pass-verify` script (PAM with a TOTP module, RADIUS, or LDAP), with `static-challenge` on
  the client to prompt for the code. Check that the username is tied to the certificate
  (`username-as-common-name` or a script that compares them), so one user's password can't be used with
  another's certificate. `auth-gen-token` avoids re-prompting on renegotiation; check its lifetime (0 or
  unset means it never expires).
- `verify-client-cert`: the default is `require`. `none` or `optional` means passwords alone (or the
  script) decide access; that's a finding unless deliberately designed.
- `script-security`: level 3 passes passwords to scripts in environment variables; the default is 1.
  Review any scripts it allows (they run on every connection).
- **Access Server:** TOTP MFA is off by default; it can be enforced globally, per group, or per user.
  Auto-login profiles don't follow the MFA requirement by default, and MFA doesn't apply to SAML logins
  (SAML relies on the identity provider's MFA). Check which users have auto-login profiles and whether
  the bootstrap admin account is subject to MFA and lockout on the installed version.
- Lockout or rate limiting for password-based OpenVPN logins and wrapper web UIs.

#### G. Exposed ports and management web UIs

- Exactly which ports are reachable from the internet (the upstream port forward and the host's own
  firewall), IPv4 and IPv6. Ideally only the VPN's UDP port. Test from outside only with explicit
  authorization.
- **wg-easy:** the web UI (TCP 51821) binds to all addresses by default (`HOST`). It must not be
  forwarded to the internet without a TLS reverse proxy and strong login; the vendor labels the
  no-proxy setup insecure and says to keep the UI local-only if `INSECURE=true`. Check `INSECURE`,
  `TRUSTED_PROXIES`, 2FA on every account, whether the first-run setup was completed before the UI was
  reachable, and the Prometheus metrics endpoint (off by default; if on, a bearer password should be set
  before it's exposed). Check what the published container ports bind to (`docker port`).
- **Access Server:** whether the Admin Web UI (TCP 943, `/admin`) is reachable from the internet; it can
  be bound to a specific interface (Web Services settings or `admin_ui.https.ip_address`). Whether the
  Client Web UI on TCP 443 must be public (it serves profile downloads and login, so it is a password
  attack surface). Legacy TCP 945 on upgraded 3.x systems, which the vendor says can be disabled. The
  web certificate (self-signed versus trusted).
- **OpenVPN management interface** (`management` directive): it gives full control of the daemon. It
  should listen only on a Unix socket or localhost with a password, never on a routable address.
- SSH and other services on the VPN host: reachable only from admin networks or admin peers.
- Hiding the VPN on a non-default port is not a control; don't credit it.

#### H. Client config files and key distribution

- Where client configs are stored on the server (PiVPN's configs directory, wg-easy's data volume,
  Access Server's profile downloads), their permissions, and whether old configs for removed peers are
  still lying around.
- How configs reach users: email, chat, and shared drives leave long-lived copies of private keys. QR
  codes shown on screen can be photographed. Prefer generating keys on the device, or a one-time
  in-person or authenticated transfer.
- Whether users store configs in cloud-synced folders or share them between devices.
- Access Server: auto-login profiles are bearer credentials (no password, no MFA by default); who has
  them and on which devices.
- Backups of the VPN server, container volume, or PKI: where they go, encryption, and who can read them.

#### I. Site-to-site trust

- Every site-to-site peer or client: which remote subnets it carries (`AllowedIPs` on WireGuard,
  `iroute` and `route` on OpenVPN) and what the local firewall lets that remote subnet reach.
- Is the trust two-way by default? A compromised remote site (a relative's house, a cloud VM, a
  colleague's lab) should not get full access to this network.
- Who controls the remote end, how it's patched, and whether its key is used anywhere else.
- Overlapping subnets or routes that could redirect traffic meant for a local network into the tunnel.
- Keepalives and endpoints: a site link with a static `Endpoint` to a dynamic DNS name depends on that DNS
  account; check its credentials and 2FA.

#### J. Logging, handshake monitoring, and time

- **WireGuard** logs almost nothing by default. Monitoring means polling `wg show all latest-handshakes`
  and `endpoints` (or a wrapper's metrics) and alerting on unknown endpoints, handshakes from peers that
  should be idle, or new peers. Check whether anything does this.
- **OpenVPN:** `log`/`log-append` destination or the journal, `verb` level (3 is the usual baseline),
  and a `status` file listing connected clients with their real source addresses. Logs should record
  connects, disconnects, authentication failures, and revocation rejections.
- **Access Server:** its log file and connection log, and whether they're forwarded off the host.
- **wg-easy:** container logs, and web UI login events if logged on the installed version.
- Remote logging to a separate system, retention, and whether anyone reviews connection history.
- Correct time on the server (NTP). WireGuard's vendor documentation notes that it relies on system time
  for replay protection, so the clock must not be attacker-controlled; time also matters for TOTP and
  log correlation.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

List what depends on the VPN before recommending a change:

- **The user's and the agent's own path:** is the current session running over this VPN? If so, any
  change to the interface, keys, firewall, or service can cut it off.
- **Every remote user and device:** who connects, from where, and what they need to reach. Removing a
  peer or revoking a certificate cuts that device off immediately.
- **Site-to-site links:** the remote site's services (backups, monitoring, DNS) that cross the tunnel.
- **Automation:** scripts, monitoring, or backups that connect through the VPN or read the wrapper API.
- **DNS:** clients pushed to an internal resolver lose name resolution if the tunnel's access to it is
  restricted.
- **Upstream firewall:** the port forward and any rules that match the tunnel subnet.
- **Shared keys:** server key or `tls-crypt` key rotation forces every client to get a new config.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Unknown or unused peers/certs | Remove WireGuard peers; revoke OpenVPN certificates and regenerate the CRL. | That device is cut off; confirm with the user first. |
| Shared configs | One peer or certificate per device and person. | Every affected device needs a new config. |
| Blanket forward rule on the tunnel | Allow each peer or group only the networks and ports it needs; deny the rest. | Users lose access to anything not listed; DNS must still be allowed if pushed. |
| `client-to-client` enabled | Remove it unless clients really need each other; filter on the host instead. | Client-to-client traffic stops. |
| Server-side AllowedIPs too broad | Set each road-warrior peer to its own `/32` and `/128`. | None for a correct peer; a site-to-site peer must be documented instead. |
| Wrapper web UI exposed to the internet | Remove the forward; reach the UI over the VPN or LAN only; add a TLS reverse proxy if remote access is needed. | Remote management requires a working VPN first. |
| No 2FA on wrapper UI | Enable TOTP for every web UI account (wg-easy, Access Server). | Admins need an authenticator; keep a recovery path. |
| No 2FA on OpenVPN | Add TOTP via plugin or Access Server MFA; tie usernames to certificates. | Users enroll; automated clients need a separate design. |
| Access Server auto-login profiles | Replace with user-locked profiles where MFA matters; restrict auto-login to devices that need it. | Users must log in on connect. |
| No or stale CRL | Add `crl-verify`, regenerate the CRL, schedule regeneration before its next-update date. | A wrong path or expired CRL can block clients, depending on version; test. |
| CA key on the VPN server | Move the CA to an offline or separate system. | Issuing and revoking becomes a separate procedure. |
| No `tls-crypt`/`tls-crypt-v2` | Add `tls-crypt-v2` (per-client keys) or at least `tls-crypt`. | Every client profile must be reissued; older clients may not support v2. |
| Legacy ciphers or compression | Remove legacy `cipher` fallbacks and compression. | Very old clients stop connecting; upgrade them first. |
| Management interface on a routable address | Bind it to a Unix socket or localhost with a password. | Tools using it remotely must change. |
| Server-generated client keys | For new peers, generate keys on the device and register the public key. | Slightly harder onboarding; wrappers may not support it. |
| Configs lying around on the server | Delete configs for removed peers; restrict permissions on the rest. | They can't be re-downloaded later. |
| No handshake/connection monitoring | Poll handshakes and endpoints, or send OpenVPN logs to a log server, and alert on unknown peers. | Needs a monitoring target. |
| Untrusted site-to-site peer | Restrict the remote subnet to specific services on the local side. | Remote services that relied on full access break. |
| No PresharedKey (WireGuard) | Add a per-peer PresharedKey for long-term confidentiality. | Each peer config must be updated. |
| Outdated server or wrapper | Update within the current series; read release notes for breaking changes (wg-easy v14 to v15, Access Server major versions). | Restart drops all tunnels briefly. |

Changing the VPN port and geoblocking are supplementary only. Never recommend them as the main fix.

Group the plan: immediate containment (unknown peers, exposed admin UI) → urgent fixes (critical updates,
missing revocation) → high-priority hardening (tunnel firewalling, 2FA) → routine maintenance → optional
defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. VPN specifics:

- **Before any change:** back up the configuration (and PKI or wrapper data volume) to protected storage,
  without displaying it. On a VM or container host, a snapshot is a good rollback point.
- **Never change the VPN you're connected through** without a second path in (LAN, console, or another
  VPN) that has been tested first.
- **Peer removal (WireGuard):** remove from the running interface (`wg set <if> peer <public-key>
  remove`) **and** from the persistent config, or the peer comes back on restart. With `SaveConfig = true`,
  edit only while the interface is down, or the running state overwrites the file. Prefer
  `wg syncconf <if> <(wg-quick strip <if>)` to apply config changes without dropping other peers (verify
  on the installed version). For wrappers, use the wrapper (wg-easy UI, `pivpn -r`), not raw `wg`.
- **Revocation (OpenVPN):** revoke in the PKI, regenerate the CRL, install it where `crl-verify` points,
  check its permissions and next-update date, and confirm the revoked client is rejected. Disconnect any
  live session of the revoked client (the management interface or a restart); verify whether the
  installed version rechecks the CRL for existing sessions.
- **Firewall changes:** add the narrow allow rules first, test from a peer, then remove the blanket rule
  as a separate step. Make sure wrapper or `PostUp` hooks won't re-add the old rule on the next restart.
- **Restarts** (`wg-quick`, OpenVPN, the wg-easy container, Access Server) drop every tunnel: C2, in a
  window the user agrees to.
- **Key or tls-crypt rotation** forces every client to get a new config: plan distribution before
  rotating, and treat it as a cutover with a window the user agrees to.
- **Wrapper updates:** read release notes first (wg-easy v15 changed configuration and needs a migration;
  Access Server releases can change defaults). Pin a known image tag.

After each change, follow the core "after a change" steps: re-read the setting and the loaded firewall
rules, confirm a test peer connects and reaches only what it should, confirm the user's own access, and
record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Printing, copying, or transmitting any private key, client config, QR code, or PKI file, for any reason.
- `easyrsa init-pki` or `easyrsa build-ca` on an existing PKI (wipes or replaces the CA and invalidates
  every certificate), or deleting the PKI directory.
- Regenerating the WireGuard server key or the OpenVPN CA as a routine fix; it cuts off every client. Only
  as part of an agreed incident recovery.
- `pivpn -u`, removing the wg-easy data volume, or uninstalling Access Server.
- Flushing the host firewall (`nft flush ruleset`, `iptables -F`) as a troubleshooting step.
- Testing credentials, guessing passwords, or running exploit code against the VPN or its web UI.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the VPN-specific steps
in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### VPN-001: Every WireGuard peer can reach the whole LAN, including admin interfaces

**Confidence:** Confirmed
**Priority:** P2. Any one lost phone or leaked config gives full LAN access, including the hypervisor and
NAS admin pages; it needs a valid peer key, so it's not directly internet-exploitable.
**State:** Open
**Component:** wg-easy v15 container, host nftables ruleset
**Evidence:** Observed 2026-02-03: `wg show` lists 9 peers; the user recognizes 7. The loaded ruleset has a
forward rule accepting all traffic from `wg0` and a masquerade for the tunnel subnet `198.51.100.0/24`.
From a test peer at `198.51.100.5`, with approval, the NAS admin page at `192.0.2.20` and the hypervisor
UI at `192.0.2.30` loaded. Two peers last handshook over 300 days ago.
**Expected secure state:** each peer reaches only the services it needs; unknown and unused peers removed
(see the peer and firewalling domains of this skill).
**Exposure and prerequisites:** any holder of a peer private key, from anywhere on the internet.
**Dependencies / blast radius:** the user's phone and laptop use the VPN for the media server and DNS; one
peer is a family member's tablet that only needs the media server.
**Recommended remediation:** remove the two unknown peers (after the user confirms they're not theirs; if
not, switch to Respond). Replace the blanket forward rule with per-peer allow rules: DNS and the media
server for everyone, admin interfaces only from the user's laptop peer. Persist the rules in wg-easy's
hook settings (verify where on the installed version) so they survive restarts.
**Operation class:** C2 (changes what every peer can reach; the container restart drops tunnels).
**Approval required:** Yes.
**Verification:** from the tablet peer, the media server works and the NAS admin page does not; from the
laptop peer, admin pages work; `wg show` lists only known peers; the rules are still in place after a
container restart.
**Rollback:** restore the previous hook configuration and restart the container.

---

## Version history

- **1.0** (2026-10-30): Initial version.
