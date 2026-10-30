# Windows: References

Always prefer current Microsoft documentation; lifecycle dates, defaults, and feature availability change
between Windows releases and editions.

Last verified: 2026-10-30

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

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Government and industry guidance

- CISA AA23-025A, Protecting Against Malicious Use of Remote Monitoring and Management Software:
  https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-025a
  Explains how attackers use legitimate remote-access tools (including portable versions) for persistence
  and scams, with detection advice.

## Third-party (not authoritative)

- CIS Benchmarks for Microsoft Windows (free registration): https://www.cisecurity.org/benchmark/microsoft_windows_desktop
  Detailed configuration baselines, written mainly for managed enterprise fleets. Many settings are too
  strict or irrelevant for home PCs; apply selectively and check against current Microsoft defaults.
