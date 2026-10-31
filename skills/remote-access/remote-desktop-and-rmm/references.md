# Remote Desktop and RMM: References

Always prefer current vendor documentation for the installed version. These projects change quickly and
option names move between releases. Re-verify links and contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

### Apache Guacamole

- Security reports and fixed vulnerabilities: https://guacamole.apache.org/security/
- Releases: https://guacamole.apache.org/releases/
- Database authentication (default administrator created by the schema): https://guacamole.apache.org/doc/gug/jdbc-auth.html
- TOTP two-factor authentication (per-user and per-group disabling from 1.6.0): https://guacamole.apache.org/doc/gug/totp-auth.html
- Docker images and configuration: https://guacamole.apache.org/doc/gug/guacamole-docker.html
- Manual index (brute-force blocking, recording, parameter tokens): https://guacamole.apache.org/doc/gug/

### RustDesk

- Self-hosting overview (ports, OSS vs. Pro): https://rustdesk.com/docs/en/self-host/
- OSS server installation (WebSocket ports and header validation warning): https://rustdesk.com/docs/en/self-host/rustdesk-server-oss/install/
- Server repository (hbbs/hbbr options, key handling): https://github.com/rustdesk/rustdesk-server
- Client security advisories: https://github.com/rustdesk/rustdesk/security

### MeshCentral

- Documentation: https://docs.meshcentral.com/
- Secure installation (dedicated low-privilege user): https://docs.meshcentral.com/install/security/secure/
- Security settings (login rate limiting, Duo 2FA, AMT TLS): https://docs.meshcentral.com/meshcentral/security/
- Configuration options (`newAccounts`, 2FA, allowed IPs): https://docs.meshcentral.com/meshcentral/config/
- Security advisories: https://github.com/Ylianst/MeshCentral/security

### Tactical RMM

- Security policy: https://docs.tacticalrmm.com/security/
- Server installation (hostnames, ports, `--insecure` warning): https://docs.tacticalrmm.com/install_server/
- API access (keys inherit user role; keys bypass 2FA): https://docs.tacticalrmm.com/functions/api/
- MeshCentral integration (mesh superuser, `userAllowedIP`, `agentAllowedIP`): https://docs.tacticalrmm.com/mesh_integration/
- Security advisories: https://github.com/amidaware/tacticalrmm/security

### Government guidance

- CISA, NSA, and MS-ISAC advisory AA23-025A, malicious use of legitimate RMM software (portable
  executables, detection, application allowlisting): https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-025a

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Community MeshCentral configuration guides and Docker images: useful for recognizing how an instance was
  deployed; confirm every setting against the vendor configuration reference.
- Community Guacamole compose stacks: often create `guacadmin` with the default password from the vendor
  schema; treat a stack's defaults as public.
