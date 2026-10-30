# Web Servers and Reverse Proxies: References

Always prefer current vendor documentation; directives, defaults, and supported branches change between
releases.

Last verified: 2026-10-30

## Vendor (authoritative)

### TLS guidance

- Mozilla Server Side TLS guidelines and configuration generator (check the guideline version shown):
  https://ssl-config.mozilla.org/ and https://wiki.mozilla.org/Security/Server_Side_TLS
- Machine-readable current guidelines: https://ssl-config.mozilla.org/guidelines/latest.json
- Let's Encrypt, ending OCSP support: https://letsencrypt.org/2024/12/05/ending-ocsp/

### Apache httpd

- Project home (current release, 2.2 end-of-life notice): https://httpd.apache.org/
- Security vulnerabilities by release: https://httpd.apache.org/security/vulnerabilities_24.html
- Security tips: https://httpd.apache.org/docs/2.4/misc/security_tips.html
- Core directives (`ServerTokens`, `Options`, `AllowOverride`, `TraceEnable`):
  https://httpd.apache.org/docs/2.4/mod/core.html
- `mod_status`: https://httpd.apache.org/docs/2.4/mod/mod_status.html
- `mod_remoteip`: https://httpd.apache.org/docs/2.4/mod/mod_remoteip.html

### nginx

- Download page (mainline, stable, legacy): https://nginx.org/en/download.html
- Security advisories: https://nginx.org/en/security_advisories.html
- Core module (`server_tokens`, `listen`, `default_server`):
  https://nginx.org/en/docs/http/ngx_http_core_module.html
- Real IP module: https://nginx.org/en/docs/http/ngx_http_realip_module.html
- Headers module (`add_header`): https://nginx.org/en/docs/http/ngx_http_headers_module.html
- Stub status: https://nginx.org/en/docs/http/ngx_http_stub_status_module.html
- Rate limiting: https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- Auth request: https://nginx.org/en/docs/http/ngx_http_auth_request_module.html

### Caddy

- Admin API: https://caddyserver.com/docs/api
- Caddyfile global options (`admin`, `trusted_proxies`, `client_ip_headers`):
  https://caddyserver.com/docs/caddyfile/options
- Automatic HTTPS: https://caddyserver.com/docs/automatic-https
- Releases and security advisories: https://github.com/caddyserver/caddy/releases and
  https://github.com/caddyserver/caddy/security/advisories

### Traefik

- API and dashboard (`api.insecure`, securing `api@internal`):
  https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/
- Entrypoints (`forwardedHeaders`, `proxyProtocol`):
  https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/
- Docker provider (socket risks, `exposedByDefault`):
  https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/
- Releases and security advisories: https://github.com/traefik/traefik/releases and
  https://github.com/traefik/traefik/security/advisories

### HAProxy

- Project home and branch table (supported branches, end-of-life dates): https://www.haproxy.org/
- Configuration manual: https://docs.haproxy.org/

### Nginx Proxy Manager

- Setup (ports, volumes, database): https://nginxproxymanager.com/setup/
- Guide: https://nginxproxymanager.com/guide/
- Releases and security advisories: https://github.com/NginxProxyManager/nginx-proxy-manager/releases and
  https://github.com/NginxProxyManager/nginx-proxy-manager/security/advisories

### Containers

- Docker Engine security (daemon attack surface): https://docs.docker.com/engine/security/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- endoflife.date (https://endoflife.date/nginx, https://endoflife.date/haproxy, and others): a convenient
  summary of support dates. It can lag or disagree with the vendor; confirm against the vendor page.
- OWASP Secure Headers Project: https://owasp.org/www-project-secure-headers/ for header meanings and
  recommended values. Check against the app before applying a strict policy.
- Certificate transparency search (for example https://crt.sh/): shows every public certificate issued for
  a domain. Useful in Discover (internal names exposed) and Respond (unexpected issuance).
