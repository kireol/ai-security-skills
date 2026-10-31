# Homebridge: References

Always prefer the Homebridge project's current documentation and release notes; options and install
methods change between releases. Re-verify links and contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

- Homebridge UI (homebridge-config-ui-x) README (default port 8581; default `admin` / `admin`
  credentials; child bridges; backup and restore): https://github.com/homebridge/homebridge-config-ui-x
- Homebridge UI config options (`auth` form/none, `host` default `0.0.0.0`, `sessionTimeout` default
  28800 seconds, `ssl`, `proxyHost`, `scheduledBackupPath`, `scheduledBackupDisable`):
  https://github.com/homebridge/homebridge-config-ui-x/wiki/Config-Options
- Homebridge UI manual configuration (the `sudo` option requires passwordless sudo; accessory control
  requires insecure mode): https://github.com/homebridge/homebridge-config-ui-x/wiki/Manual-Configuration
- Homebridge UI security advisories and policy: https://github.com/homebridge/homebridge-config-ui-x/security
- Homebridge UI releases: https://github.com/homebridge/homebridge-config-ui-x/releases
- Homebridge releases: https://github.com/homebridge/homebridge/releases
- Homebridge security advisories: https://github.com/homebridge/homebridge/security
- Homebridge wiki (install guides for each platform): https://github.com/homebridge/homebridge/wiki
- Install Homebridge on Debian or Ubuntu (apt package, storage path `/var/lib/homebridge`, `hb-shell`,
  update procedure): https://github.com/homebridge/homebridge/wiki/Install-Homebridge-on-Debian-or-Ubuntu-Linux
- Homebridge Raspberry Pi image, getting started (Imager install, first-boot account creation from
  release 1.4.0, "Homebridge WiFi Setup" hotspot, `homebridge.local`):
  https://github.com/homebridge/homebridge-raspbian-image/wiki/Getting-Started
- Homebridge apt package releases (bundled Node.js, Homebridge, and UI versions):
  https://github.com/homebridge/homebridge-apt-pkg/releases
- Homebridge Docker image: https://github.com/homebridge/docker-homebridge
- Verified plugins program: https://github.com/homebridge/homebridge/wiki/Verified-Plugins
- Apple, Home app user guide (sharing a home, home hubs, accessories):
  https://support.apple.com/guide/iphone/intro-to-home-iph6f85b2b33/ios

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- GitHub Advisory Database, npm ecosystem (search for each plugin's package name):
  https://github.com/advisories?query=ecosystem%3Anpm
- Plugin changelogs noting that Homebridge 2.0 (May 2026) requires Node.js 22 or 24 and changed the
  default mDNS advertiser; confirm on the Homebridge release notes above.
