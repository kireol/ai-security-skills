# QNAP QTS and QuTS hero: References

Always prefer current QNAP documentation for exact firmware behavior, builds, and app versions. Re-verify
links and contents when updating this skill; record the date checked. Download QNAP utilities only from
official QNAP domains; QNAP has warned about fake Qfinder Pro download sites.

Last verified: 2026-10-31

## Vendor (authoritative)

- Security advisories (firmware and apps): https://www.qnap.com/en/security-advisories
- Best practices for enhancing NAS security (closing ports 8080/443, UPnP, myQNAPcloud Link, QVPN):
  https://www.qnap.com/en/how-to/faq/article/what-is-the-best-practice-for-enhancing-nas-security
- Network ports used by QTS, QuTS hero, and QuTScloud (default port list, including web admin, Qfinder Pro,
  Telnet): https://www.qnap.com/en/how-to/faq/article/what-network-ports-are-used-by-qts-quts-hero-and-qutscloud-systems
- Product Support Status (per-model support and security-update end dates): https://www.qnap.com/go/product/status
- How to check product support status: https://www.qnap.com/en/how-to/faq/con_show.php?cid=3397
- Security Center (QTS 5.2 / QuTS hero h5.2 and later): https://www.qnap.com/static/landing/2023/en-security-center/index.html
- Example campaign advisories (historical; read for the response pattern, check for newer ones):
  - DeadBolt and Photo Station, QSA-22-24: https://www.qnap.com/en-us/security-advisory/qsa-22-24
  - eCh0raix and brute-force guidance, NAS-201907-11: https://www.qnap.com/go/security-advisory/nas-201907-11
  - Checkmate (SMB exposed to the internet, dictionary attacks), QSA-22-21:
    https://www.qnap.com/go/security-advisory/qsa-22-21
- Release notes and firmware downloads: from the model's page under https://www.qnap.com/en/download

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents. QNAP-specific government advisory (archived, historical; shows the
update-blocking persistence pattern): CISA/NCSC AA20-209A on QSnatch,
https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-209a. Search CISA and national CERT sites
for newer ones.

## Third-party (not authoritative)

- endoflife.date and similar trackers summarize lifecycles but disagree with each other and with QNAP;
  always confirm on the Product Support Status page.
- News coverage of the Qlocker (2021) and DeadBolt (2022) campaigns was used only to confirm which classes
  of app (backup, media, photo) were involved; specific CVE and version details must come from QNAP's
  advisories.
