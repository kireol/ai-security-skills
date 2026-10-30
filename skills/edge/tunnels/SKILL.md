---
name: tunnels
description: >-
  Security assessment, hardening, remediation, and incident response for tunnels and service-publishing
  tools other than Cloudflare Tunnel: ngrok, Tailscale Funnel and Serve, frp (fast reverse proxy), Pangolin,
  zrok/OpenZiti, localtunnel-style tools, Microsoft Dev Tunnels and VS Code port forwarding or remote
  tunnels, SSH reverse tunnels, and mesh VPNs (Tailscale, Headscale, ZeroTier, NetBird) where they publish
  services or extend network access. Use when inventorying what is published from a home or work network
  and who can reach it, reviewing authentication in front of tunneled services, agent credentials, frp or
  Pangolin servers, mesh VPN ACLs, subnet routers, and exit nodes, or when a tunnel agent may have been
  installed or abused by an attacker.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "ngrok agent v3 and Traffic Policy, Tailscale (Serve, Funnel, subnet routers, exit nodes), Headscale, frp 0.5x and later (TOML/YAML/JSON configuration), Pangolin with Newt, zrok 1.x/2.x, Microsoft Dev Tunnels CLI and VS Code port forwarding/remote tunnels, OpenSSH remote forwarding, ZeroTier, NetBird (verify the live versions; CLIs, flags, and defaults change often)"
  audience: "home, work, homelab, web"
  finding_prefix: "TUN"
  modes: "discover, recommend, remediate, respond"
---

# Tunnels and Service-Publishing Security

Act as a careful, evidence-driven network and edge security engineer. A tunnel agent makes an outbound
connection to a relay and then accepts inbound traffic through it, so a service behind a firewall with no
port forwards can still be on the internet. Firewalls, router port-forward lists, and external port scans
don't show these paths, which is why tunnels are easy to forget and why attackers like them. Answer one
question for every tunnel: **what is reachable from where, and who can reach it?** Identify, explain,
prioritize, remediate (only when authorized), and verify weaknesses in tunnel agents, the endpoints they
publish, the credentials they hold, the servers they connect to, and the mesh networks that extend access
into the LAN.

## How to use this skill

This skill holds only tunnel-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Tunnel-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and threat reporting are in [references.md](references.md).

Related skills: Cloudflare Tunnel (`cloudflared`) has its own skill, [cloudflare](../cloudflare/SKILL.md);
use it for Cloudflare accounts and tunnels and don't repeat that work here. Self-hosted WireGuard and
OpenVPN servers are covered by [vpn-servers](../../network/vpn-servers/SKILL.md). The host each agent runs
on is covered by the operating-system skills ([linux](../../operating-systems/linux/SKILL.md),
[macos](../../operating-systems/macos/SKILL.md), [windows](../../operating-systems/windows/SKILL.md)) and
[docker](../../containers/docker/SKILL.md) for containers.

## Tunnel-specific principles

- **Inventory beats configuration review.** A tunnel you don't know about can't be assessed. Every host,
  VM, container, NAS app, and developer laptop is a candidate. Start with domain A and treat every agent
  nobody can explain as a possible compromise until shown otherwise.
- **Every published URL is an exposure, and a hard-to-guess name is not a control.** Free-tier and random
  hostnames are discoverable: ngrok's free plan gives each account one fixed assigned domain that doesn't
  change between restarts, Tailscale documents that enabling HTTPS publishes machine and tailnet names in
  public certificate transparency logs, and URLs leak through chat, browser history, referrers, and logs.
  A published service without authentication in front of it is internet-exposed.
- **Public and private modes look alike.** Tailscale **Serve** shares a service with the tailnet only;
  **Funnel** makes it public on the internet, and the most recent command for a port decides which one
  applies. Dev Tunnels are private to the creating account by default but can be opened with
  `--allow-anonymous`. zrok has public and private shares, and a public share can also be reached
  privately. Always record which mode each endpoint is in, from the tool's own status output.
- **Agent credentials are secrets.** ngrok authtokens and API keys, frp `auth.token` values, Tailscale auth
  keys and node state, Dev Tunnels access tokens, Pangolin site (Newt) credentials, zrok account and share
  tokens, and the SSH keys behind persistent `ssh -R` sessions all let someone publish or receive traffic
  as the user. Never print, paste, upload, or log them.
- **Starting or stopping a tunnel is a change.** Stopping one can break a service someone relies on or
  destroy evidence; starting one creates a new exposure. Both are at least **C2**. Deleting a tunnel,
  reserved domain, share, or mesh node is **C3** when it can't be recreated with the same identity.
- **A mesh VPN is a network, not a tunnel to one service.** Subnet routers and exit nodes extend access to
  whole LANs or route other people's traffic out through the user's internet connection. Assess them like
  a VPN: who can reach what, enforced by which policy.
- **Legitimate tools are also attacker tools.** CISA has reported state-sponsored actors implanting ngrok
  for persistence and FRP clients for command and control, and MITRE ATT&CK tracks IDE tunneling (VS Code
  and Dev Tunnels) as a remote-access technique. An unexpected agent is a Respond trigger, not a hygiene
  note.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **ngrok agent** | `ngrok` binary, service (`ngrok service install`), or container; `ngrok.yml` (v3 format); endpoints in the ngrok dashboard. | Authentication is added with Traffic Policy (OAuth, OIDC, JWT validation, IP restrictions, basic auth, rate limiting); the older `--oauth`, `--basic-auth`, and `--cidr-allow` flags for `ngrok http` are deprecated in favor of Traffic Policy. A local inspection UI records request and response bodies. |
| **Tailscale Serve** | `tailscale serve` configuration on a node; HTTPS on the node's tailnet name. | Reachable only from the tailnet, subject to the tailnet policy. Persists across reboots when started with `--bg`. |
| **Tailscale Funnel** | `tailscale funnel` configuration; a `funnel` node attribute in the tailnet policy file. | Public on the internet on ports 443, 8443, or 10000 through Tailscale's relays. No Tailscale identity is required to reach it; the service's own authentication is the only barrier. |
| **Mesh VPN** (Tailscale, Headscale, ZeroTier, NetBird) | `tailscaled`, `headscale`, `zerotier-one`, or `netbird` services; an admin console or self-hosted control server. | Access policy (ACLs or grants), device approval, key expiry, auth keys, subnet routes, and exit nodes decide reach. With Headscale or self-hosted NetBird/ZeroTier controllers, the control server is also yours to secure. |
| **frp** (fast reverse proxy) | `frpc` on internal hosts and `frps` on a public server; TOML, YAML, or JSON config (INI deprecated). | You run the public server. Its bind port, dashboard, `auth.token` or OIDC, `allowPorts`, and TLS settings are all in scope. `frpc` doesn't verify the server certificate unless configured to. |
| **Pangolin** | A Pangolin server (often on a VPS, with Gerbil and Traefik) and Newt site connectors on internal hosts. | Public resources get Pangolin SSO by default; other methods (PIN, passcode, email OTP, header auth, share links, mTLS) and access rules can be added or loosened per resource. The server is internet-facing and is yours to secure. |
| **zrok / OpenZiti** | `zrok` or `zrok2` CLI, `zrok share` processes; hosted service or a self-hosted instance. | Public shares are on the internet; private shares need `zrok access private` and the share token; permission modes (closed by default, or open) control which accounts may access a private share. Reserved shares persist. |
| **Microsoft Dev Tunnels / VS Code** | `devtunnel` CLI, VS Code **Ports** view, `code tunnel` (Remote Tunnels), Visual Studio, Codespaces. | Private to the creating account by default; can be opened to anonymous users, an Entra tenant, or a GitHub organization. `code tunnel` gives remote editor and terminal access to the whole machine, not one port. Unused tunnels are deleted after 30 days of inactivity by default. |
| **localtunnel-style tools** | `lt`/`localtunnel` (npm), and similar free relays. | Typically no account and no authentication on the published URL; the relay operator sees the traffic. Treat as public and short-lived only. |
| **SSH reverse tunnel** | `ssh -R` or `autossh` sessions to a VPS or jump host; `RemoteForward` in SSH client config; a systemd unit or cron job keeping it alive. | OpenSSH binds remote forwards to loopback by default (`GatewayPorts no`); with `GatewayPorts yes` or `clientspecified`, the forwarded port can be public on the remote server. Exposure depends on the remote server's firewall too. |
| **Agent in a container or NAS app** | Official or community images for any of the above; NAS app-store packages. | Credentials usually sit in environment variables or compose files, readable by anyone who can inspect the container. Host networking lets the agent reach the whole LAN. |

## Detection

Hints for recognizing tunnel agents during an inventory (used by the `full-assessment` skill). These tools
make outbound connections only, so a network port scan rarely finds them; look on hosts and in egress
logs. Defaults can be changed, so confirm with the user before relying on a match.

- **Processes, services, and containers on hosts:** `ngrok`, `frpc`, `frps`, `tailscaled`, `headscale`,
  `zerotier-one`, `netbird`, `newt` (Pangolin connector), `pangolin`/`gerbil` (Pangolin server), `zrok` or
  `zrok2`, `devtunnel`, `code tunnel` / `code-tunnel`, `lt`/`localtunnel`, and long-running `ssh -R` or
  `autossh`. Check systemd units, launchd jobs, Windows services, scheduled tasks, cron, and container
  images, not just running processes. Renamed binaries are common in intrusions; compare hashes and
  command lines, not only names.
- **Local admin and metrics ports:** the ngrok agent's web inspection interface listens on
  `localhost:4040` by default (with a `/status` page). frp examples use port 7000 for `frps` client
  connections, 7500 for the `frps` dashboard, and 7400 for the `frpc` admin UI; these are project example
  values rather than fixed defaults, and the dashboard is off until configured. A frp dashboard or Pangolin
  login page answering on a public address is a strong match.
- **Mesh VPN interfaces:** a `tailscale0`/`utun` interface, a ZeroTier `zt*` interface, or a `wt0`
  NetBird interface, with addresses from the provider's overlay range. Tailscale and ZeroTier use
  vendor-documented UDP ports (41641 and 9993 respectively) for direct peer connections; verify in current
  docs.
- **Egress, DNS, and proxy logs:** queries and connections to tunnel providers, for example ngrok domains
  (`ngrok.com`, `ngrok-free.app`, `ngrok.io` and related agent-connect hostnames), Tailscale control and
  DERP relay hostnames under `tailscale.com`, Dev Tunnels hostnames (`*.devtunnels.ms`,
  `*.rel.tunnels.api.visualstudio.com`, `global.rel.tunnels.api.visualstudio.com`), localtunnel
  (`localtunnel.me`, `loca.lt`), and zrok hosted-service hostnames. Long-lived outbound TLS or SSH sessions
  from servers to a VPS address are typical of frp, Pangolin, and `ssh -R`. Verify current hostname lists
  in vendor firewall documentation before writing block rules.
- **Public footprint:** certificate transparency entries for `*.ts.net` names (Tailscale HTTPS), the
  user's domains pointed at a frp or Pangolin server, and published URLs found in docs, chat, or webhooks.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

Prefer the providers' admin consoles (the user shares screenshots or reads values out), each tool's own
status commands, and user-run checks. For APIs (ngrok API, Tailscale API, Pangolin API), ask the user for
a dedicated, read-only, short-lived credential where the provider supports one, and to revoke it when the
assessment ends. Run the host commands on every host in scope, not only servers.

Candidate read-only commands, **not yet verified** on every version and platform unless marked. Check
each exists first, and redact tokens from any output before showing it.

```sh
# Host inventory (Linux; adapt for macOS launchctl and Windows Get-Service/Get-ScheduledTask)
PAT='ngrok|frp[cs]|tailscaled|zerotier|netbird|newt|zrok|devtunnel|code[ -]tunnel|localtunnel|autossh|ssh .*-R'
ps axo pid,user,lstart,args | grep -Ei "$PAT" | grep -v grep   # REDACT tokens in the arguments
systemctl list-unit-files --type=service | grep -Ei 'ngrok|frp|tailscale|zerotier|netbird|newt|zrok|tunnel'
docker ps --format '{{.Names}}  {{.Image}}  {{.Status}}'  # look for tunnel images; don't print env vars
ss -tnp state established                     # long-lived outbound sessions and their processes
ss -tlnp                                      # local admin/inspection ports (4040, frp admin, metrics)
crontab -l; ls /etc/cron.d                    # keep-alive jobs for ssh -R, autossh, or agents

# ngrok
ngrok version                                 # installed agent version
ngrok config check                            # vendor-documented: validates config, prints its path
curl -s http://127.0.0.1:4040/api/tunnels     # local agent API: endpoints and public URLs (not yet verified)

# Tailscale
tailscale version
tailscale status                              # peers, exit node in use, offline nodes
tailscale serve status                        # vendor-documented: what Serve publishes on this node
tailscale funnel status                       # what is public through Funnel (not yet verified)

# Others
devtunnel list                                # Dev Tunnels owned by the signed-in account
devtunnel show <tunnel-id>                    # ports and access control entries (not yet verified)
code tunnel status                            # VS Code Remote Tunnels on this machine (not yet verified)
zerotier-cli listnetworks                     # joined ZeroTier networks
netbird status                                # NetBird peers and routes
frps --version; frpc --version                # frp versions (not yet verified flag spelling)
```

For SSH reverse tunnels, on the remote server: `ss -tlnp` shows `sshd` listeners for forwarded ports, and
`sshd -T | grep -Ei 'gatewayports|allowtcpforwarding|permitlisten'` shows the effective settings (needs
root; not yet verified on every OpenSSH build).

**Never do these during Discover:**

- Print, paste, upload, or log an authtoken, API key, auth key, access token, frp token, OIDC client
  secret, Newt or zrok credential, or SSH private key. Don't `cat` `ngrok.yml`, `frpc.toml`/`frps.toml`,
  Tailscale state files (`tailscaled.state` holds the node key), Headscale's database or private keys,
  Pangolin or Newt config, zrok environment files, or compose files without redacting secret fields
  first. Redact `--authtoken`, `--token`, `NGROK_AUTHTOKEN`, `TS_AUTHKEY`, and similar values in `ps`
  output, unit files, and container definitions. Don't run `devtunnel token` or `ngrok config
  add-authtoken`.
- Start, stop, restart, install, or uninstall a tunnel or agent (`ngrok http`, `ngrok service ...`,
  `tailscale up/down/set`, `tailscale serve`/`funnel` with any target or `reset`, `devtunnel host`,
  `code tunnel`, `zrok share`, `lt`, a new `ssh -R`). Killing a suspicious process destroys evidence;
  switch to Respond instead.
- Change ACLs, grants, node attributes, route or exit-node approvals, key expiry, device approval, Dev
  Tunnels access entries, Pangolin resource authentication, or frp server settings.
- Visit published URLs while logged in, with credentials, or with tokens or bypass headers
  (`X-Tunnel-Authorization`, `ngrok-skip-browser-warning`). An unauthenticated request to check whether a
  login is in front of a service needs the user's approval and must target only the user's own endpoints.
- Guess passwords, PINs, or passcodes, test default credentials on a frp dashboard or Pangolin server, or
  run exploit scripts against anything published.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Agent inventory on every host

- Build a table: host (or container, VM, NAS app), tool, version, how it starts (service, launchd job,
  scheduled task, cron, container restart policy, terminal session), which local account runs it, and
  who installed it and why. Include developer laptops and admin workstations, not only servers.
- Agents nobody recognizes, renamed or unsigned binaries, binaries in temporary or user-writable
  directories, and agents installed outside the package manager or official image. Any of these is a
  potential P0 (see Respond).
- Agents still running for a finished purpose: a demo, a webhook test, a contractor's support session,
  a `devtunnel host` or VS Code forwarded port left open, an `ssh -R` kept alive by `autossh`.
- What each agent's host can reach. An agent on a flat LAN, or in a container with host networking, can
  publish anything on the network, not just the intended service.
- Whether the same tool is installed on several hosts with the same credential.

#### B. Published endpoints (what is reachable from where)

- For every agent, list every endpoint it publishes: URL or hostname, protocol (HTTP, TCP, TLS, UDP),
  the local service and port behind it, and the audience (internet, tailnet, a named account, an
  organization or tenant, anyone with a link). Use the tool's own status output and the provider's
  dashboard (ngrok Endpoints and Agents, Tailscale Machines and Funnel status, Dev Tunnels list, Pangolin
  resources, zrok overview, frp dashboard proxy list), and reconcile them; a dashboard endpoint with no
  known agent, or an agent with no dashboard entry, needs explaining.
- **Tailscale:** for each node, which ports Serve shares with the tailnet and which Funnel makes public.
  Whether the `funnel` node attribute applies to all members (`autogroup:member`, the CLI's default when
  it adds the attribute) or only to the nodes or users that need it.
- **Raw TCP and UDP endpoints** (ngrok TCP, frp `tcp`/`udp` proxies, Funnel TCP forwarding, `ssh -R` with
  `GatewayPorts`): these publish SSH, RDP, databases, or admin protocols directly. Flag each one.
- Admin interfaces, hypervisors, NAS and router management, home-automation dashboards, cameras, remote
  desktops, and anything without strong built-in authentication published at all.
- Names that reveal the service or the owner, and names that appear in certificate transparency logs or
  public places. Remember that a fixed free-tier domain or a random URL is still findable.
- Leftover port forwards on the router for services that are also tunneled; the tunnel doesn't remove the
  older exposure.

#### C. Authentication in front of published services

- **ngrok:** each public endpoint's Traffic Policy. Is there an authentication action (OAuth, OpenID
  Connect, JWT validation, or basic auth as a minimum) or an IP restriction, and does the OAuth or OIDC
  rule restrict *which* identities (specific emails or a domain you control), rather than accepting any
  Google or GitHub account? Endpoints still configured with deprecated agent flags should be migrated.
  Webhook endpoints: is the provider's signature verified (Traffic Policy or the app)?
- **Tailscale Funnel:** no Tailscale login is in front of a Funnel endpoint. The application must
  authenticate users itself. **Serve:** reachable by any tailnet member the policy allows to reach the
  node; check the policy actually limits that, and whether the app trusts Tailscale identity headers only
  from Serve.
- **Pangolin:** for each public resource, whether Platform SSO is still on or was replaced by something
  weaker (a short PIN, a shared passcode, a share link with no expiry, or header auth), and whether access
  rules allow-list paths or IP ranges that skip authentication. Which identity providers and users or roles
  may access each resource.
- **Dev Tunnels:** access control entries per tunnel and port: anonymous, tenant-wide, or GitHub
  organization-wide access, and their expiry. Outstanding access tokens (client, host, manage-ports,
  management) and who received them.
- **zrok:** public versus private shares; for private shares, permission mode (closed or open) and access
  grants; who holds share tokens.
- **frp:** HTTP Basic Auth (`httpUser`/`httpPassword`) on `http` proxies is optional and weak on its own;
  `stcp`/`xtcp` proxies need a `secretKey` shared by the visitor. Check what each proxy relies on.
- **localtunnel-style relays and `ssh -R`:** usually nothing in front; the published service must
  authenticate on its own.
- In every case: does the backend service have its own authentication too, so one misconfiguration in the
  tunnel isn't the only barrier? Interstitial or anti-phishing pages (ngrok free tier, Dev Tunnels) are
  not authentication.

#### D. Agent credentials and secrets

- **ngrok:** where the authtoken and any API key live (`ngrok.yml`, `NGROK_AUTHTOKEN`, `NGROK_API_KEY`,
  compose files, CI secrets). Whether each agent has its own credential rather than the account's single
  token, and whether credentials are restricted to the endpoints they need (verify current ngrok
  credential ACL features). File permissions on the config file.
- **Tailscale:** auth keys in scripts, compose files, or cloud-init (`TS_AUTHKEY`); whether they are
  reusable, pre-approved, or tagged, and their expiry. OAuth clients and API access tokens, their scopes,
  and expiry. Permissions on the node state directory.
- **frp:** `auth.token` strength and storage (it can be read from a file with `auth.tokenSource`), whether
  every client shares one token, and OIDC client secrets.
- **Pangolin:** Newt site ID and secret storage, Pangolin admin and API keys, and the server's own
  secrets.
- **Dev Tunnels / VS Code:** which Microsoft, Entra, or GitHub account owns each tunnel; that account's
  MFA. **zrok:** account token and environment files. **SSH:** the private key used for a persistent
  `ssh -R`, whether it has a passphrase, and whether its `authorized_keys` entry on the remote server is
  restricted (for example `restrict`, `permitlisten`, or a forced command).
- The provider account itself (ngrok, Tailscale, GitHub, Microsoft, zrok hosted service): MFA, SSO,
  members and roles, and the mailbox that can reset it.
- When each credential was last rotated, and whether any appears in a git repository, image layer,
  paste, or shared file.

#### E. Self-hosted tunnel servers (frp, Pangolin, zrok, Headscale)

- **frps:** which ports are open on the public server (bind port, vhost HTTP/HTTPS ports, every port
  `allowPorts` permits). Is `allowPorts` set, so a client can't open arbitrary ports? Is the dashboard
  enabled, bound only to loopback or a management network, with a strong unique password and TLS? Is the
  metrics or pprof endpoint enabled? Is `transport.tls.force` set so only TLS clients connect? Do clients
  verify the server certificate (`trustedCaFile` or system CA)? Is authentication applied to heartbeats
  and new work connections (`auth.additionalScopes`) where the version supports it?
- **Pangolin server:** OS and firewall hardening on the VPS, admin account MFA, which ports are open
  (web, and the WireGuard ports used by Gerbil and Newt), update status of each component, and backups of
  its database.
- **Self-hosted zrok or OpenZiti and Headscale:** the control plane is internet-facing and holds every
  node's or share's authorization. Admin API keys, database protection, TLS, and update status.
- Whether the server can reach back into the home network (a VPS that is also a mesh VPN node or a
  subnet router turns a server compromise into LAN access).
- Hand the host itself to the [linux](../../operating-systems/linux/SKILL.md) skill.

#### F. Mesh VPN access, keys, routes, and exit nodes

- **Access policy:** the tailnet policy (ACLs or grants), ZeroTier flow rules and member authorization,
  or NetBird policies. Flag an allow-all policy (the default Tailscale policy lets every member reach
  every device), rules that give guests or shared users broad access, and `autogroup:internet` granted
  more widely than intended.
- **Device admission:** device approval required or not; Tailnet Lock (Tailscale) where used; ZeroTier
  networks set to public (verify the current behavior in ZeroTier's docs; a public network admits members
  without authorization); unknown, unnamed, or long-offline devices.
- **Key expiry:** Tailscale's default node key expiry is 180 days (configurable from 1 to 180). List
  nodes with key expiry disabled; tagged devices have it disabled by default. Servers may justify it,
  laptops and phones usually don't.
- **Subnet routers:** every advertised route, whether it's approved and by whom (manual or
  `autoApprovers`), and how broad it is. A route for the whole LAN gives every node the policy allows the
  whole LAN. By default Tailscale source-NATs subnet traffic, so LAN devices and their logs see the
  router's address, not the real client.
- **Exit nodes:** which nodes are approved as exit nodes and who may use them. An exit node sends other
  users' internet traffic out through the user's connection, so abuse looks like it came from the user.
  Check whether clients use `--exit-node-allow-lan-access` and whether that matters.
- **Sharing and external users:** nodes shared to other tailnets, invited external users, and Funnel or
  Serve on nodes reachable by them.
- **Self-hosted control (Headscale):** API keys, pre-auth keys (reusable, expiry), and who can run the
  admin CLI.

#### G. Ad-hoc and developer tunnels (Dev Tunnels, VS Code, localtunnel, `ssh -R`)

- **Dev Tunnels:** persistent tunnels (`devtunnel create`) versus temporary ones; anonymous access entries
  and their expiry; tunnels unused for weeks (deleted after 30 days of inactivity by default, but each use
  extends that window).
- **VS Code port forwarding:** ports set to **Public** visibility; forwarded ports left open after a
  session.
- **VS Code Remote Tunnels (`code tunnel`):** installed as a service? Which account signs in? This grants
  a full editor and terminal on the machine to whoever controls that account. On work machines, whether
  the organization allows it at all.
- **localtunnel and similar:** any use on anything other than a disposable test service.
- **SSH reverse tunnels:** every persistent `ssh -R` or `RemoteForward`, what it forwards, the remote
  server's `GatewayPorts`, `AllowTcpForwarding`, and `PermitListen` settings, and whether the remote side
  binds to loopback only. A reverse tunnel from a home server to a shared or third-party VPS gives the VPS
  owner a path in.

#### H. Egress control and unsanctioned tunnels

- Can every host reach tunnel providers? Servers, cameras, IoT, and NAS devices rarely need to. Is there
  an approved list of tunnel tools, and are others blocked or alerted on at the firewall, DNS filter, or
  proxy (see [dns-filtering](../../network/dns-filtering/SKILL.md) and the firewall skills)?
- Review recent DNS and firewall logs for tunnel-provider hostnames and for long-lived outbound sessions
  to VPS addresses, and match each to an inventoried agent.
- On work devices, whether organization policy restricts Dev Tunnels and VS Code tunnels (MITRE
  recommends disabling Dev Tunnels where not needed and restricting to approved Entra tenants).
- Large or steady outbound transfers through tunnel agents (possible exfiltration).

#### I. Logging, monitoring, and updates

- Which logs exist and are retained: ngrok dashboard and agent logs (and whether traffic inspection is
  on, since it records request bodies, including credentials, on the agent host), Tailscale configuration
  audit logs and network flow logs (plan-dependent), frp server logs, Pangolin access logs, Dev Tunnels
  activity, SSH server logs for forwarding. Are they reviewed, and do alerts exist for new endpoints, new
  devices, or policy changes?
- Version of every agent and server against the current release; how each updates (package manager,
  image tag, built-in updater, or never). Check vendor release notes and security advisories (core:
  vulnerability triage); don't rely on a static list.
- Agents or servers on unmaintained projects or forks, or abandoned free relays.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Who and what uses each endpoint:** people, mobile apps, webhooks from third parties (payment, chat,
  smart-home clouds), monitoring, and backups. Webhook senders and non-browser clients often can't
  complete an OAuth login and need a separate, signature-verified endpoint.
- **The user's and agent's own access:** remote administration often runs through the tunnel or mesh VPN
  being changed. Keep a second working path before touching it.
- **Mesh VPN dependants:** devices that reach the LAN only through a subnet router, users relying on an
  exit node, and automation using auth keys.
- **Shared credentials:** rotating an authtoken, frp token, or auth key breaks every agent that uses it.
- **Hosted versus self-hosted:** changes on a self-hosted frp, Pangolin, zrok, or Headscale server affect
  every client at once.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Unknown agent on a host | Switch to Respond; don't kill it before evidence is collected. | Possible compromise; the host may need rebuilding. |
| Forgotten or finished tunnel | Stop and remove the agent and its service, delete the endpoint or reserved name, and revoke its credential. | Anything still using the URL breaks; confirm nobody does first. |
| Admin UI or raw TCP service published | Remove it from the tunnel; reach it over a mesh VPN (Serve, private share, private Dev Tunnel) instead. | Each admin device needs a client. |
| Public endpoint without authentication | Add an identity-checking layer: ngrok Traffic Policy OAuth/OIDC limited to named identities, Pangolin SSO, or an authenticating reverse proxy; keep the app's own login. | Users must log in; webhooks need a separate path. |
| OAuth/OIDC accepting any account | Restrict to specific email addresses or a domain the user controls. | Anyone not listed loses access. |
| Funnel where Serve would do | Switch the port to Serve (tailnet only). Limit the `funnel` node attribute to the nodes that need it. | Non-tailnet users lose access. |
| Weak Pangolin method (PIN, shared passcode, open share link) | Restore Platform SSO or an external IdP; give share links an expiry. | Users must log in. |
| Dev Tunnel anonymous or tenant-wide access | Remove the anonymous entry, or set a short expiry; use private access or access tokens for specific clients. | Clients without the account or token lose access. |
| Agent credentials in compose files or repos | Move to a secret store or file with tight permissions; rotate anything that was exposed. | Agents restart with the new secret. |
| One credential shared by many agents | Issue one credential per agent, scoped where the provider supports it. | More credentials to track; easier revocation. |
| frps without `allowPorts`, with public dashboard, or weak token | Set `allowPorts`, bind the dashboard to loopback with a strong password and TLS, use a long random token or OIDC, force TLS, and configure clients to verify the server certificate. | All `frpc` clients must be updated together. |
| Default allow-all tailnet policy | Write a policy that grants each user or tag only the devices and ports it needs. | Unlisted access stops; test with the policy tests feature first. |
| Key expiry disabled on user devices | Re-enable expiry; keep it disabled only on tagged servers with a reason. | Users re-authenticate periodically. |
| Broad subnet route or open exit node | Narrow routes to the hosts or subnets needed; restrict exit-node use by policy; remove unneeded `autoApprovers`. | Devices outside the narrower routes become unreachable remotely. |
| `ssh -R` with `GatewayPorts yes` | Bind the forward to loopback and front it with an authenticating proxy, or replace with a mesh VPN; restrict the key with `permitlisten` and `restrict`. | Remote clients must connect differently. |
| Servers and IoT can reach tunnel providers | Block tunnel-provider domains on segments that don't need them; alert on new tunnel traffic. | Legitimate agents need explicit exceptions. |
| ngrok traffic inspection on sensitive services | Disable inspection for that endpoint or agent (verify the current setting name), and keep the inspection UI on loopback. | Less debugging detail. |
| Outdated agents or servers | Update through the original installation method; pin container image versions. | Brief interruption. |

Hiding a hostname, relying on a random URL, or leaning on an interstitial warning page is never the fix
for an unauthenticated published service.

Group the plan: immediate containment (unknown agents, unauthenticated admin endpoints, exposed
credentials) → urgent fixes (authentication in front of every public endpoint, frps hardening, broad
routes) → high-priority hardening (mesh policy, key expiry, credential scoping, egress control) →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Tunnel specifics:

- **Before any change:** record the current state: endpoint list, Traffic Policy, tailnet policy file,
  Serve/Funnel status, Pangolin resource settings, frp config (secrets redacted), and Dev Tunnels access
  entries. Back up the tailnet policy file and frp configs before editing.
- **Use each tool's supported interface:** the ngrok dashboard, API, or agent config; the Tailscale admin
  console, policy file, or GitOps workflow (if the policy is managed in git, change it there or the next
  sync reverts it); `devtunnel access` commands; the Pangolin dashboard; frp config files followed by a
  service restart.
- **Keep a way back in.** Don't remove the tunnel, route, or policy rule that the user's own remote access
  depends on without a tested second path. Tailscale policy changes take effect for the whole tailnet
  within seconds; use the policy file's tests to confirm access before saving.
- **Adding authentication:** add the new authentication (Traffic Policy action, Pangolin SSO, OAuth
  restriction) and test it with a real login and with a non-allowed identity before removing the old
  arrangement. Move webhooks to their own endpoint with signature verification first.
- **Removing a tunnel:** stop the agent through its service manager, disable the service so it doesn't
  return at boot, then delete the endpoint, reserved name, or share in the provider dashboard, then revoke
  the credential. Confirm in the dashboard that no agent session remains.
- **Credential rotation:** create the new credential, update each agent (the user pastes it into the
  secret store or config; never display it), confirm each reconnects, then revoke the old one. For frp,
  change the token on the server and every client in one planned window.
- **Mesh VPN changes:** narrow subnet routes by changing what the router advertises and what is approved;
  re-enable key expiry per device; remove stale devices after confirming with their owner.
- **frps changes:** apply on a test client first where possible; enabling `transport.tls.force` or
  certificate verification breaks clients that aren't ready.

After each change, follow the core "after a change" steps: re-read the endpoint list and status output,
confirm an unauthenticated request to each changed endpoint is denied (from the user's own vantage point,
with approval), confirm legitimate users and webhooks still work, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Killing or uninstalling an unknown agent before evidence is preserved (switch to Respond).
- Deleting a tailnet, ZeroTier network, ngrok account, Pangolin instance, or Headscale database.
- Removing the last admin, rotating the only admin credential, or enabling Tailnet Lock as an automated
  step; the user does these with recovery keys in hand.
- Changing the access policy, routes, or tunnel that the user's only remote path depends on.
- Starting a new public tunnel "to test" exposure.
- Any credential testing, default-password checks, or exploit attempts against published services or
  tunnel servers.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the tunnel-specific
steps in [incident-response.md](incident-response.md). P0 indicators include a tunnel agent nobody
installed, an endpoint or agent session in a provider dashboard that matches no known host, a new mesh
device, route, or exit node nobody approved, a policy change nobody made, an exposed authtoken, auth key,
or frp token, and outbound tunnel traffic from a host that has no inventoried agent.

---

## Worked example (invented)

### TUN-001: Forgotten ngrok agent publishes a home-automation dashboard without authentication

**Confidence:** Confirmed
**Priority:** P1. The dashboard can control locks and cameras and is reachable by anyone who learns the
URL; its own login is the only barrier, and the agent's traffic inspection records that login.
**State:** Open
**Component:** ngrok agent installed as a system service on `192.0.2.40`, publishing
`https://<assigned-name>.ngrok-free.app` to the local dashboard on port 8123.
**Evidence:** Observed 2026-03-10: `ps` shows `ngrok start --all` running as a service since 2025-11-02
(token argument redacted). `ngrok config check` reports a v3 config; the endpoint section (secrets
redacted) defines one HTTP endpoint with no `traffic_policy`. The ngrok dashboard's Endpoints page lists
the same URL, online. The user says it was set up for a one-off integration test. With approval, a
request from `198.51.100.7` returned the ngrok interstitial page and then the dashboard login page with no
OAuth redirect. The local inspection interface at `localhost:4040` shows recent requests, including a
login form submission.
**Expected secure state:** no tunnel left running after its purpose ends; any public endpoint that must
stay has an identity-checking layer (Traffic Policy OAuth or OIDC limited to named identities) in front of
the application's own login (ngrok Traffic Policy documentation).
**Exposure and prerequisites:** anyone on the internet with the URL. Free-plan domains are fixed per
account, so the URL hasn't changed since November and may appear in chat, browser history, or logs.
**Dependencies / blast radius:** the user says nothing uses the URL any more; the dashboard's mobile app
connects through the vendor's own remote-access service, not this tunnel.
**Recommended remediation:** stop and uninstall the ngrok service, delete the endpoint in the dashboard,
and revoke the authtoken (it sat in a readable config file for months). Rotate the dashboard password,
since the inspection log captured logins. Block ngrok domains on the server VLAN unless an approved use
returns.
**Operation class:** C2 (stops a running service and revokes a credential).
**Approval required:** Yes.
**Verification:** no `ngrok` process or service on the host; the dashboard shows no online agent or
endpoint; the URL returns ngrok's endpoint-offline error; the old authtoken no longer appears in the
dashboard; DNS logs show no further ngrok lookups from the host.
**Rollback:** reinstall the agent with a new authtoken (not recommended unless a need returns, and then
only with Traffic Policy authentication).

---

## Version history

- **1.0** (2026-10-30): Initial version.
