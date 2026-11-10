# Synology DSM: References

Always prefer current Synology documentation for exact DSM behavior and builds. Re-verify links and
contents when updating this skill; record the date checked.

Last verified: 2026-11-10 (all links resolve; the two Control Panel help pages below were re-read)

## Vendor (authoritative)

- Security recommendations: https://kb.synology.com/en-us/DSM/tutorial/How_to_add_extra_security_to_your_Synology_NAS
- Security Advisor: https://kb.synology.com/en-global/DSM/help/DSM/SecurityScan/securityscan_desc?version=7
- Control Panel → Security → Account (2-factor enforcement and what it breaks, Adaptive MFA, Account
  Protection): https://kb.synology.com/en-global/DSM/help/DSM/AdminCenter/connection_security_account?version=7
- Control Panel → Security → Security (session settings, Trusted Proxies):
  https://kb.synology.com/en-global/DSM/help/DSM/AdminCenter/connection_security_security?version=7
- Product support status (which models still receive updates): https://www.synology.com/en-global/products/status
- Product Security Advisories: https://www.synology.com/en-global/security/advisory
- DSM release notes: https://www.synology.com/en-global/releaseNote/DSM
- Downloads and model-specific support: https://www.synology.com/en-global/support/download
- DSM Administration CLI Guide (legacy; validate every command against the target build):
  https://global.download.synology.com/download/Document/Software/DeveloperGuide/Firmware/DSM/All/enu/Synology_DiskStation_Administration_CLI_Guide.pdf

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

Reviewed when preparing v3.0. Treat as operational references only (see the core tool-use contract).

- iuliandita/skills, `skills/synology-dsm`: https://github.com/iuliandita/skills/tree/main/skills/synology-dsm
  Useful DSM command-surface notes, shell/CLI caveats, package-dependency observations, and storage-recovery
  warnings. Its observations are tied to particular hardware and builds; its dated release and CVE
  statements must be revalidated. Its storage-recovery procedures are specialist material and are
  deliberately not reproduced here.
- atom2ueki/mcp-server-synology, `skills/synology-nas`: https://github.com/atom2ueki/mcp-server-synology/tree/main/skills/synology-nas
  Primarily an MCP tool-selection guide. Useful patterns: explicit multi-NAS targeting, session-state
  discovery, aggregate-first health checks, path validation, and inspect-before-mutate. Its tool names
  apply only when that exact server and version is installed.
