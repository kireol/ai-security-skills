# Unraid: References

Always prefer current Unraid documentation and release notes for exact behavior. Re-verify links and
contents when updating this skill; record the date checked.

Last verified: 2026-10-31

## Vendor (authoritative)

- Release notes (security fixes are announced here; read every version between installed and current):
  https://docs.unraid.net/unraid-os/release-notes/
  - Example security maintenance release (7.2.9): https://docs.unraid.net/unraid-os/release-notes/7.2.9/
  - 7.3.0 (internal boot, TPM licensing, rollback limits): https://docs.unraid.net/unraid-os/release-notes/7.3.0/
- Updating Unraid: https://docs.unraid.net/unraid-os/updating-unraid/
- Security fundamentals (share modes, port-forwarding risks, remote administration):
  https://docs.unraid.net/unraid-os/system-administration/secure-your-server/security-fundamentals/
- Securing your connection (Use SSL/TLS, ports, `myunraid.net` certificates, `use_ssl` recovery):
  https://docs.unraid.net/unraid-os/system-administration/secure-your-server/securing-your-connection
- User management (root vs. share users, password reset via the boot device):
  https://docs.unraid.net/unraid-os/system-administration/secure-your-server/user-management/
- Securing the flash drive: https://docs.unraid.net/unraid-os/system-administration/secure-your-server/secure-your-flash-drive
  (page did not render for automated fetch on the verification date; read it in a browser)
- Unraid Connect remote access: https://docs.unraid.net/unraid-connect/remote-access
- Unraid Connect automated flash backup (unencrypted in the cloud, exclusions, restore):
  https://docs.unraid.net/unraid-connect/automated-flash-backup
- Changing the flash device: https://docs.unraid.net/unraid-os/system-administration/maintain-and-update/changing-the-flash-device/
- Coordinated vulnerability disclosure (January 2025; WebGUI XSS/CSRF and the Community Applications
  repository-takeover fix): https://newsletter.unraid.net/p/unraid-coordinated-vulnerability-disclosure
- Security guidelines for plugin authors (forum): https://forums.unraid.net/topic/185562-security-guidelines-for-plugins/
- Unraid security best practices (blog; older, check against current docs):
  https://unraid.net/blog/unraid-server-security-best-practices

No dedicated vendor security-advisory feed was found on the verification date. Search NVD and the Zero Day
Initiative for "Unraid" for CVEs, and confirm fixed versions in the release notes.

- NVD search: https://nvd.nist.gov/vuln/search (keyword "Unraid")
- Zero Day Initiative published advisories: https://www.zerodayinitiative.com/advisories/published/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Unraid forums (https://forums.unraid.net/): announcements, plugin support threads, and staff replies.
  Useful for context on specific plugins and known issues; user posts are not authoritative, and plugin
  support threads are run by plugin authors.
- Community Applications (the CA plugin and its app feed): a catalog of third-party plugins and Docker
  templates. Its listing is not a security review of the app.
