# OPNsense: References

Always prefer current OPNsense documentation; menus and features change between release series.

Last verified: 2026-10-30

## Vendor (authoritative)

- Security policy, "Run an Audit", sensitive privileges, deployment considerations:
  https://docs.opnsense.org/security.html
- Security advisories (published on GitHub): https://github.com/opnsense/core/security/advisories?state=published
- Release notes, all series: https://docs.opnsense.org/releases.html
- Settings (administration, web GUI, SSH, console, logging, cron): https://docs.opnsense.org/manual/settingsmenu.html
- Two-factor authentication (TOTP): https://docs.opnsense.org/manual/how-tos/two_factor.html
- Configuration backups and history: https://docs.opnsense.org/manual/backups.html
- Git backup plugin: https://docs.opnsense.org/manual/git-backup.html
- DHCP (dnsmasq, Kea, ISC): https://docs.opnsense.org/manual/dhcp.html
- ISC DHCP (end-of-life notice): https://docs.opnsense.org/manual/isc.html
- dnsmasq DNS and DHCP: https://docs.opnsense.org/manual/dnsmasq.html
- Firewall advanced settings: https://docs.opnsense.org/manual/firewall_settings.html
- Release announcements and security update notices: https://forum.opnsense.org/

## Upstream

- FreeBSD security advisories: https://www.freebsd.org/security/advisories/
- FreeBSD VuXML (the database behind the firmware security audit): https://vuxml.freebsd.org/freebsd/index.html

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Home Network Guy, OPNsense access-hardening guides:
  https://homenetworkguy.com/how-to/ways-to-secure-access-to-opnsense-and-your-home-network/
  Practical walkthroughs for restricting management access and segmenting networks. Check each step
  against the current OPNsense version.
