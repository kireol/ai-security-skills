# Home Assistant: References

Always prefer current Home Assistant documentation; menus and settings change between monthly releases.

Last verified: 2026-10-30

## Vendor (authoritative)

- Security policy, reporting, published advisories, and what is out of scope (including "every user is
  trusted"): https://www.home-assistant.io/security/
- Security advisories (GitHub): https://github.com/home-assistant/core/security/advisories
- Securing checklist: https://www.home-assistant.io/docs/configuration/securing/
- Release notes and blog (monthly releases, breaking changes): https://www.home-assistant.io/blog/
- Home Assistant Alerts (vendor alerts shown in Repairs): https://alerts.home-assistant.io/ and
  https://www.home-assistant.io/integrations/homeassistant_alerts/
- Deprecation of Core and Supervised installs and 32-bit systems (May 2025):
  https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/
- Installation types: https://www.home-assistant.io/installation/
- Authentication overview and tokens: https://www.home-assistant.io/docs/authentication/
- Auth providers (`homeassistant`, `trusted_networks`, `command_line`):
  https://www.home-assistant.io/docs/authentication/providers/
- Multi-factor authentication: https://www.home-assistant.io/docs/authentication/multi-factor-auth/
- Locked out (console password reset): https://www.home-assistant.io/docs/locked_out/
- Auth API (long-lived token validity): https://contributors.home-assistant.io/core/internals/auth-api/
- HTTP server (port, trusted proxies, X-Forwarded-For, IP bans, `/local/`):
  https://www.home-assistant.io/integrations/http/
- Remote access options: https://www.home-assistant.io/docs/configuration/remote/
- Secrets (`secrets.yaml`): https://www.home-assistant.io/docs/configuration/secrets/
- Backups (encryption, emergency kit, locations): https://www.home-assistant.io/common-tasks/general/backups/
- Recorder: https://www.home-assistant.io/integrations/recorder/
- Zeroconf discovery: https://www.home-assistant.io/integrations/zeroconf/
- App (add-on) security, protection mode, and security rating:
  https://contributors.home-assistant.io/apps/guides/security/
- Home Assistant Cloud remote access (Nabu Casa support): https://support.nabucasa.com/
- HACS and the built-in Marketplace (2026.11): https://www.hacs.xyz/docs/use/ and
  https://www.hacs.xyz/docs/marketplace/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Home Assistant community forum: https://community.home-assistant.io/
  Useful for known issues after a release and app-specific behavior. Verify anything security-relevant
  against the vendor documentation and the installed version.
