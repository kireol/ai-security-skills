# TrueNAS: References

Always prefer current TrueNAS documentation for the exact release on the system; docs are versioned by
release, and menus, feature names, and API behavior change between them. Re-verify links and contents
when updating this skill; record the date checked.

Last verified: 2026-10-31

## Vendor (authoritative)

- Security recommendations (ports table, SSH, SMB, NFS, iSCSI, apps, logging):
  https://www.truenas.com/docs/solutions/optimizations/security/
- Software status (which releases are maintained and recommended): https://www.truenas.com/compare/
- Security advisories (per product line, including CORE and TrueNAS Connect) and hardening summary:
  https://security.truenas.com/. Release notes for the installed version, under https://www.truenas.com/docs/,
  list security fixes.
- API keys (user-linked keys, HTTPS required, automatic revocation over HTTP; 25.10 docs):
  https://www.truenas.com/docs/scale/25.10/scaletutorials/toptoolbar/managingapikeys/
- API documentation (JSON-RPC over WebSocket; REST API deprecated): https://www.truenas.com/docs/scale/25.10/api/
- Global network configuration (hostname, mDNS, WS-Discovery, NetBIOS):
  https://www.truenas.com/docs/scale/network/networkconfiguration/globalconfigurationscreens/
- Containers and VMs in 25.10 (experimental containers, VM migration notes):
  https://www.truenas.com/docs/scale/25.10/scaletutorials/containers/
- Release plans and naming (2026 plans; the release previewed as 26 renumbered as 27):
  https://www.truenas.com/blog/truenas-plans-for-2026 and https://www.truenas.com/blog/truenas-27-is-here/
- TrueNAS CORE documentation (legacy): https://www.truenas.com/docs/core/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- endoflife.date, TrueNAS: https://endoflife.date/truenas. Useful summary of release dates and CORE's
  maintenance status; it lags the vendor and the vendor's support policy isn't formally documented, so
  confirm on the software-status page.
- TrueNAS community forums (https://forums.truenas.com/) were used only to confirm feature changes
  between releases (discovery behavior, Incus VM migration); treat forum posts as observations, not
  documentation.
