# Tunnels: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only tunnel-specific steps. For Cloudflare Tunnel (`cloudflared`), use the
[cloudflare](../cloudflare/incident-response.md) Respond steps instead.

Tunnel tools are a common attacker choice for persistence, remote access, and exfiltration because they
need no inbound firewall change and their traffic goes to reputable providers. CISA has reported actors
implanting ngrok on several hosts to keep access and proxy RDP (AA22-320A), and Volt Typhoon implanting
FRP clients for command and control (AA24-038A); MITRE ATT&CK lists ngrok as software used by several
groups and tracks IDE tunneling (VS Code and Dev Tunnels) as a technique. Treat an unexplained tunnel as a
compromise of the host it runs on until shown otherwise.

## Triage and containment

- **Indicators on hosts:** a tunnel agent (`ngrok`, `frpc`, `zrok`, `devtunnel`, `code tunnel`,
  `tailscaled`, `zerotier-one`, `netbird`, `newt`, `lt`, `autossh`, or `ssh -R`) nobody installed;
  renamed or packed binaries (CISA noted UPX-packed FRP clients); agents started by scheduled tasks, cron,
  `Run` keys, new services, or launched from scripting hosts; config files in temporary or user-profile
  directories; a VS Code tunnel signed in with an account the user doesn't own.
- **Indicators in provider consoles:** agent sessions or endpoints in ngrok from unknown IPs or hosts; new
  Tailscale devices, approved routes or exit nodes, policy changes, auth keys, or Funnel enablement nobody
  made; Pangolin resources or sites nobody created, or authentication removed from a resource; unknown
  Dev Tunnels or anonymous access entries; frp dashboard proxies that no known client defines.
- **Indicators in the network:** DNS or firewall log entries for tunnel providers from hosts with no
  inventoried agent; long-lived outbound sessions to unfamiliar VPS addresses; sustained uploads through
  a tunnel.
- **Contain at the provider and the network, not by killing the process first.** Record the process,
  its command line (redact tokens), parent, open connections, and binary hash before stopping anything
  (core: preserve evidence). Then, with approval:
  - Disable or delete the endpoint and revoke the credential at the provider (ngrok authtoken or agent
    credential, Tailscale node or auth key, Dev Tunnel or its access entries, zrok share, Pangolin site).
  - Block the provider's hostnames for the affected host at the firewall or DNS filter, or isolate the host
    from the network per the core playbook.
  - For a mesh VPN, remove or expire the unknown device and revoke route and exit-node approvals it holds.
  - For a self-hosted frps or Pangolin server, stop accepting new clients by changing the token or site
    credentials, after recording the current client and proxy list.
- If an attacker-owned account runs the tunnel (common with ngrok and VS Code tunnels), you can't revoke
  its credential; network blocking and host isolation are the containment. Report abuse to the provider.

## Evidence to preserve (tunnel-specific)

- **Host:** process list with command lines and start times (redacted), parent process chain, binary
  path, hash, signature, and file timestamps; service, launchd, scheduled-task, cron, and container
  definitions; agent config files copied to evidence storage with secret fields redacted in any working
  copy; agent logs; shell history; `ss`/`netstat` output showing the agent's connections.
- **ngrok:** dashboard agent sessions, endpoints, and their Traffic Policy; the local inspection
  interface history at `localhost:4040` if the agent is still running (it is held in the agent, so
  capture it before the agent stops; it may contain credentials, so store it as sensitive evidence).
- **Tailscale and other mesh VPNs:** device list with creation and last-seen times, the tailnet policy
  file and its change history, configuration audit logs and network flow logs where the plan has them,
  approved routes and exit nodes, auth keys and their creators, and Serve/Funnel status on affected
  nodes.
- **frp:** `frps` logs, dashboard proxy and client lists, and server config; `frpc` config from each client.
- **Pangolin:** resources, sites, users and roles, authentication settings per resource, and access logs.
- **Dev Tunnels / VS Code:** `devtunnel list` and `show` output for the owning account, access entries,
  and the account's sign-in logs (Microsoft, Entra, or GitHub).
- **SSH reverse tunnels:** the remote server's `sshd` logs, its listening sockets, and the
  `authorized_keys` entry used.
- **Network:** DNS, firewall, and proxy logs for the provider hostnames over the suspected window and well
  before it.

## Scope checks specific to tunnels

- **Everything the agent's host could reach.** A tunnel is a doorway into whatever network the host sits
  on; check the services behind every published endpoint and every LAN host reachable from it.
- **Everything published while the attacker was active:** each endpoint's backend logs and logins.
- **Credentials seen by the tunnel:** inspection logs, basic-auth headers, and any login that passed
  through a published endpoint; rotate those application credentials.
- **Other hosts with the same credential or config:** a stolen authtoken, frp token, or auth key may have
  been reused elsewhere.
- **Mesh-wide reach:** if a mesh device was compromised, every device and subnet the policy let it reach.
  If an exit node was abused, traffic may have left through the user's connection; preserve logs in case
  of third-party complaints.
- **Provider accounts:** the ngrok, Tailscale, Microsoft, GitHub, or zrok account and its mailbox.

## Eradication and recovery

- Rebuild any host that ran an attacker-installed tunnel from trusted media (core playbook); removing the
  agent alone doesn't remove whatever installed it.
- Rotate every tunnel credential that existed on affected hosts or servers: ngrok authtokens and API keys,
  Tailscale auth keys, OAuth clients, and the affected nodes' keys (re-authenticate the node), frp tokens
  and OIDC secrets, Newt and Pangolin keys, zrok tokens, Dev Tunnels (delete and recreate), and SSH keys
  used for reverse tunnels.
- Restore the tailnet policy, Pangolin resource authentication, and Traffic Policies from records taken
  **before** the earliest plausible compromise; diff against the current state.
- Reinstall legitimate agents from official packages or images at current versions.
- Before reconnecting: every legitimate endpoint has authentication in front of it, unapproved devices are
  gone, routes and exit nodes are narrowed, egress to tunnel providers is blocked for hosts that don't
  need it, and alerts exist for new agents, endpoints, and devices.

## Quick checklist tailored for tunnels

Start with the core quick checklist, plus:

- [ ] Record the agent's process, command line (redacted), parent, connections, and hash before stopping it.
- [ ] Capture provider-side evidence: endpoints, agent sessions, devices, policy history, audit logs.
- [ ] Revoke the tunnel credential or endpoint at the provider; block provider hostnames for the host.
- [ ] Remove unknown mesh devices, routes, and exit-node approvals; restore the access policy.
- [ ] Rotate every tunnel credential and any application login that passed through the tunnel.
- [ ] Rebuild hosts that ran an attacker-installed agent; check every system the tunnel could reach.
