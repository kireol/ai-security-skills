# UPS: References

Always prefer current vendor documentation for the exact card model, firmware, and software version.
Re-verify links and contents when updating this skill; record the date checked.

Last verified: 2026-10-31

## Vendor (authoritative)

- Network UPS Tools
  - `upsd.conf` (LISTEN default, port 3493, TLS options, file-permission guidance):
    https://networkupstools.org/docs/man/upsd.conf.html
  - `upsd.users` (actions, instcmds, upsmon primary/secondary, file permissions):
    https://networkupstools.org/docs/man/upsd.users.html
  - `upsmon.conf` (MONITOR lines, primary/secondary roles): https://networkupstools.org/docs/man/upsmon.conf.html
  - NUT documentation index (security chapter, user manual): https://networkupstools.org/documentation.html
- APC / Schneider Electric
  - Schneider Electric security notifications: https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp
  - PowerChute Network Shutdown ports (UDP/TCP 3052, TCP 6547, NMC registration ports):
    https://www.se.com/us/en/faqs/FA373363/
  - NMC firmware upgrade methods, NMC2/NMC3, Secure NMC System tool: https://www.apc.com/be/en/faqs/FA156047
  - NMC3 password recovery (no reset to the default; full factory reset):
    https://www.se.com/us/en/faqs/FA156064/
  - PowerChute Business Edition product range (discontinued; replaced by PowerChute Serial Shutdown):
    https://www.apc.com/be/en/product-range/61932-powerchute-business-edition
  - UPS management software guide (which PowerChute product to use):
    https://www.se.com/ca/en/work/support/product-support/ups-management-software-guide/
- CyberPower
  - RMCARD205 product page (manuals, firmware downloads): https://www.cyberpower.com/sg/en/product/sku/rmcard205
  - No dedicated CyberPower security-advisory index was found; check CISA ICS advisories and the product
    download pages.
- Eaton
  - Eaton cybersecurity security notifications:
    https://www.eaton.com/us/en-us/company/news-insights/cybersecurity/security-notifications.html
  - Network-M2 product page (forced password change on setup; end-of-life notice): https://www.eaton.com/network-m2
- Government
  - CISA ICS advisories (UPS cards and shutdown software appear here):
    https://www.cisa.gov/news-events/cybersecurity-advisories
  - Example: CISA ICSA-24-123-01, CyberPower PowerPanel Business:
    https://www.cisa.gov/news-events/ics-advisories/icsa-24-123-01

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Schneider Electric community thread reporting NMC2 (AP9630/AP9631/AP9635) as end of life with no further
  firmware: https://community.se.com/t5/APC-UPS-Data-Center-Enterprise/How-to-determine-NMC-version-via-software/td-p/475968
  A forum post, not an official notice; confirm on Schneider's lifecycle pages.

## Not verified when writing this skill

- The official end-of-life date for NMC2 cards and the current NMC3 firmware subscription terms.
- Default web UI ports for PowerChute Serial Shutdown and CyberPower PowerPanel Business/Personal on the
  latest versions; check each user guide.
- The default PowerChute Network Shutdown authentication phrase on the current release; check the PCNS
  user guide.
- Which APC NMC SSH CLI commands are read-only on every firmware.
