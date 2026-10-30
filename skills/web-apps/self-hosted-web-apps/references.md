# Self-Hosted Web Apps and Dashboards: References

This skill covers many projects, and each changes quickly. Always prefer the project's own current
documentation, release notes, and security advisories for the installed version. The links below cover
the apps named in the skill; for any other app, find the equivalent pages (README, documentation,
releases, `SECURITY.md`, GitHub Security Advisories) before assessing it.

Last verified: 2026-10-30

## Vendor (authoritative)

### Dashboards and start pages

- Homepage installation and security notes (authentication, rate limiting, allowed hosts):
  https://gethomepage.dev/installation/
- Homepage Docker installation (socket mounting, PUID/PGID): https://gethomepage.dev/installation/docker/
- Homepage security advisories: https://github.com/gethomepage/homepage/security
- Heimdall (repository, releases): https://github.com/linuxserver/Heimdall
- Homarr documentation: https://homarr.dev/docs/
- Homarr security advisories: https://github.com/homarr-labs/homarr/security

### Network scanners

- NetAlertX (repository, Docker requirements, security advice): https://github.com/netalertx/NetAlertX
- NetAlertX security advisories: https://github.com/netalertx/NetAlertX/security
- WatchYourLAN (repository; no built-in authentication, host networking required):
  https://github.com/aceberg/WatchYourLAN

### Monitoring

- Glances quickstart (web mode, `--password`, `xmlrpc_allowed_hosts`):
  https://glances.readthedocs.io/en/latest/quickstart.html
- Glances security advisories: https://github.com/nicolargo/glances/security
- Uptime Kuma security policy (supported image tags, advisories):
  https://github.com/louislam/uptime-kuma/security
- Grafana security configuration (anonymous access implications):
  https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/
- Grafana sign-in (default login and forced change):
  https://grafana.com/docs/grafana/latest/setup-grafana/sign-in-to-grafana/
- Grafana security advisories: https://grafana.com/security/security-advisories/

### Containers and access layers

- Docker Engine security (daemon attack surface): https://docs.docker.com/engine/security/
- Docker packet filtering and firewalls (published ports and host firewall rules):
  https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Authelia: https://www.authelia.com/
- Authentik: https://goauthentik.io/docs/
- oauth2-proxy: https://oauth2-proxy.github.io/oauth2-proxy/
- Cloudflare Access (Zero Trust applications): https://developers.cloudflare.com/cloudflare-one/applications/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Tecnativa Docker Socket Proxy: https://github.com/Tecnativa/docker-socket-proxy. A filtering proxy for
  the Docker API, named in Traefik's documentation. It limits which API endpoints a container can call;
  configure it to allow only what the app needs, and remember it's still access to the Docker API.
- GitHub repository metadata (last commit, last release, archived flag, open security issues): the
  practical signal for project maintenance status. Read it as evidence, not as a guarantee either way.
