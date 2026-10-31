# DNS Filtering Servers (AdGuard Home, Pi-hole, Technitium DNS Server): References

Always prefer current vendor documentation. Both products change settings, keys, and menus between
releases; re-verify links and contents when updating this skill.

Last verified: 2026-10-31 (Technitium); 2026-10-30 (AdGuard Home, Pi-hole)

## Vendor (authoritative)

### AdGuard Home

- Security advisories (GitHub): https://github.com/AdguardTeam/AdGuardHome/security/advisories
- Releases and release notes: https://github.com/AdguardTeam/AdGuardHome/releases
- Changelog: https://github.com/AdguardTeam/AdGuardHome/blob/master/CHANGELOG.md
- Getting started (ports, service commands, updates, Docker/Snap update behavior):
  https://adguard-dns.io/kb/adguard-home/getting-started/
- Running AdGuard Home securely (bind addresses, allowlist mode, rate limiting, file ownership, GPG
  verification): https://adguard-dns.io/kb/adguard-home/running-securely/
- FAQ (reverse proxies, `trusted_proxies`, listen addresses): https://adguard-dns.io/kb/adguard-home/faq/
- DNS filtering rule syntax (hosts-style rules, `$dnsrewrite`, `$client`, `$ctag`):
  https://adguard-dns.io/kb/general/dns-filtering-syntax/
- Configuration file reference (marked outdated by the vendor; check the Knowledge Base for current
  keys): https://github.com/AdguardTeam/AdGuardHome/wiki/Configuration
- Docker (ports, volumes, update procedure): https://github.com/AdguardTeam/AdGuardHome/wiki/Docker
- HTTP API (OpenAPI spec, Basic authentication):
  https://github.com/AdguardTeam/AdGuardHome/tree/master/openapi

### Pi-hole

- Security advisories (GitHub, per component):
  https://github.com/pi-hole/pi-hole/security/advisories,
  https://github.com/pi-hole/FTL/security/advisories,
  https://github.com/pi-hole/web/security/advisories,
  https://github.com/pi-hole/docker-pi-hole/security/advisories
- Release announcements: https://pi-hole.net/blog/ and https://discourse.pi-hole.net/
- Introducing Pi-hole v6 (embedded web server and REST API, native HTTPS, one-way upgrade):
  https://pi-hole.net/blog/2025/02/18/introducing-pi-hole-v6/
- Configuration reference (`pihole.toml` keys and defaults): https://docs.pi-hole.net/ftldns/configfile/
- API authentication (sessions, app passwords, TOTP, rate limits): https://docs.pi-hole.net/api/auth/
- Listening modes and open-resolver warning: https://docs.pi-hole.net/ftldns/interfaces/
- `pihole` command reference: https://docs.pi-hole.net/main/pihole-command/
- Updating: https://docs.pi-hole.net/main/update/
- Docker (ports, `FTLCONF_` variables, upgrades): https://docs.pi-hole.net/docker/
- Unbound as a local recursive resolver: https://docs.pi-hole.net/guides/dns/unbound/
- cloudflared (DoH) guide, including the proxy-dns deprecation warning:
  https://docs.pi-hole.net/guides/dns/cloudflared/

### Technitium DNS Server

- Project home and feature list: https://technitium.com/dns/
- Source, releases, and security policy: https://github.com/TechnitiumSoftware/DnsServer
- Changelog (security fixes per release): https://github.com/TechnitiumSoftware/DnsServer/blob/master/CHANGELOG.md
- HTTP API documentation (login, TOTP, API tokens, sessions, settings fields and initial values,
  users, groups, permissions, cluster endpoints):
  https://github.com/TechnitiumSoftware/DnsServer/blob/master/APIDOCS.md
- Docker environment variables (read only on first start; recursion, web service, SSO, LDAP):
  https://github.com/TechnitiumSoftware/DnsServer/blob/master/DockerEnvironmentVariables.md
- Vendor Docker compose file (default published ports):
  https://github.com/TechnitiumSoftware/DnsServer/blob/master/docker-compose.yml
- Blog, release announcements (v15: OpenID Connect SSO, non-root service, .NET 10):
  https://blog.technitium.com/2026/04/technitium-dns-server-v15-released.html
- Understanding clustering and how to configure it (what replicates, TLS and certificate advice):
  https://blog.technitium.com/2025/11/understanding-clustering-and-how-to.html

### Client behavior

- Mozilla, canary domain `use-application-dns.net` (disables Firefox's default DoH only):
  https://support.mozilla.org/en-US/kb/canary-domain-use-application-dnsnet

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- None relied on for this version. Community blocklist catalogs and sync tools are third-party
  integrations: assess them under the core tool-use contract before trusting them.
