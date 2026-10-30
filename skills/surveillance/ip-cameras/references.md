# IP Cameras: References

Always prefer the current vendor documentation and advisories for the exact model and hardware
revision. Camera menus, defaults, and support status change with firmware. Vendor advisory pages often
need a browser (JavaScript), so open them directly when an automated fetch returns nothing.

Last verified: 2026-10-30

## Vendor (authoritative)

- Hikvision cybersecurity advisories: https://www.hikvision.com/en/support/cybersecurity/security-advisory/
  (page needs a browser; content not verified by automated fetch)
- Hikvision port list (legacy US technical bulletin): https://us-legacy.hikvision.com/sites/default/files/tb/network_port_list.pdf
- Dahua cybersecurity center and advisories: https://www.dahuasecurity.com/support/cybersecurity (verify the current index page)
- Reolink, how to disable UID (P2P) and configure service ports:
  https://support.reolink.com/hc/en-us/articles/900000621783-How-to-Disable-UID/
- Reolink, about UID: https://support.reolink.com/hc/en-us/articles/360013481134-Enable-UID-for-Reolink-Products
- TP-Link Tapo, RTSP/ONVIF questions (ports, camera account, remote-access warning):
  https://www.tp-link.com/ph/support/faq/4465 (regional mirrors exist)
- TP-Link Tapo, viewing a camera via RTSP/ONVIF: https://tp-link.com/support/faq/2680
- TP-Link security advisories: https://www.tp-link.com/us/press/security-advisory/
- Wyze, product security information and support periods: https://www.wyze.com/pages/psti
- Wyze, reporting a vulnerability: https://www.wyze.com/pages/security-report
- Wyze, response to the 2022 security report (Wyze Cam v1 end-of-life):
  https://www.wyze.com/pages/response-to-3-29-22-security-report
- Ubiquiti release notes and security advisory bulletins: https://community.ui.com/releases
- Thingino open firmware (supported hardware, installation): https://thingino.com and
  https://github.com/themactep/thingino-firmware/wiki

## Government advisories

- CISA alert, Hikvision CVE-2021-36260: https://www.cisa.gov/news-events/alerts/2021/09/28/rce-vulnerability-hikvision-cameras-cve-2021-36260
- CISA ICS advisory ICSA-17-341-01, Xiongmai IP cameras and DVRs: https://www.cisa.gov/ics/advisories/ICSA-17-341-01
- CISA Known Exploited Vulnerabilities catalog (search by vendor):
  https://www.cisa.gov/known-exploited-vulnerabilities-catalog

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- NVD records for CVE-2021-33044 / CVE-2021-33045 (Dahua) and CVE-2022-45045 (Xiongmai):
  https://nvd.nist.gov/ . Use for affected versions and references; confirm fixes with the vendor.
- IPCamTalk forums (https://ipcamtalk.com): community knowledge on OEM relationships, firmware families,
  and per-model settings. Anecdotal; never follow its cross-flashing guides as security remediation.
- Press coverage of the February 2024 Wyze incident (for example
  https://www.malwarebytes.com/blog/news/2024/02/wyze-cameras-show-the-wrong-feeds-to-customers-again):
  context for cloud-account risk; figures come from the vendor's own statements.
