# Photo and Document Apps: References

Both projects release frequently. Always prefer the project's current documentation, release notes, and
security advisories for the installed version. Re-verify links and contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

### Immich

- Docker Compose installation (`UPLOAD_LOCATION`, `DB_DATA_LOCATION`, `DB_PASSWORD`, version pinning):
  https://docs.immich.app/install/docker-compose/
- Environment variables (default ports 2283 and 3003, metrics ports, trusted proxies, password files):
  https://docs.immich.app/install/environment-variables/
- OAuth (auto register, auto launch, role and quota claims, mobile redirect):
  https://docs.immich.app/administration/oauth/
- Sharing (shared links, partner sharing): https://docs.immich.app/features/sharing/
- External libraries (read-only mounts, ownership, deletion behavior):
  https://docs.immich.app/features/libraries/
- Security policy and advisories: https://github.com/immich-app/immich/security
- Releases (version and migration notes): https://github.com/immich-app/immich/releases

### Paperless-ngx

- Configuration (secret key, allowed hosts, trusted proxies, admin user, auto-login, remote-user auth,
  social login, MFA, consumption folder, trash): https://docs.paperless-ngx.com/configuration/
  (source: https://github.com/paperless-ngx/paperless-ngx/blob/main/docs/configuration.md)
- Usage (share links, mail rules, permissions, workflows, 2FA, AI and remote OCR):
  https://docs.paperless-ngx.com/usage/
- Administration (backup with the document exporter, management commands):
  https://docs.paperless-ngx.com/administration/
- Security policy and advisories: https://github.com/paperless-ngx/paperless-ngx/security
- Releases: https://github.com/paperless-ngx/paperless-ngx/releases

### Containers and access layers

- Docker Engine security: https://docs.docker.com/engine/security/
- Docker packet filtering and firewalls (published ports bypassing host firewall rules):
  https://docs.docker.com/engine/network/packet-filtering-firewalls/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Gotenberg (https://gotenberg.dev/) and Apache Tika (https://tika.apache.org/): document conversion and
  parsing services used by Paperless for Office files. They parse untrusted input; keep them on the
  internal Compose network and update them with Paperless.
