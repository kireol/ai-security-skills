# Self-Hosted Web Apps and Dashboards: References

This skill covers many projects, and each changes quickly. Always prefer the project's own current
documentation, release notes, and security advisories for the installed version. The links below cover
the apps named in the skill; for any other app, find the equivalent pages (README, documentation,
releases, `SECURITY.md`, GitHub Security Advisories) before assessing it.

Last verified: 2026-10-31

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

### Notification servers

- ntfy server configuration (default port, `auth-file`, `auth-default-access`, ACLs, tokens, admin
  socket, `behind-proxy`, attachments, Web Push keys): https://docs.ntfy.sh/config/
- ntfy publishing and topic names (topic name as the only secret on open servers):
  https://docs.ntfy.sh/publish/
- ntfy FAQ (guessable topics, ACLs): https://docs.ntfy.sh/faq/
- ntfy releases and security advisories: https://github.com/binwiederhier/ntfy/releases and
  https://github.com/binwiederhier/ntfy/security
- Gotify configuration (default port, initial `admin` user and password, registration, `_FILE`
  secrets, trusted proxies, secure cookie, config file permissions): https://gotify.net/docs/config
- Gotify concepts (applications vs clients): https://gotify.net/docs/
- Gotify pushing messages (`X-Gotify-Key` application token): https://gotify.net/docs/pushmsg
- Gotify plugins (Go plugin system): https://gotify.net/docs/plugin
- Gotify releases and security advisories: https://github.com/gotify/server/releases and
  https://github.com/gotify/server/security

### Homelab platforms

- CasaOS repository (install script, supported systems, update and uninstall, web-terminal caution):
  https://github.com/IceWhaleTech/CasaOS
- CasaOS releases (check the date of the latest stable release): https://github.com/IceWhaleTech/CasaOS/releases
- CasaOS security policy and advisories (support limited before v1.0):
  https://github.com/IceWhaleTech/CasaOS/security
- CasaOS wiki (first account, running behind a web server): https://wiki.casaos.io/en/guides/casaos-behind-webserver
- CasaOS app store repository: https://github.com/IceWhaleTech/CasaOS-AppStore
- ZimaOS (the vendor's actively developed NAS OS): https://github.com/IceWhaleTech/ZimaOS
- Vendor-hosted community summary of CasaOS development status (summarizes forum posts; not an official
  lifecycle notice): https://shop.zimaspace.com/pages/is-casaos-abandoned-development-status

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
- A Debian install guide documenting the CasaOS gateway's port fallback (80, then 81–89, then
  8080–8089, saved in `/etc/casaos/gateway.ini`):
  https://computingforgeeks.com/how-to-setup-personal-cloud-using-casaos-on-debian/. Confirm on the
  installed version.
- GitHub repository metadata (last commit, last release, archived flag, open security issues): the
  practical signal for project maintenance status. Read it as evidence, not as a guarantee either way.
