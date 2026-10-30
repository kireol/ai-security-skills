# Cloudflare: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only Cloudflare-specific steps.

A compromised Cloudflare account can redirect a domain's DNS, publish internal services through a tunnel,
remove Access protection, and read or change traffic through Workers. A leaked tunnel token lets someone
run connectors for that tunnel and receive its traffic. Unlike a host compromise, most of this happens in
Cloudflare's control plane, so the account and its credentials are what you contain first.

## Triage and containment

- **Indicators that point at the account:** unknown members or pending invitations, API tokens nobody
  created, a rolled Global API Key, logins from unknown locations in the audit log, changed account email,
  2FA removed from a member, new zones, DNS records nobody made (especially changed MX, NS-like
  delegations, or A records pointing somewhere new), new Workers or routes, Access policies widened to
  Everyone or changed to Bypass, new identity providers, new service tokens, or SSL/TLS mode lowered.
- **Indicators that point at a tunnel:** a connector in `cloudflared tunnel info` or the dashboard that
  doesn't match any known host, new public hostnames or private routes, a tunnel nobody created, or a
  token found in a public repository, paste, image layer, or shared compose file.
- **Indicators that point at a host:** an unexpected `cloudflared` process or container, especially a
  quick tunnel (`trycloudflare.com` hostname) or a token-run tunnel that isn't in the user's account.
  Attackers use `cloudflared` to expose a compromised machine or create a covert channel; treat that host
  as compromised under the core playbook.
- **Account containment (user does these, with approval for anything disruptive):** from a clean device,
  change the Cloudflare password, confirm 2FA on the account email's mailbox, re-enroll 2FA, remove
  unknown members, revoke unknown API tokens, and roll the Global API Key if it may be exposed (inventory
  integrations first, but don't let that delay a confirmed compromise).
- **Tunnel containment:** refresh the tunnel token, then delete the tunnel's existing connections through
  the documented API call so attacker-run connectors drop; reinstall known connectors with the new token.
  If a public hostname is exposing something sensitive, remove that hostname or put an Access application
  with a narrow Allow policy in front of it immediately.
- **Don't delete tunnels, zones, records, or tokens before recording them.** Deleting removes evidence of
  what was there. Disable, narrow, or revoke first; delete later.

## Evidence to preserve (Cloudflare-specific)

Collect from a clean admin device, before changing anything where possible:

- **Audit logs** for the account, covering the suspected window and well before it: export through the
  dashboard (CSV) or the audit logs API. Cloudflare documents 18-month retention; if Logpush is configured,
  secure the external copy too.
- Members and roles, pending invitations, and API token metadata (names, permissions, resources, IP
  filters, creation and last-used dates). Never export token values.
- **DNS:** an export of every zone's records (BIND format), plus DNSSEC status and the registrar's
  nameserver and DS records.
- **Tunnels:** list of tunnels (including deleted ones: `cloudflared tunnel list -d`), each tunnel's
  connectors (connector IDs, origin addresses as Cloudflare reports them, versions, connect times), public
  hostnames, ingress configuration, and private routes. Screenshot connectors before deleting connections.
- **Access:** applications, policies, identity providers, service tokens (metadata), and Access
  authentication logs for affected applications.
- Zone settings that may have been changed: SSL/TLS mode, WAF and custom rules, Page/Configuration/
  Transform Rules, Workers and their routes (save the Worker code), redirects, and notifications.
- **On hosts running `cloudflared`:** process list and service definitions (redact tokens), container
  definitions and image digests, `cloudflared` version, `config.yml` (credential fields redacted), file
  timestamps of credentials files, and `cloudflared` logs.
- Origin web server and application logs for the same window, since traffic from Cloudflare (or from
  someone who bypassed it) lands there.

## Scope checks specific to Cloudflare

- **Every service published through the account:** each tunnel hostname and proxied site may have been
  reached while Access was weakened. Check each origin's own logs and logins.
- **Mail and identity:** if MX, SPF, or DKIM records were changed, mail may have been intercepted;
  password resets for other services sent to the domain may have been captured. If DNS was redirected,
  certificates may have been issued for the domain by someone else; check certificate transparency logs.
- **Every host with a connector:** a compromised account can't read files on those hosts, but a
  compromised host gives up the token. Work out which came first.
- **Every integration holding a Cloudflare credential:** DDNS clients, ACME clients, CI/CD, Terraform
  state, and hosting panels. A leaked token from any of these may be the entry point.
- **Private networks reachable through WARP routes:** treat them like a VPN compromise.
- **The registrar account** for each domain, and the mailbox for the Cloudflare account email.

## Eradication and recovery

- Restore DNS records, Access policies, SSL/TLS mode, rules, and Workers from records taken **before** the
  earliest plausible compromise (exports, Terraform state history, screenshots), and diff against the
  current state to understand what the attacker changed. Don't restore attacker changes.
- **Rotate every Cloudflare credential:** account password, 2FA factors and backup codes, every API token,
  the Global API Key, every tunnel token (Refresh token, then reinstall connectors), locally managed
  tunnel credentials (recreate the tunnel if the credentials file was exposed; verify the current
  procedure), `cert.pem` on hosts, service tokens (rotate or delete and recreate), and IdP client secrets
  configured in Access.
- Rebuild any host found running an unknown `cloudflared` from a trusted source (core playbook). Reinstall
  `cloudflared` on known hosts from the official package or image.
- Rotate origin IP addresses if the attacker could have learned them (DNS-only records, logs, or
  configuration they could read).
- Before calling it done: 2FA enforced, members and tokens reviewed, every public hostname has an Access
  application, no Bypass or Everyone policies on admin apps, SSL/TLS Full (strict), origins locked down,
  notifications going to a monitored address, and audit-log review scheduled.

## Quick checklist tailored for Cloudflare

Start with the core quick checklist, plus:

- [ ] From a clean device: change the Cloudflare password, check the account email's mailbox security,
      and confirm 2FA.
- [ ] Export the audit log, DNS records, tunnel connectors, and Access policies before deleting anything.
- [ ] Remove unknown members; revoke unknown API tokens; roll the Global API Key if it may be exposed.
- [ ] Refresh tunnel tokens, delete existing tunnel connections, and reinstall known connectors.
- [ ] Put Access in front of (or remove) any public hostname exposing a sensitive service.
- [ ] Check the registrar: nameservers, DS records, and registrar account access.
