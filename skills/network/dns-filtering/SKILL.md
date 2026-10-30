---
name: dns-filtering
description: >-
  Security assessment, hardening, remediation, and incident response for network-wide DNS filtering
  servers: AdGuard Home and Pi-hole (v6 and later), on bare metal, in containers, or in LXC containers and
  VMs. Use when auditing a DNS filtering server's admin UI and API access, listening interfaces and
  open-resolver exposure, upstream and encrypted DNS, DNSSEC, blocklist sources, local DNS records and
  rewrites, client bypass and firewall enforcement, redundancy, query logs, or updates, or when a DNS
  filtering server may have been compromised or is redirecting names.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "AdGuard Home v0.107.x stable (v0.108 is in beta) and Pi-hole v6.x (Core, FTL, Web); verify the live versions"
  audience: "home, work, homelab"
  finding_prefix: "DNS"
  modes: "discover, recommend, remediate, respond"
---

# DNS Filtering Server Security (AdGuard Home and Pi-hole)

Act as a careful, evidence-driven network security engineer. A DNS filtering server answers every name
lookup on the network, so whoever controls it decides where every device connects: a single malicious
rewrite or local record can send a bank, an update server, or a password manager to an attacker. It also
sees every name every client looks up, and when it stops, the whole network looks "down". Identify,
explain, prioritize, remediate (only when authorized), and verify weaknesses in the server, the lists it
trusts, and the network controls that make clients actually use it.

## How to use this skill

This skill holds only DNS-filtering-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

DNS-filtering-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and advisories are in [references.md](references.md).

If the DNS filter runs as a plugin or service on a firewall (for example, Unbound blocklists or an
AdGuard Home plugin on OPNsense), also use the firewall's skill: the firewall's own trust boundary and
plugin-repository rules apply there.

## DNS-filtering-specific principles

- **A DNS change is a network-wide change.** Upstreams, listening interfaces, blocklists, rewrites, local
  records, and service restarts affect every client at once. Treat any change that could stop resolution
  as **C2**, and assume the agent's own connectivity may depend on this server.
- **DNS answers are a redirection primitive.** AdGuard Home rewrites, `$dnsrewrite` rules, and hosts-style
  rules with a real address, and Pi-hole local DNS records (`dns.hosts`), CNAME records
  (`dns.cnameRecords`), conditional forwarding, and custom dnsmasq files, can each silently send a name to
  an attacker. Review every one as if it were a firewall port forward.
- **Blocklists are code from strangers.** Every subscribed list is fetched from a third party and applied
  automatically, usually on a schedule. In AdGuard Home, a list can contain more than blocks: a
  hosts-style line with a non-blocking address *answers* with that address, and the vendor documents that
  `$dnsrewrite` rules work in all rules in AdGuard Home (they are filtered out only of lists in AdGuard's
  curated registry). Treat list subscriptions as a supply-chain input.
- **Filtering is advisory unless the firewall enforces it.** Devices with hard-coded resolvers, browsers
  and apps with their own DNS over HTTPS (DoH), and VPN clients skip the filter entirely. DNS filtering
  is a convenience and privacy control, not a security boundary, unless outbound DNS to anywhere else is
  blocked at the firewall.
- **The admin credential is the whole server.** AdGuard Home has a single privilege level: its API uses
  HTTP Basic authentication with the web user's own credentials, so every integration holds full admin
  rights. Pi-hole v6 has a main password, an optional app password (which by default can't change
  settings, unless `webserver.api.app_sudo` is enabled), and a CLI password file.
- **Configuration and backups are secrets.** `AdGuardHome.yaml` holds the web users' bcrypt hashes and may
  hold a TLS private key or its path. `pihole.toml` holds the password hash, app-password hash, and TOTP
  secret. Pi-hole Teleporter exports bundle the configuration and databases. Never print, paste, or upload
  one whole; read only the keys you need and redact them.
- **Query logs are sensitive personal data and evidence at the same time.** They show every site every
  household or office member visits. Handle them under core privacy rules, and never flush them during
  an investigation.
- **The vendor files own the configuration.** AdGuard Home overwrites `AdGuardHome.yaml` while running
  (stop it before hand-editing). Pi-hole v6 settings set through `FTLCONF_` environment variables become
  read-only and override the file and the web UI, so in containers check the environment, not just the UI.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Pi-hole v6, bare metal or VM** | `pihole` and `pihole-FTL` commands; `/etc/pihole/pihole.toml`; web UI under `/admin/`. | Web server and REST API are built into `pihole-FTL` (no lighttpd or PHP since v6). Updated with `pihole -up`. The OS underneath needs its own patching and SSH hardening. |
| **Pi-hole in Docker** (`pihole/pihole`) | Container image tag (dated, `latest`, or `nightly`); settings in `FTLCONF_*` variables. | Updated by pulling a new image, not with `pihole -up`. With the default bridge network the vendor requires `listeningMode` `ALL`, so exposure depends entirely on which host address the ports are published on and on the host firewall. Without host networking, the server may see the bridge address instead of real client addresses, which weakens per-client rules and log evidence. |
| **AdGuard Home, bare metal or VM** | `AdGuardHome` binary, `AdGuardHome.yaml`, service installed with `-s install`. | Can self-update from the web UI (the previous binary and config are kept in a `backup` directory). The vendor says the install directory and binary should be owned by root and writable only by root. |
| **AdGuard Home in Docker** (`adguard/adguardhome`) | Volumes mapped to `/opt/adguardhome/work` and `/opt/adguardhome/conf`. | Self-update is disabled; update the image. DHCP needs host networking (Linux only). The documented port list includes a debug-profiling port (6060); don't publish it. |
| **Snap or Home Assistant add-on** (AdGuard Home) | Snap package or add-on panel. | The vendor disables self-update; updates come from the packaging channel, which may lag the vendor release. |
| **LXC container** (any hypervisor) | Unprivileged or privileged container on a hypervisor host. | The hypervisor host is part of the trust boundary. Check whether the container is privileged, and protect the host's admin interface. Snapshots are a useful pre-change rollback and evidence tool. |
| **On a router or firewall** (plugin or package) | Installed as a firewall plugin, often from a third-party repository. | Plugin-repository supply-chain risk and the firewall's admin model apply; use the firewall's skill too. |
| **Redundant pair** | Two servers handed out by DHCP; a sync tool between them. | Sync tools hold admin credentials for both servers and replicate changes (including malicious ones). Assess both nodes and the sync tool. |
| **Also the DHCP server** | Pi-hole `dhcp.active` true, or AdGuard Home DHCP enabled. | Lease data, static leases, and DHCP options (gateway and DNS pushed to clients) join the attack surface and the outage blast radius. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- Answers DNS on 53/UDP and 53/TCP, and is often the DNS server handed out by DHCP while not being the
  default gateway.
- **Pi-hole v6:** web UI on HTTP 80 and HTTPS 443 by default (FTL generates a self-signed certificate),
  served from `/admin/` with a Pi-hole login page; REST API under `/api/`. The default local name is
  `pi.hole`. The embedded NTP server is enabled by default on 123/UDP. A dnsmasq-style answer to a CHAOS
  `version.bind` query is a hint, not proof (not yet verified on every version).
- **AdGuard Home:** an unconfigured instance serves its setup wizard on TCP 3000 on all interfaces;
  after setup the web UI is usually on 80 (and 443 with encryption enabled), with an AdGuard Home login
  page and an API under `/control/`. With encryption enabled it may also answer DNS over TLS on 853/TCP,
  DNS over QUIC on 853/UDP, DoH on 443 at `/dns-query`, and DNSCrypt on 5443.
- Either may answer DHCP on 67/UDP if it is the DHCP server.
- No vendor mDNS or SSDP announcement is documented for either product; don't rely on discovery
  protocols.
- MAC vendor (OUI): often a single-board-computer maker (both products are popular on Raspberry Pi
  boards), but just as often a hypervisor or container bridge vendor, or the host's NIC. The MAC rarely
  identifies these products.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the web UI, the documented API with a session the user creates, or user-run checks. Labels:
**vendor-documented** commands appear in vendor docs; **not yet verified** commands must be checked to
exist and behave read-only on the installed version first.

Pi-hole v6 (on the host, or with `docker exec <container>` in front):

```sh
pihole -v                             # versions of Core, Web, FTL (vendor-documented)
pihole status                         # DNS and blocking state (vendor-documented)
pihole -q <domain>                    # which list or rule matches a domain (vendor-documented)
pihole-FTL --config dns.listeningMode # read one setting; omit the value to read (not yet verified)
pihole-FTL --config dns.upstreams     # same pattern for any key you need (not yet verified)
```

AdGuard Home:

```sh
./AdGuardHome -s status                # service status (vendor-documented)
./AdGuardHome --version                # version (not yet verified)
# API, authenticated as the admin, read-only GET calls (vendor OpenAPI spec; check paths per version):
#   /control/status  /control/dns_info  /control/access/list  /control/filtering/status
#   /control/rewrite/list  /control/querylog_info  /control/clients
```

Any host or container (generic tools):

```sh
ss -tulpn                              # what listens on 53, 80, 443, 853, 3000, 5443, 123, 67
docker ps --format '{{.Names}} {{.Image}} {{.Ports}}'   # published ports and host addresses
dig @<dns-host> example.com            # resolution works from a given client
dig @<dns-host> example.com +dnssec    # AD flag present when DNSSEC validation is in effect
```

- **Never run:** `pihole -up`, `pihole -g`, `pihole checkout`, `pihole repair`, `pihole setpassword`,
  `pihole disable`, `pihole reloaddns`, `pihole flush`, `pihole networkflush`, `pihole uninstall`, or
  `pihole debug` with upload (the debug log contains configuration and network details); `AdGuardHome
  --update` or `-s stop|restart|uninstall`; any POST, PUT, PATCH, or DELETE API call (Pi-hole
  `webserver.api.allow_destructive` is on by default, so some API calls restart DNS or flush logs).
- **Never** print whole `AdGuardHome.yaml`, `pihole.toml`, the Pi-hole CLI password file under
  `/etc/pihole`, or a Teleporter export. Read single keys and redact hashes, secrets, and key material.
- **Never complete an AdGuard Home setup wizard** you find open; report it (domain B) and let the owner
  finish it.
- Query-log reads are R but privacy-sensitive: read only what the finding needs, and summarize rather
  than copy.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, versions, and update channel

- Product, exact version, and deployment variant (above). For Pi-hole, record Core, Web, and FTL
  versions separately; for Docker, the image tag and digest.
- Whether the installed version is current. Check the vendor's GitHub security advisories and release
  notes (see references) live; both products have shipped fixes for authentication bypasses and web-UI
  injection flaws, so an old version is a real exposure, not just hygiene.
- Update channel: AdGuard Home release versus beta or edge builds; Pi-hole `master` versus a development
  branch selected with `pihole checkout`; Docker `latest` versus a pinned date tag versus `nightly`.
  Non-release channels on a production DNS server are a finding.
- Automatic image updaters (for example Watchtower) or AdGuard Home self-update: who decides when DNS
  restarts, and is there a rollback?
- Pi-hole only: a v5 installation is end-of-life for practical purposes (v6 is a one-way upgrade);
  confirm against vendor sources before rating it.
- The underlying OS, container host, or hypervisor: patched, and with its own admin access hardened.

#### B. Admin UI, authentication, and API credentials

- **Is authentication on at all?** AdGuard Home with an empty `users` list has no authentication. A
  Pi-hole with an empty password has no login (verify on the installed version). Either is a P1 when the
  UI is reachable from more than the admin's own host.
- **AdGuard Home setup wizard still open** on TCP 3000: anyone who reaches it can set the admin
  credentials. Report it immediately; don't complete it.
- Password quality is the user's to confirm; never guess or test passwords.
- **Second factor:** Pi-hole v6 supports TOTP (`webserver.api.totp_secret` set). AdGuard Home has no
  built-in second factor as of this review (verify on the installed version), so its UI should be
  reachable only from a management network or through an authenticating proxy.
- **Brute-force protection:** AdGuard Home `auth_attempts` and `block_auth_min` (0 disables blocking).
  Pi-hole rate-limits login attempts per second.
- **Sessions:** AdGuard Home `http.session_ttl`; Pi-hole `webserver.session.timeout` (default 1800 s) and
  `webserver.api.max_sessions`. Pi-hole shows active API sessions in its web UI settings (verify the
  menu name on the installed version); unknown sessions are a Respond trigger.
- **API credentials and integrations** (dashboards, home-automation integrations, sync tools, scripts):
  list each one, where its credential is stored, and what it can do.
  - AdGuard Home: every integration uses an admin username and password. Prefer a dedicated web user per
    integration so it can be removed alone; all users are still full admins.
  - Pi-hole: integrations should use the **app password**, not the main password, and
    `webserver.api.app_sudo` should be `false` unless an integration truly must change settings. An app
    password also bypasses TOTP, so treat it as a strong secret.
  - Pi-hole `webserver.api.cli_pw` (default true) writes a temporary clear-text password for the `pihole`
    CLI under `/etc/pihole`, regenerated on restart. Anyone who can read it gets an API session (vendor:
    it can't change configuration but can query data and manage lists). Check file permissions and who
    has shell access.
  - Pi-hole `webserver.api.localAPIauth`: whether localhost API calls skip authentication (verify the
    default on the installed version).
- **HTTPS for the UI:** AdGuard Home's Basic authentication and Pi-hole's session ID both cross the
  network on every request. Plain HTTP from anywhere but the local host is a finding. Check the
  certificate, AdGuard Home `force_https`, and that HTTP is redirected.
- **Reverse proxy in front:** AdGuard Home `trusted_proxies` contains only the proxy; Pi-hole
  `webserver.paths.prefix` and the proxy's own access controls. A proxy that publishes the admin UI to
  the internet is a P1 regardless of the login.
- Pi-hole `webserver.serve_all` should be `false` (otherwise every file in the webroot is served).
- AdGuard Home `http.pprof.enabled` should be `false` (profiling handler), and its port never published.

#### C. Network exposure and open-resolver risk

- **Which addresses DNS listens on.** Pi-hole `dns.listeningMode`: `LOCAL` (default; answers only clients
  on directly connected subnets), `SINGLE`, `BIND`, `ALL`, or `NONE`. The vendor calls permitting all
  origins "a dangerous thing to do". AdGuard Home `dns.bind_hosts` (all addresses is the common default).
- **Is it reachable from the internet?** Check router and firewall port forwards for 53, 853, 443, 5443,
  and the UI ports; IPv6 pass rules that expose the host directly; a VPS or cloud host with a public
  address; and Docker published ports (`0.0.0.0:53`). Docker inserts its own forwarding rules, which can
  bypass host firewall front-ends such as ufw. Test from outside only with explicit authorization, with a
  single benign query for a name you control or `example.com`.
- **An open resolver** (answers anyone on the internet) gets abused for reflection and amplification
  attacks, and the ISP or hosting provider may cut the line. AdGuard Home `allowed_clients` (allowlist
  mode, recommended by the vendor for public instances, ideally by ClientID), `disallowed_clients`,
  `refuse_any`, and `ratelimit` (default 20/s per subnet). Pi-hole `dns.rateLimit` (default 1000 queries
  per 60 s per client).
- **Which internal segments** (guest, IoT, cameras, VPN) can reach the admin UI, as opposed to just DNS.
  Clients need port 53 (and 853/443 for encrypted DNS); only admins need the UI ports. Pi-hole
  `webserver.acl` (empty allows all) and `webserver.port`; AdGuard Home `http.address`.
- Other listeners: Pi-hole's NTP server (enabled by default; disable if unused or limit by firewall),
  DHCP on 67/UDP, AdGuard Home DNSCrypt, DoQ, and the profiling port.
- AdGuard Home `serve_plain_dns`: on a public encrypted-only instance, plain DNS can be turned off once
  encrypted DNS is enabled.

#### D. Upstream resolvers, encrypted DNS, and DNSSEC

- **Upstream list:** who receives every query in clear text or encrypted, and is each one intended? An
  unfamiliar upstream is a Respond trigger (it sees and can falsify every answer).
  - AdGuard Home `upstream_dns` (and `upstream_dns_file`), `fallback_dns`, `bootstrap_dns`. Upstream
    URLs show the protocol: `tls://` (DoT), `https://` (DoH), `quic://` (DoQ), `sdns://` (DNSCrypt or
    DoH stamp). Per-domain upstreams (`[/example.com/]<upstream>`) route a single domain to a different
    resolver: review each.
  - Pi-hole `dns.upstreams` plus conditional forwarding (`dns.revServers`; verify the key name). Pi-hole
    doesn't encrypt upstream queries itself (verify on the installed version); encryption needs a local
    helper it forwards to (for example Unbound with DoT forwarding, or dnscrypt-proxy). The vendor's
    cloudflared guide now warns that cloudflared's proxy-dns feature is deprecated and that cloudflared
    updated after 2026-02-02 no longer works as the guide describes, so a cloudflared-based setup may
    silently break on update.
- **Local helper resolvers** (Unbound, cloudflared, dnscrypt-proxy): they should listen on loopback only
  (the vendor's Unbound guide uses `127.0.0.1#5335`) and be patched like any other service.
- **Encrypted DNS served to clients** (AdGuard Home DoH/DoT/DoQ): valid certificate, `strict_sni_check`
  as appropriate, `http.doh.insecure_enabled` (`allow_unencrypted_doh` before v0.107.74) only when a
  trusted TLS-terminating proxy sits in front.
- **DNSSEC:** Pi-hole `dns.dnssec` (default `false`) makes Pi-hole validate. AdGuard Home `enable_dnssec`
  sets the DO bit and relies on the upstream to validate (verify on the installed version). Note whether
  validation happens anywhere in the chain; `dig +dnssec` on a signed name should show the AD flag.
- ECS (EDNS Client Subnet): AdGuard Home `edns_client_subnet`; sending client subnets upstream is a
  privacy leak.
- Private reverse lookups: AdGuard Home `use_private_ptr_resolvers` and `local_ptr_upstreams`; Pi-hole
  `dns.bogusPriv` and `dns.domainNeeded`. Private names and addresses should not leak to public upstreams.

#### E. Blocklists and allowlists (supply chain)

- Every subscribed list: URL, maintainer, HTTPS (not HTTP), still maintained, and why it is there.
  Abandoned list domains can be re-registered by someone else.
- Update schedule (Pi-hole gravity runs weekly by default; AdGuard Home filter update interval).
- **AdGuard Home:** lists that contain hosts-style lines with non-blocking addresses, `$dnsrewrite`
  rules, or `@@` allow rules can redirect or unblock names. Check custom lists and lists outside the
  vendor's curated registry. Local file lists are limited by `filtering.safe_fs_patterns` (v0.107.53 and
  later); check it isn't widened to writable directories.
- **Pi-hole:** subscribed allowlists (allow-type subscriptions) unblock whatever their maintainer adds;
  confirm each one is intended. Check the domain counts after each gravity run for sudden jumps or drops.
- Allowlist and custom rules (AdGuard Home `user_rules` and allowlists; Pi-hole allow, deny, and regex
  entries): rules nobody remembers adding.
- Lists from paid or community "mega-lists": prefer fewer, maintained lists over many unknown ones.

#### F. Rewrites, local DNS records, and other redirection

- **AdGuard Home:** `filtering.rewrites`, `$dnsrewrite` in `user_rules`, `$client`/`$ctag` rules that
  give one device different answers, per-domain upstreams, and the Blocked services and Safe search
  settings.
- **Pi-hole:** Local DNS records (`dns.hosts`), CNAME records (`dns.cnameRecords`), conditional
  forwarding, and, if `misc.etc_dnsmasq_d` is enabled, every file in `/etc/dnsmasq.d/` (custom dnsmasq
  directives, including `address=` and `server=` lines, are a hidden redirection and persistence
  surface).
- For each record: the name, the answer, who owns the target, and whether it is still needed. Flag any
  record for an external domain (a bank, a software-update host, a cloud login) pointing at an internal
  or unknown address. That is a Respond trigger until explained.
- Local names that shadow public names (`<service>.example.com` answered locally) are normal for
  split-horizon setups; record them and confirm the owner.

#### G. Client enforcement and bypass

- What clients are told to use: the DHCP DNS option (and DHCPv6/router advertisement RDNSS on IPv6). If
  IPv6 clients get the ISP's resolver via router advertisements, filtering is bypassed on IPv6.
- Firewall egress: is outbound 53/UDP and 53/TCP to anywhere but the DNS filter blocked or redirected?
  Is 853/TCP and 853/UDP (DoT/DoQ) blocked? Without this, any device can bypass the filter.
- DoH can't be blocked by port. Check for: a DoH-provider blocklist, firewall aliases of known DoH
  endpoints, and managed browser policies. The `use-application-dns.net` canary domain (both products can
  block it) disables Firefox's *default* DoH only; it doesn't affect DoH a user turned on.
- Secondary DNS: if DHCP hands out a public resolver as the second server, clients use it at will.
- Is the DNS filter treated as a security boundary anywhere (for example, the only control keeping IoT
  devices away from malware domains)? If so, the bypass findings carry more weight.

#### H. Availability and redundancy

- How many DNS filtering servers do clients get? With one, a crash, update, power loss, or SD-card
  failure takes out name resolution for the whole network.
- If there are two, are they independent (different hosts, power, storage)? Does the sync tool hold
  admin credentials, and how is it secured?
- Fallback design: a public resolver as the second DHCP DNS server restores availability but bypasses
  filtering. Document the trade-off rather than hiding it.
- Storage health on single-board computers (SD cards wear out under logging), disk-usage warnings
  (Pi-hole `misc.check.disk`), and monitoring that alerts when DNS stops.
- Update and restart behavior: does an automatic update restart DNS during working hours?

#### I. Query logs, statistics, and privacy

- What is logged and for how long: Pi-hole `dns.queryLogging` (default on), `database.maxDBdays` (default
  91), `misc.privacylevel` (default 0, nothing hidden); AdGuard Home `querylog.enabled`,
  `querylog.interval`, `querylog.file_enabled`, `statistics.interval`, and `dns.anonymize_client_ip`.
- Who can read the logs: every admin, every integration, the host's backups, and anyone with shell
  access. Logs sent elsewhere (syslog, a dashboard) carry the same sensitivity.
- Whether logging is set to what the household or organization has agreed to. In a work setting,
  monitoring staff browsing may have legal requirements; flag it for the user rather than judging.
- Evidence value: whether logs are kept long enough to investigate an incident, and whether they are
  copied off the server. Balance this against privacy explicitly in the recommendation.
- Debug options that log more (Pi-hole `debug.queries`, `debug.api`): should be off in normal use.

#### J. Host, container, and backups

- Host OS: SSH keys-only, who has shell or `sudo`, other services sharing the host.
- AdGuard Home file ownership (vendor: root-owned, writable only by root) and whether it runs as root or
  as an unprivileged user with `CAP_NET_BIND_SERVICE`.
- Containers: image source (official image), privileged mode, host networking, mounted volumes, and the
  Docker socket (never mounted into this container).
- Backups of configuration (AdGuard Home `AdGuardHome.yaml`; Pi-hole Teleporter or `/etc/pihole`):
  where they go, whether encrypted, and whether a restore has been tested. They contain secrets.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Every device resolves through this server, so list what depends on the setting before recommending a
change:

- **Every client**, including the agent's own session and the admin's workstation: a mistake in
  upstreams, listening mode, or a restart stops resolution network-wide.
- **Local names** (rewrites, local records, conditional forwarding) that servers, reverse proxies,
  certificates, and home-automation systems rely on.
- **Integrations** using the admin or app password: dashboards, home-automation integrations, sync tools,
  scripts. Rotating a password breaks them until updated.
- **DHCP**, if this server provides it: leases, static leases, and the DNS and gateway options.
- **Allow rules** that keep business-critical or family-critical services working.
- **The firewall**, if enforcement rules (DNS redirect, DoT block) reference this server's address.
- **The second DNS server and the sync tool**, which replicate changes.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No authentication / open setup wizard | Set an admin password now (the owner, not the agent); restrict the UI to the admin network. | None for clients; integrations need credentials. |
| Admin UI reachable from untrusted segments | Restrict with firewall rules, Pi-hole `webserver.acl`, or AdGuard Home `http.address`. | Admins on those segments lose UI access; DNS keeps working. |
| Admin UI over plain HTTP | Enable HTTPS with a trusted or internal-CA certificate; redirect HTTP. | Bookmarks and integrations need the new URL; self-signed certificates prompt warnings. |
| No second factor (Pi-hole) | Enable TOTP; move integrations to the app password. | Admins need an authenticator app; scripts using the main password break. |
| No second factor possible (AdGuard Home) | Keep the UI on a management network or behind an authenticating proxy. | Remote admin needs a VPN. |
| Integrations hold the main password | Pi-hole: app password with `app_sudo` off. AdGuard Home: a separate web user per integration. | Each integration must be reconfigured. |
| DNS reachable from the internet | Remove the port forward or bind/publish only on the LAN address; if public by design, allowlist clients and rate-limit. | Remote users lose DNS unless they use the VPN. |
| `listeningMode` `ALL` / bind all on a multi-homed host | Pi-hole `LOCAL`; AdGuard Home specific `bind_hosts`. In Docker bridge mode, publish only on the LAN address instead. | Clients on non-local subnets (routed VLANs, VPN) may need explicit allowance; test from each. |
| Unintended or plain-text upstreams | Use chosen upstreams over DoT/DoH/DoQ (AdGuard Home), or a local loopback-only helper (Pi-hole). | The upstream sees all queries; helper adds a moving part; deprecated helpers may break. |
| DNSSEC not validated anywhere | Pi-hole `dns.dnssec` true, or a validating upstream/helper. | Misconfigured domains fail to resolve (SERVFAIL); have a way to diagnose. |
| Unknown or HTTP blocklists | Remove, or replace with maintained HTTPS lists. | Some ads or trackers return; fewer false positives. |
| Unexplained rewrites or local records | Treat as Respond first; then remove what the owner can't explain. | Services that relied on a legitimate record break; confirm with the owner. |
| No egress enforcement | Block or redirect outbound 53 and block 853 to anything but the DNS servers; block known DoH endpoints. | Devices with hard-coded DNS fail until redirected; some apps break; VPN clients need exceptions. |
| IPv6 clients get another resolver | Advertise the filter's IPv6 address (RDNSS/DHCPv6) or block IPv6 DNS elsewhere. | IPv6 changes affect every client. |
| Single DNS server | Add a second, independent server with a secured sync. | Another host to patch; sync credentials to protect. |
| Logs kept longer than needed / no privacy level | Shorten retention, raise Pi-hole `privacylevel` or AdGuard Home `anonymize_client_ip`. | Less evidence available for incidents; agree the trade-off with the user. |
| Pre-release channel / outdated | Move to the stable channel and update; pin container tags. | DNS restart; brief outage. |
| Destructive API allowed (Pi-hole) | Set `webserver.api.allow_destructive` false if no workflow needs it. | Restart and flush actions from the UI or API stop working. |

Changing the UI port or hiding the login page is supplementary only. Never recommend it as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (no authentication, internet exposure,
unexplained redirects, critical updates) → high-priority hardening → routine maintenance → optional
defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. DNS-filtering specifics:

- **Before any change:** export the configuration (AdGuard Home: copy `AdGuardHome.yaml` while the service
  is stopped, or use the host or container snapshot; Pi-hole: Teleporter export or a copy of
  `/etc/pihole`). Store it off the server and treat it as secret. On a VM or LXC, take a snapshot.
- **Keep resolution alive.** Make sure clients have a working second resolver or the user accepts a
  short outage, and make sure the agent's own session doesn't depend on the server being changed. Change
  the secondary first in a pair.
- **Use the supported method.** Web UI, documented API, `pihole-FTL --config`, or (AdGuard Home) the YAML
  file with the service stopped. In Docker Pi-hole, change the `FTLCONF_*` variable and recreate the
  container; a setting from the environment can't be changed in the UI.
- **Password and TOTP changes are done by the owner.** The agent never sets, sees, or stores the new
  password or TOTP secret. Update integrations immediately afterward.
- **Listening and binding changes** can cut off clients on routed subnets or VPNs. Test resolution from
  each segment immediately after the change, and keep console or hypervisor access.
- **Upstream changes:** test the new upstream with `dig @<upstream>` from the server first, then switch.
- **Blocklist removals and rewrite removals:** remove one at a time, run a gravity update or filter
  refresh, and test the names the owner cares about.
- **Firewall enforcement** is a firewall change: apply it with that skill's rules, starting with one test
  client or segment.
- **Updates:** read the release notes of every component (Pi-hole Core, Web, FTL). Self-update or `pihole
  -up` on bare metal, or pull the new image and recreate the container. Verify GPG signatures on AdGuard
  Home release builds where practical.

After each change, follow the core "after a change" steps: re-read the setting, resolve a public and a
local name from at least two segments, confirm blocking still works, check the admin UI, and record
before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Flushing query logs, the long-term database, or statistics, or deleting backups, during or after a
  suspected incident.
- `pihole uninstall`, `pihole networkflush --arp`, or deleting `/etc/pihole` or the AdGuard Home work
  directory as remediation.
- Hand-editing `AdGuardHome.yaml` while the service runs, or editing `pihole.toml` when the same key is
  set by an `FTLCONF_` variable.
- Uploading a `pihole debug` log or a Teleporter export anywhere.
- Completing an AdGuard Home setup wizard or setting credentials on the owner's behalf.
- Disabling filtering network-wide (`pihole disable`, AdGuard Home protection off) as a troubleshooting
  step without the user present.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the DNS-filtering
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### DNS-001: Local DNS record redirects a software-update domain to an unknown internal host

**Confidence:** Likely
**Priority:** P0 until explained. A redirect of an update domain lets whoever controls the target serve
software or credentials to every client that trusts the name.
**State:** Open
**Component:** Pi-hole v6 Local DNS records (`dns.hosts`), bare metal on a VM
**Evidence:** Observed 2026-03-04 in the web UI (Local DNS → DNS records) and with `pihole-FTL --config
dns.hosts`: an entry `192.0.2.66 updates.example.com`. `dig @192.0.2.53 updates.example.com` from a LAN
client returns `192.0.2.66`; public resolution of the name returns `203.0.113.40`. The owner doesn't
recognize the record. No other local records reference `192.0.2.66`.
**Expected secure state:** local records exist only for names the owner controls and documents
(Pi-hole configuration documentation, `dns.hosts`).
**Exposure and prerequisites:** every client using the Pi-hole. The attacker needed admin access to the
Pi-hole (UI, API, or shell) and control of `192.0.2.66`.
**Dependencies / blast radius:** none known; the domain belongs to a third-party vendor.
**Recommended remediation:** switch to Respond. Preserve the configuration, the query log, and the
session list first; identify `192.0.2.66` and which clients resolved the name; then remove the record and
rotate the Pi-hole password, app password, and TOTP secret (see incident-response.md).
**Operation class:** R for evidence collection; C1 to remove the record; C2 for credential rotation
(integrations break).
**Approval required:** Yes.
**Verification:** `dig @192.0.2.53 updates.example.com` returns the public answer; the record is gone in
the UI and in `dns.hosts`; no new unknown sessions.
**Rollback:** not applicable for the malicious record; restore from the pre-change export only if a
legitimate record was removed by mistake.

---

## Version history

- **1.0** (2026-10-30): Initial version.
