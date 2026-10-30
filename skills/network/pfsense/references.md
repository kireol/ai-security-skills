# pfSense: References

Always prefer current Netgate documentation; menus and features change between releases, and CE and Plus
differ.

Last verified: 2026-10-30

## Vendor (authoritative)

- Security advisories (pfSense-SA-YY_NN): https://docs.netgate.com/advisories/index.html
- Release notes, CE and Plus, with supported and unsupported releases:
  https://docs.netgate.com/pfsense/en/latest/releases/index.html
- Upgrade guide (branches, update settings, cautions):
  https://docs.netgate.com/pfsense/en/latest/install/upgrade-guide.html
- Admin access settings (GUI, anti-lockout, DNS rebind check, HTTP_REFERER, login protection, SSH,
  console): https://docs.netgate.com/pfsense/en/latest/config/advanced-admin.html
- Remote administration recommendations:
  https://docs.netgate.com/pfsense/en/latest/recipes/remote-firewall-administration.html
- Console menu options: https://docs.netgate.com/pfsense/en/latest/config/console-menu.html
- User privileges: https://docs.netgate.com/pfsense/en/latest/usermanager/privileges.html
- Users and SSH authorized keys: https://docs.netgate.com/pfsense/en/latest/usermanager/users.html
- Viewing the loaded ruleset (`pfctl`, anchors): https://docs.netgate.com/pfsense/en/latest/firewall/pf-ruleset.html
- UPnP IGD & PCP: https://docs.netgate.com/pfsense/en/latest/services/upnp.html
- WireGuard: https://docs.netgate.com/pfsense/en/latest/vpn/wireguard/index.html
- DNS Resolver and access lists: https://docs.netgate.com/pfsense/en/latest/services/dns/resolver.html and
  https://docs.netgate.com/pfsense/en/latest/services/dns/resolver-acls.html
- DHCP (Kea and ISC backends, deprecation notice): https://docs.netgate.com/pfsense/en/latest/services/dhcp/index.html
- AutoConfigBackup: https://docs.netgate.com/pfsense/en/latest/backup/autoconfigbackup.html and
  https://docs.netgate.com/pfsense/en/latest/backup/acb-info.html
- Restoring from backups and Config History: https://docs.netgate.com/pfsense/en/latest/backup/restore.html
- Remote logging: https://docs.netgate.com/pfsense/en/latest/monitoring/logs/remote.html
- pfBlockerNG package: https://docs.netgate.com/pfsense/en/latest/packages/pfblocker.html
- Netgate Nexus multi-instance management (Plus): https://docs.netgate.com/pfsense/en/latest/mim/index.html
- Bug and feature tracker: https://redmine.pfsense.org/

## Upstream

- FreeBSD security advisories: https://www.freebsd.org/security/advisories/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Netgate Forum: https://forum.netgate.com/
  Release announcements and community troubleshooting. Posts by Netgate staff are useful context; others
  are opinions. Confirm anything important in the documentation.
