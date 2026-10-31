# Windows: References

Always prefer current Microsoft documentation; lifecycle dates, defaults, and feature availability change
between Windows releases and editions.

Last verified: 2026-10-31

## Vendor (authoritative)

- Security Update Guide (advisories, monthly security updates): https://msrc.microsoft.com/update-guide
- Microsoft Security Response Center blog: https://msrc.microsoft.com/blog/
- Windows 11 release information (versions, builds, end-of-updates dates per edition):
  https://learn.microsoft.com/en-us/windows/release-health/windows11-release-information
- Windows 10 release information: https://learn.microsoft.com/en-us/windows/release-health/release-information
- Windows Server release information (mainstream and extended support dates):
  https://learn.microsoft.com/en-us/windows-server/get-started/windows-server-release-info
- Windows release health (known issues): https://learn.microsoft.com/en-us/windows/release-health/
- Windows lifecycle FAQ: https://learn.microsoft.com/en-us/lifecycle/faq/windows
- Windows 10 Extended Security Updates (commercial):
  https://learn.microsoft.com/en-us/windows/whats-new/extended-security-updates
- Windows 10 consumer ESU: https://www.microsoft.com/en-us/windows/extended-security-updates
- Windows 10 end of support: https://www.microsoft.com/en-us/windows/end-of-support
- Windows security documentation (overview): https://learn.microsoft.com/en-us/windows/security/
- BitLocker overview and device encryption:
  https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/
- Finding a BitLocker recovery key (consumer): https://support.microsoft.com/en-us/windows/find-your-bitlocker-recovery-key-6b71ad27-0b89-ea08-f143-056f5ab347d6
- Tamper protection: https://learn.microsoft.com/en-us/defender-endpoint/prevent-changes-to-security-settings-with-tamper-protection
- Attack surface reduction rules reference:
  https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-reference
- Controlled folder access: https://learn.microsoft.com/en-us/defender-endpoint/controlled-folders
- Microsoft Defender Antivirus compatibility (active/passive modes):
  https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-antivirus-compatibility
- Smart App Control FAQ: https://support.microsoft.com/en-us/windows/smart-app-control-frequently-asked-questions-285ea03d-fa88-4d56-882e-6698afdb7003
- Windows LAPS overview: https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview
- Detect, enable, and disable SMBv1/v2/v3 (also SMB signing defaults):
  https://learn.microsoft.com/en-us/windows-server/storage/file-server/troubleshoot/detect-enable-and-disable-smbv1-v2-v3
- Control SMB signing behavior: https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing
- PowerShell logging on Windows (PowerShell 7): https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows
- Windows PowerShell 5.1 logging: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging?view=powershell-5.1
- LSA protection: https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection
- Credential Guard: https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard
- Windows Secure Boot certificate expiration and CA updates:
  https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e
- Microsoft account security (two-step verification, recovery info, sign-in activity):
  https://support.microsoft.com/en-us/account-billing/how-to-use-two-step-verification-with-your-microsoft-account-c7910146-672f-01e9-50a0-93b4585e7eb4
- Microsoft Sysinternals Autoruns (persistence review): https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns

### Active Directory domain controllers

- Best practices for securing Active Directory (larger estates; read for principles):
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory
- Enterprise access model (successor to the AD tier model): https://learn.microsoft.com/en-us/security/compass/privileged-access-access-model
- Privileged access overview: https://learn.microsoft.com/en-us/security/zero-trust/security-concept-privileged-access
- Protected Users security group:
  https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group
- Windows LAPS architecture (AD password encryption, DSRM password backup):
  https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-concepts-overview
- AD forest recovery guide: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide
- AD forest recovery prerequisites: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-prerequisites
- Reset the krbtgt password (twice, at least the maximum ticket lifetime apart):
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- LDAP signing (defaults by Windows Server version, events 2886–2889):
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-signing
- LDAP channel binding (defaults, `LdapEnforceChannelBinding`, events 3039–3041 and 3074–3075):
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-channel-binding
- LDAP channel binding and signing requirements history (KB4520412):
  https://support.microsoft.com/topic/2020-2023-and-2024-ldap-channel-binding-and-ldap-signing-requirements-for-windows-kb4520412-ef185fb8-00f7-167d-744c-f299a66fc00a
- ADV190023, guidance for enabling LDAP channel binding and signing: https://msrc.microsoft.com/update-guide/advisory/ADV190023
- Kerberos KDC RC4 changes for CVE-2026-20833 (KB5073381; phases and KDCSVC events):
  https://support.microsoft.com/en-us/kb/5073381
- Advancing Windows security: disabling NTLM by default (Windows IT Pro blog, January 2026):
  https://techcommunity.microsoft.com/blog/windows-itpro-blog/advancing-windows-security-disabling-ntlm-by-default/4489526
- Group managed service accounts:
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/manage-group-managed-service-accounts
- Delegated managed service accounts FAQ (Windows Server 2025):
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/delegated-managed-service-accounts/delegated-managed-service-accounts-faq
- Microsoft Security Compliance Toolkit (security baselines for GPOs):
  https://learn.microsoft.com/en-us/windows/security/operating-system-security/device-management/windows-security-configuration-framework/security-compliance-toolkit-10
- Virtualized domain controller architecture (VM-GenerationID, snapshot safety):
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/virtualized-domain-controller-architecture
- Active Directory: automate system state backup (archived TechNet Wiki; `wbadmin start systemstatebackup`):
  https://learn.microsoft.com/en-us/archive/technet-wiki/51272.active-directory-automate-system-state-backup

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Government and industry guidance

- CISA AA23-025A, Protecting Against Malicious Use of Remote Monitoring and Management Software:
  https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-025a
  Explains how attackers use legitimate remote-access tools (including portable versions) for persistence
  and scams, with detection advice.
- CISA countermeasure CM0050, reset the krbtgt password twice: https://www.cisa.gov/eviction-strategies-tool/info-countermeasures/CM0050

## Third-party (not authoritative)

- CIS Benchmarks for Microsoft Windows (free registration): https://www.cisecurity.org/benchmark/microsoft_windows_desktop
  Detailed configuration baselines, written mainly for managed enterprise fleets. Many settings are too
  strict or irrelevant for home PCs; apply selectively and check against current Microsoft defaults.
