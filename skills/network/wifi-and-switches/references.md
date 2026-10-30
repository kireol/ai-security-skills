# Wi-Fi Mesh and Managed Switches: References

Always prefer current vendor documentation for the exact model and firmware. Consumer mesh apps change
menus often, and lifecycle dates are per model. Re-verify links and contents when updating this skill.

Last verified: 2026-10-30

## Standards and government guidance (authoritative)

- Wi-Fi Alliance, Wi-Fi security overview (WPA3, PMF, Enhanced Open): https://www.wi-fi.org/discover-wi-fi/security
- CERT/CC VU#723755, WPS PIN brute-force design flaw: https://www.kb.cert.org/vuls/id/723755
- CISA alert TA12-006A, WPS PIN brute force (notes some devices keep WPS on when the UI says off):
  https://www.cisa.gov/uscert/ncas/alerts/TA12-006A
- CISA BOD 26-02, Mitigating Risk From End-of-Support Edge Devices (definitions include switches and
  wireless access points; binding on US federal agencies, recommended for everyone):
  https://www.cisa.gov/news-events/directives/bod-26-02-mitigating-risk-end-support-edge-devices
- NSA, Hardening Network Devices (SNMPv3, unused ports, native VLAN, out-of-band management):
  https://media.defense.gov/2020/Aug/18/2002479461/-1/-1/0/HARDENING_NETWORK_DEVICES.PDF
- NSA, Cisco Smart Install protocol misuse (disable with `no vstack`; block TCP 4786):
  https://media.defense.gov/2019/Jul/16/2002157833/-1/-1/0/CSA-CISCO-SMART-INSTALL-PROTOCOL-MISUSE.PDF

## Vendor (authoritative)

- Cisco Smart Install advisory (detection with `show tcp brief all | include 4786`; ACL fallback):
  https://www.cisco.com/c/en/us/support/docs/csa/cisco-sa-20180409-smi.html
- Cisco Security Advisories (PSIRT): https://sec.cloudapps.cisco.com/security/center/publicationListing.x
- Cisco end-of-life bulletins (per product; look for "End of Vulnerability/Security Support"):
  https://www.cisco.com/c/en/us/products/eos-eol-listing.html
- Google Nest Wifi / Google Wifi security features (WPA2 default, WPA3 transition-mode toggle, signed
  automatic updates, UPnP warning): https://support.google.com/googlenest/answer/6309220
- eero, What is bridge mode? (features lost in bridge mode; wired requirement):
  https://support.eero.com/hc/articles/208276903
- eero, What is NAT? (double NAT trade-offs): https://eero.com/support/articles/what-is-nat
- TP-Link end-of-life products list (home products such as Deco; check the regional site for your
  model): https://www.tp-link.com/us/support/faq/3562/
- TP-Link security advisories: https://www.tp-link.com/us/press/security-advisory/
- NETGEAR security advisories (Orbi and other products): https://www.netgear.com/about/security/
- Ubiquiti UniFi required ports reference (discovery and device-inform ports):
  https://help.ui.com/hc/en-us/articles/218506997-UniFi-Network-Required-Ports-Reference
- Ubiquiti security advisory bulletins: https://community.ui.com/releases (filter for security advisories)

For any other vendor, find its security advisory page, its product lifecycle / end-of-support page, and
the release notes for the exact model before assessing.

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- HPE Aruba Networking, Wi-Fi security modes (WPA3, transition mode, PMF, and 6 GHz rules explained
  in detail): https://arubanetworking.hpe.com/techdocs/aos/wifi-design-deploy/security/modes/overview/
  A different vendor's documentation, useful for the standards behavior; menus won't match consumer
  products.
