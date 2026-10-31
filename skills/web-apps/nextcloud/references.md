# Nextcloud: References

Always prefer current Nextcloud documentation for the installed major version (the `latest` manual links
below track the newest major; versioned manuals exist for older ones). Re-verify links and contents when
updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

- Security advisories (authoritative list): https://github.com/nextcloud/security-advisories
- Security overview, reporting, and bug bounty: https://nextcloud.com/security/
- Maintenance and release schedule (supported majors, end-of-life dates):
  https://github.com/nextcloud/server/wiki/Maintenance-and-Release-Schedule
- Hardening and security guidance (HTTPS, HSTS, fail2ban, `allowed_admin_ranges`, data directory):
  https://docs.nextcloud.com/server/latest/admin_manual/installation/harden_server.html
- Reverse proxy configuration (`trusted_proxies`, `forwarded_for_headers`, overwrite settings):
  https://docs.nextcloud.com/server/latest/admin_manual/configuration_server/reverse_proxy_configuration.html
- Brute-force protection: https://docs.nextcloud.com/server/latest/admin_manual/configuration_server/bruteforce_configuration.html
- Two-factor authentication (enforcement, backup codes, `occ twofactorauth:*`):
  https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/two_factor-auth.html
- File sharing settings (link passwords, expiry, public uploads):
  https://docs.nextcloud.com/server/latest/admin_manual/configuration_files/file_sharing_configuration.html
- Federated cloud sharing: https://docs.nextcloud.com/server/latest/admin_manual/configuration_files/federated_cloud_sharing_configuration.html
- Server-side encryption (what it protects, master key vs. user keys, decrypt-all):
  https://docs.nextcloud.com/server/latest/admin_manual/configuration_files/encryption_configuration.html
- Background jobs (AJAX, Webcron, Cron): https://docs.nextcloud.com/server/latest/admin_manual/configuration_server/background_jobs_configuration.html
- occ command reference: https://docs.nextcloud.com/server/latest/admin_manual/occ_command.html and
  system commands (setupchecks, brute-force, background jobs): https://docs.nextcloud.com/server/latest/admin_manual/occ_system.html
- Code signing (official vs. other apps; integrity checks): https://docs.nextcloud.com/server/stable/admin_manual/issues/code_signing.html
- Nextcloud All-in-One (ports, Docker socket, AIO interface login, BorgBackup, reset warnings):
  https://github.com/nextcloud/all-in-one
- AIO behind a reverse proxy (`APACHE_PORT`, `APACHE_IP_BINDING`, AIO interface certificate):
  https://github.com/nextcloud/all-in-one/blob/main/reverse-proxy.md
- Nextcloud Security Scan (external check of a public instance; sends the hostname to the vendor):
  https://scan.nextcloud.com/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- fail2ban and CrowdSec documentation for the jail or collection that reads `nextcloud.log`: useful for
  rate limiting in front of Nextcloud. Match the filter to the installed version's log format.
