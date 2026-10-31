# Automation Platforms: References

Both platforms change quickly (n8n releases very often; Node-RED ships a new major yearly). Always prefer
the vendor's current documentation and advisories for the installed version. The n8n documentation is
being reorganized; if a link below redirects, follow it to the current page. Re-verify links and
contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

### n8n

- Securing n8n (overview: SSL, SSO, 2FA, audit, public API, blocking nodes, task runners, SSRF
  protection, key rotation): https://docs.n8n.io/hosting/securing/overview/
- Security audit (`n8n audit`, `/audit` API, risk categories): https://docs.n8n.io/hosting/securing/security-audit/
- Blocking nodes (`NODES_EXCLUDE`): https://docs.n8n.io/hosting/securing/blocking-nodes/
- Disabling the public API: https://docs.n8n.io/hosting/securing/disable-public-api/
- Encryption key (`N8N_ENCRYPTION_KEY`, queue-mode workers):
  https://docs.n8n.io/hosting/configuration/configuration-examples/encryption-key/
- Security environment variables (env access, file access, cookies):
  https://docs.n8n.io/hosting/configuration/environment-variables/security/
- Node environment variables (default `NODES_EXCLUDE`, community package toggles, Code-node module
  allowlists): https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/nodes
- Community node risks (full machine access, verified vs. unverified):
  https://docs.n8n.io/integrations/community-nodes/risks/
- Docker installation (port 5678, data folder, tunnel warning): https://docs.n8n.io/hosting/installation/docker/
- Security advisories: https://github.com/n8n-io/n8n/security
- Release notes: https://docs.n8n.io/release-notes/

### Node-RED

- Securing Node-RED (`adminAuth`, `hash-pw`, `httpNodeAuth`, `httpStaticAuth`, HTTPS, session expiry):
  https://nodered.org/docs/user-guide/runtime/securing-node-red
- Runtime configuration (`uiHost`, `uiPort`, `httpAdminRoot`, `disableEditor`, `externalModules`,
  `functionExternalModules`): https://nodered.org/docs/user-guide/runtime/configuration
- Default settings file (comments on `credentialSecret`, diagnostics, runtime state):
  https://github.com/node-red/node-red/blob/master/packages/node_modules/node-red/settings.js
- Admin API `GET /auth/login` (detecting whether editor auth is active):
  https://nodered.org/docs/api/admin/methods/get/auth/login/
- Releases and support policy (current, maintenance, end-of-life streams):
  https://nodered.org/about/releases/
- Security policy and advisories: https://github.com/node-red/node-red/security

### Home Assistant add-on

- Node-RED add-on documentation (ingress vs. direct port, `credential_secret`, `http_node`,
  `http_static`, `init_commands`, `leave_front_door_open`):
  https://github.com/hassio-addons/addon-node-red/blob/main/node-red/DOCS.md

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Reports in 2026 of malicious npm packages posing as n8n community nodes to harvest OAuth tokens
  (third-party write-ups, not a vendor advisory). Useful as a reason to restrict unverified community
  packages; check the original sources before citing details.
