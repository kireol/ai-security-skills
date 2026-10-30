# Home Routers and ISP Gateways: References

Always prefer current vendor and ISP documentation. Menus, feature names, and support status vary by
model, hardware version, firmware, and ISP. Re-verify links and contents when updating this skill.

Last verified: 2026-10-30

## Vendor (authoritative)

Router vendors (security advisories and end-of-life pages; regional copies exist, so use the user's
region):

- ASUS product security advisories: https://www.asus.com/content/asus-product-security-advisory/
- NETGEAR product security advisories: https://www.netgear.com/about/security/
- TP-Link security advisories: https://www.tp-link.com/us/press/security-advisory/
- TP-Link end-of-life product lists: https://www.tp-link.com/support/faq/3562/
- For other vendors (Linksys, D-Link, ISP OEMs), use the vendor's own security-advisory and end-of-life or
  support-status pages for the exact model and hardware version. For ISP gateways, use the ISP's support
  pages and ask the ISP.

OpenWrt:

- Security guide, release support status, and end-of-life policy:
  https://openwrt.org/docs/guide-developer/security
- Security advisories: https://openwrt.org/advisory/start
- Securing LuCI access (WAN blocked by default, HTTPS, SSH tunnel): https://openwrt.org/docs/guide-user/luci/luci.secure
- Warning against mass package upgrades: https://openwrt.org/meta/infobox/upgrade_packages_warning
- apk package manager (25.12 and later): https://openwrt.org/docs/guide-user/additional-software/apk
- Bridge-mode and half-bridge terminology: https://openwrt.org/docs/guide-user/network/wan/bridge-mode

DD-WRT:

- Firmware FAQ (builds are betas; router database caveats): https://dd-wrt.com/wiki/index.php/Index:FAQ

ISP documentation (example of passthrough behavior):

- AT&T, IP passthrough (removes the gateway's firewall protection from the passthrough device):
  https://www.att.com/support/smallbusiness/article-modal/smb-internet/KM1188700/

## Government guidance

- FBI IC3 PSA I-050725-PSA (May 2025), criminal proxy services exploiting end-of-life routers:
  https://www.ic3.gov/PSA/2025/PSA250507
- CISA BOD 26-02 (February 2026), mitigating risk from end-of-support edge devices (binds US federal
  civilian agencies): https://www.cisa.gov/news-events/directives/bod-26-02-mitigating-risk-end-support-edge-devices
- CISA Project Upskill, securing home Wi-Fi (remote management, UPnP, WPS, firmware, guest network):
  https://www.cisa.gov/audiences/high-risk-communities/projectupskill/module5
- NSA, Best Practices for Securing Your Home Network (2023):
  https://media.defense.gov/2023/Feb/22/2003165170/-1/-1/0/CSI_BEST_PRACTICS_FOR_SECURING_YOUR_HOME_NETWORK.PDF
- UK NCSC (April 2026), state actors hijacking routers for DNS hijacking:
  https://www.ncsc.gov.uk/news/uk-exposes-russian-military-intelligence-hijacking-vulnerable-routers-for-cyber-attacks

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Broadband Forum, TR-069 (CPE WAN Management Protocol) specification: https://www.broadband-forum.org/
  Defines CWMP; useful for understanding what an ISP's management server can do. Port and feature details
  vary by ISP and device.
- The Register (2016), Mirai variant abusing port 7547 on ISP routers:
  https://www.theregister.com/2016/11/28/router_flaw_exploited_in_massive_attack/
  Historical context for why WAN-reachable management services matter. News coverage, not a vendor
  advisory.
- endoflife.date, OpenWrt release tracking: https://endoflife.date/openwrt
  Convenient summary; confirm against OpenWrt's own security page.
