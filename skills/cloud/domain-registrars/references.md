# Domain Registrars: References

Always prefer current registrar, registry, and ICANN documentation. Policies (transfer rules, grace
periods, API eligibility) and dashboard menus change. Re-verify links and contents when updating this
skill.

Last verified: 2026-10-31

## Policy and standards (authoritative)

- ICANN EPP status codes (what `clientTransferProhibited` and the others mean):
  https://www.icann.org/resources/pages/epp-status-codes-2014-06-16-en
- ICANN: launching RDAP and sunsetting WHOIS for gTLDs (January 2025):
  https://www.icann.org/en/announcements/details/icann-update-launching-rdap-sunsetting-whois-27-01-2025-en
- ICANN Transfer Policy (check the current version and any pending revisions):
  https://www.icann.org/resources/pages/transfer-policy-2016-06-01-en
- ICANN Transfer Dispute Resolution Policy:
  https://www.icann.org/resources/pages/tdrp-2016-06-01-en
- ICANN Expired Registration Recovery Policy:
  https://www.icann.org/resources/pages/errp-2013-02-28-en
- ICANN SSAC SAC007, domain name hijacking incidents, threats, risks, and remedial actions (older, but
  still the reference on registrar lock and transfer abuse):
  https://www.icann.org/en/ssac/publications/documents/sac007-executive-summary-for-domain-name-hijacking-incidents-threats-risks-and-remedial-actions-12-07-2005-en
- DNS CAA (RFC 8659): https://www.rfc-editor.org/rfc/rfc8659
- Automating DNSSEC delegation trust maintenance with CDS/CDNSKEY (RFC 7344, RFC 8078):
  https://www.rfc-editor.org/rfc/rfc7344 and https://www.rfc-editor.org/rfc/rfc8078
- Null MX (RFC 7505): https://www.rfc-editor.org/rfc/rfc7505

## Vendor (authoritative): registrars

- Namecheap two-factor authentication: https://www.namecheap.com/support/knowledgebase/article.aspx/9253/45/how-can-i-enable-twofactor-authentication-for-my-namecheap-account/
- Namecheap domain privacy (Withheld for Privacy): https://www.namecheap.com/security/domain-privacy/
- Namecheap API access (eligibility and IP whitelist): https://www.namecheap.com/support/api/intro/
- GoDaddy account security and 2-step verification: https://www.godaddy.com/help/enable-2-step-verification-7502
- GoDaddy developer API access (eligibility): https://developer.godaddy.com/getstarted
- Cloudflare Registrar: https://developers.cloudflare.com/registrar/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- "Can I take over XYZ?" (community list of services vulnerable to subdomain takeover):
  https://github.com/EdOverflow/can-i-take-over-xyz. Useful to classify a dangling record; entries change
  as providers fix issues, so confirm with the provider's documentation.
- crt.sh (certificate transparency search): https://crt.sh/. Useful for finding subdomains and
  unexpected certificates.
- rdap.org (RDAP bootstrap redirector): https://rdap.org/. Redirects lookups to the right registry RDAP
  server.
- KrebsOnSecurity, "Researchers: Weak Security Defaults Enabled Squarespace Domains Hijacks" (2024):
  https://krebsonsecurity.com/2024/07/researchers-weak-security-defaults-enabled-squarespace-domains-hijacks/.
  Background on registrar migrations as a risk.
