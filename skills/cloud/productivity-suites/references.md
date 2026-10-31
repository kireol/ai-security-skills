# Microsoft 365 and Google Workspace: References

Always prefer current vendor documentation. Admin console names, licensing, and retirement dates change
often. Re-verify links and contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative): Microsoft

- Security defaults in Microsoft Entra ID (what they enable, legacy authentication block):
  https://learn.microsoft.com/entra/fundamentals/security-defaults
- Block legacy authentication with Conditional Access:
  https://learn.microsoft.com/entra/identity/conditional-access/policy-block-legacy-authentication
- Mandatory multifactor authentication for Azure and admin portals:
  https://learn.microsoft.com/entra/identity/authentication/concept-mandatory-multifactor-authentication
- Manage emergency access (break-glass) accounts:
  https://learn.microsoft.com/entra/identity/role-based-access-control/security-emergency-access
- Control automatic external email forwarding (outbound spam policy):
  https://learn.microsoft.com/defender-office-365/outbound-spam-policies-external-email-forwarding
- SMTP AUTH basic authentication retirement: check the current Exchange Team blog and Message Center
  entry MC786329 (the date has moved more than once): https://techcommunity.microsoft.com/category/exchange/blog/exchange
- Microsoft Graph PowerShell and Exchange Online PowerShell module documentation:
  https://learn.microsoft.com/powershell/microsoftgraph/ and https://learn.microsoft.com/powershell/exchange/
- Responding to a compromised email account:
  https://learn.microsoft.com/defender-office-365/responding-to-a-compromised-email-account
- Detect and remediate illicit consent grants:
  https://learn.microsoft.com/defender-office-365/detect-and-remediate-illicit-consent-grants
- Configure how users consent to applications:
  https://learn.microsoft.com/entra/identity/enterprise-apps/configure-user-consent
- Email authentication (SPF, DKIM, DMARC) in Microsoft 365:
  https://learn.microsoft.com/defender-office-365/email-authentication-about
- Microsoft account security (consumer):
  https://support.microsoft.com/account-billing/how-to-help-keep-your-microsoft-account-safe-and-secure-628538c2-7006-33bb-5ef4-c917657362b9

## Vendor (authoritative): Google

- Security best practices for administrator accounts:
  https://knowledge.workspace.google.com/admin/users/security-best-practices-for-administrator-accounts
- Super administrator account best practices (Google Cloud):
  https://docs.cloud.google.com/resource-manager/docs/super-admin-best-practices
- Deploy and enforce 2-Step Verification: https://support.google.com/a/answer/9176657
- Transition from less secure apps to OAuth:
  https://knowledge.workspace.google.com/admin/sync/transition-from-less-secure-apps-to-oauth
- Control which third-party and internal apps access Workspace data (API controls):
  https://support.google.com/a/answer/7281227
- Gmail automatic forwarding setting: https://support.google.com/a/answer/2491924
- Set up DKIM: https://support.google.com/a/answer/174124
- Email sender guidelines (SPF, DKIM, DMARC requirements): https://support.google.com/a/answer/81126
- Alert center (viewing alert details): https://support.google.com/a/answer/9104586
- Google Account Security Checkup (consumer): https://myaccount.google.com/security-checkup

## Standards and generic guidance

- DMARC (RFC 7489): https://www.rfc-editor.org/rfc/rfc7489
- Null MX (RFC 7505): https://www.rfc-editor.org/rfc/rfc7505
- CISA guidance on business email compromise and Microsoft 365 / Google Workspace secure configuration
  baselines (SCuBA): https://www.cisa.gov/resources-tools/services/secure-cloud-business-applications-scuba-project

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- CIS Microsoft 365 Foundations Benchmark and CIS Google Workspace Foundations Benchmark
  (https://www.cisecurity.org/benchmark): useful checklists; their control numbering and defaults lag the
  live products, so verify each against vendor documentation.
- GAM (open-source Google Workspace admin CLI): powerful but needs a Cloud project, OAuth client, and
  often domain-wide delegation. Treat installation and setup as a change and review its scopes first.
