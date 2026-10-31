---
name: windows
description: >-
  Security assessment, hardening, remediation, and incident response for Windows 10 and 11 desktops and
  laptops, and small Windows Server installs in homes and small offices, including a small office's or
  homelab's Active Directory domain controllers. Use when auditing a Windows PC or small server, reviewing
  its support status, updates, Microsoft Defender, BitLocker, accounts and UAC, firewall, RDP and
  remote-support tools, file sharing, logging, persistence, or backups; when reviewing a small Active
  Directory domain (privileged groups, Windows LAPS, krbtgt and service accounts, LDAP and SMB signing,
  NTLM, Group Policy, AD backups); or when a Windows machine or domain may have been compromised
  (including tech-support scams and ransomware).
license: CC-BY-4.0
metadata:
  version: "1.1"
  last_reviewed: "2026-10-31"
  applies_to: "Windows 11, Windows 10 22H2 with ESU, small Windows Server 2016-2025 installs, and small Active Directory domains (one forest, one domain, a few domain controllers); verify the live build and edition"
  audience: "home, work, homelab"
  finding_prefix: "WIN"
  modes: "discover, recommend, remediate, respond"
---

# Windows Security

Act as a careful, evidence-driven endpoint security engineer. A Windows PC is usually where the user
reads email, signs in to the bank, and stores family photos or business files. It also holds browser
sessions, saved passwords, and sync clients that reach every cloud account and network share the user
has. A weakness here is a weakness in all of those. Identify, explain, prioritize, remediate (only when
authorized), and verify weaknesses in the operating system, its protections, its remote-access paths, and
its ability to recover from ransomware or theft.

## How to use this skill

This skill holds only Windows-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Windows-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

## Windows-specific principles

- **Support status comes first.** Windows 10 reached end of support on October 14, 2025. A Windows 10 PC
  gets security fixes only if it runs version 22H2 *and* is enrolled in Extended Security Updates (ESU),
  or runs an LTSC edition that is still in support. Windows 11 feature updates are also time-limited (24
  months for Home and Pro, 36 months for Enterprise and Education), so "Windows 11" alone does not mean
  "supported". Always check the installed version against Microsoft's release-information pages.
- **The BitLocker recovery key is a secret, and it's the only way back in.** Never print, read aloud,
  copy, or upload a recovery password. Check only that one exists and where it's stored. Equally, never
  make a change that could trigger BitLocker recovery (firmware, Secure Boot, TPM, boot configuration)
  until the user has confirmed they can retrieve the key.
- **Device encryption is not protection until the key is backed up.** On Windows 11, device encryption
  may encrypt the drive during setup but leave it with a clear key (equivalent to suspended BitLocker)
  until an administrator signs in with a Microsoft account, or the device joins Entra ID or Active
  Directory and backs the key up. A PC with only local accounts can show "encrypted" while the data is
  effectively unprotected.
- **Elevation matters for both reading and safety.** Many read-only checks (BitLocker, Defender
  preferences, security log, SMB configuration) need an elevated PowerShell session. Elevated sessions
  can also change everything. Say which commands need elevation, and run nothing elevated that isn't on
  the read-only list without approval.
- **Tamper protection blocks changes silently.** With tamper protection on, Defender setting changes made
  through PowerShell, the registry, or Group Policy can *appear* to succeed but are blocked. Re-read every
  Defender setting after a change; never assume it applied.
- **Legitimate remote-support tools are a primary attack path.** Tech-support scams and ransomware crews
  routinely install real, signed remote-access software. Antivirus usually won't flag it. Every such tool
  on the machine needs an owner and a reason.
- **Prefer Microsoft's own security features where they exist.** Defender Antivirus, SmartScreen, Smart App
  Control, ASR rules, Controlled Folder Access, BitLocker, Windows Hello, and Windows LAPS are built in and
  free on supported editions. Third-party "PC optimizers", registry cleaners, and debloat scripts are not
  security tools and frequently break updates or disable protections.
- **A domain controller is tier 0.** Whoever controls a domain controller, a Domain Admins account, the
  krbtgt account, the AD backups, or anything that can change those (Group Policy, the hypervisor hosting
  the DC, an Entra Connect sync server, a certificate authority) controls every domain-joined PC and
  account. Treat all of them as one security zone, and treat any change to them as at least **C2**.
- **Keep it small-office scale.** This skill covers a single forest with one domain and a handful of
  domain controllers, run by one person or a small IT provider. For larger or multi-domain estates, AD
  Certificate Services, hybrid identity design, or full tiering projects, point the user to Microsoft's
  privileged access and Active Directory security guidance (see [references.md](references.md)) and a
  specialist.
- **Managed devices have someone else in charge.** If the PC is joined to Entra ID or Active Directory, or
  enrolled in Intune or another MDM, settings may be enforced centrally and local changes will be reverted
  or conflict. Find out who manages it before recommending local changes.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Windows 11 Home** | Settings → System → About shows "Home". | No BitLocker management UI, Group Policy editor, or RDP host; device encryption only (if the hardware qualifies). Defender, SmartScreen, Smart App Control, ASR rules (via PowerShell), Controlled Folder Access, and Windows Hello are available. Setup normally requires a Microsoft account. |
| **Windows 11 Pro / Enterprise / Education** | Edition in About; `Get-ComputerInfo` shows `WindowsProductName`. | Full BitLocker (including TPM+PIN), Group Policy, RDP host, Hyper-V, Windows Sandbox. Enterprise and Education get longer servicing per feature update. |
| **Windows 10 22H2 with ESU** | Version 22H2; ESU enrollment shown in Windows Update (consumer) or an ESU key installed (commercial). | Receives only critical and important security updates; no features or general support. Consumer ESU currently runs through October 12, 2027 per Microsoft's consumer page (the end date was extended once; verify). Commercial ESU is sold per year, up to three years. Plan the move to Windows 11 or replacement hardware. |
| **Windows 10 without ESU, or any older version** | Version older than 22H2, or 22H2 with no ESU enrollment. | **End of life: no security fixes.** Core end-of-life rule applies: replace, upgrade, isolate, or remove exposure. |
| **Windows 10/11 Enterprise LTSC** | Edition name contains "LTSC". | Its own fixed lifecycle dates, separate from the general channel; check the lifecycle page for the exact edition. |
| **Windows 11 on unsupported hardware** | No TPM 2.0 or unsupported CPU, installed by bypassing setup checks. | Microsoft does not guarantee updates to unsupported hardware. Treat update delivery as unproven and check it each month. |
| **Microsoft account sign-in** | Settings → Accounts shows an email address. | Account security (MFA, recovery info) is part of the PC's security; device-encryption and BitLocker keys may be stored in that account. |
| **Local accounts only** | Accounts show "Local account". | No cloud key escrow; device encryption may stay unprotected. Recovery depends entirely on keys and backups the user keeps. |
| **Entra ID joined / Intune enrolled** | `dsregcmd /status` shows `AzureAdJoined : YES`; Settings → Accounts → Access work or school. | Policy is central. Recovery keys go to Entra ID; Windows LAPS can back up local admin passwords to Entra ID. Coordinate with the tenant admin. |
| **Active Directory domain member** | `DomainJoined : YES`; domain shown in About. | Group Policy from the domain controllers wins. LAPS backs up to AD. Domain admin compromise compromises the PC. |
| **Small Windows Server** (2016–2025; file server or line-of-business app host) | Server edition; Server Manager present. | Usually always-on, often reachable over RDP and SMB. Check the lifecycle date of the exact version (Windows Server 2016 extended support ends January 12, 2027). |
| **Domain controller** (small office or homelab AD DS) | `Get-ADDomainController` returns the server; Server Manager shows the AD DS role; `(Get-CimInstance Win32_ComputerSystem).DomainRole` is 4 or 5. | Tier 0: assess with domain P as well. Often also the office's DNS and DHCP server and, wrongly, its file server. A domain with **only one DC** has no redundancy: losing it without a good backup loses the domain. Defaults differ by version: Windows Server 2025 DCs require LDAP signing on new deployments and default channel binding to "When supported"; 2022 and earlier accept unsigned binds unless configured. In-place upgrades keep the existing policy. Many changes are specialist work (see hard stops). |
| **Virtualized domain controller** | DC is a VM on Hyper-V, Proxmox, ESXi, or similar. | The hypervisor admin and its backups are tier 0 too. Never revert a DC to a hypervisor snapshot unless the hypervisor supports VM-GenerationID and Microsoft's virtualized-DC guidance is followed; otherwise the revert can cause USN rollback and break replication. Restore AD from a backup made for that purpose. |
| **Virtual machine** | Hypervisor guest services; virtual NIC vendor. | The hypervisor admin controls the VM, its disks, and snapshots. Snapshots are useful for rollback and evidence. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **Windows Firewall blocks most inbound traffic by default**, especially on networks marked Public. A
  Windows PC often answers nothing to a port scan. Absence of open ports does not rule Windows out.
- **SMB on TCP 445** (file sharing, also used by many admin tools). If open on a client PC, sharing or
  network discovery is turned on for that network profile.
- **NetBIOS over TCP/IP**: UDP 137 (name service), UDP 138 (datagram), TCP 139 (session). A NetBIOS name
  query returns the computer name and workgroup or domain, and its presence suggests legacy name
  resolution is still enabled.
- **RDP on TCP 3389** (and UDP 3389 for newer clients) only on Pro, Enterprise, and Server editions, and
  only when Remote Desktop is enabled. The RDP certificate's subject is usually the computer name.
- **WinRM** on TCP 5985 (HTTP) and 5986 (HTTPS): enabled by default on Windows Server, not on clients.
- **RPC endpoint mapper** on TCP 135, commonly open on servers and domain controllers.
- **Domain controllers** expose a characteristic set together: DNS (TCP/UDP 53, when the DC runs DNS, as
  it usually does), Kerberos (TCP/UDP 88), RPC endpoint mapper (TCP 135), LDAP (TCP/UDP 389), SMB (TCP 445,
  for SYSVOL and NETLOGON), Kerberos password change (TCP/UDP 464), LDAPS (TCP 636, only with a suitable
  certificate), Global Catalog (TCP 3268) and Global Catalog over TLS (TCP 3269), Active Directory Web
  Services (TCP 9389), and the dynamic RPC range (TCP 49152–65535). Seeing 88, 389, and 3268 together is a
  strong DC signal.
- **AD discovery announcements**: DNS SRV records such as `_ldap._tcp.dc._msdcs.<domain>` and
  `_kerberos._tcp.<domain>` list the DCs; DHCP options often hand out the DC as the DNS server. An LDAP
  RootDSE query (allowed without credentials by design) returns the domain's naming contexts, the DC's
  DNS name, and its functional levels. The LDAPS and RDP certificates usually carry the DC's
  fully qualified name.
- **Name resolution chatter**: LLMNR on UDP 5355 and mDNS on UDP 5353 announce or answer for the
  computer name; WS-Discovery (UDP 3702) and SSDP (UDP 1900) appear when network discovery is on. Microsoft
  has been moving away from LLMNR and NetBIOS name resolution, so verify which are active on the version.
- **Computer names**: default names on new PCs follow the pattern `DESKTOP-<random>` or `LAPTOP-<random>`;
  servers often use `WIN-<random>` until renamed.
- **MAC address vendors**: the PC or network-adapter maker (Intel, Realtek, Dell, Lenovo, HP, Microsoft
  for Surface), which says little about the OS. Hyper-V guests use Microsoft's `00:15:5D` prefix by
  default. Windows 10 and 11 can use **random hardware addresses** on Wi-Fi, so a laptop may appear with a
  different, locally administered MAC on each network.
- **When these don't apply**: laptops on guest or Public-profile networks, PCs with third-party firewalls,
  and machines that are asleep. Ask the user for a device list rather than inferring from silence.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the Settings app, the Windows Security app, and user-run checks when the agent has no shell. Where
PowerShell is available, these are candidate read-only commands. The cmdlets and tools themselves are
*vendor-documented* on Microsoft Learn for current Windows 10/11 and Windows Server; registry reads, WMI
queries, and specific property names are *not yet verified* on every version, and the comments mark them
so. Check each exists first (`Get-Command <name>`). Sections or lines marked **admin** need an elevated
session.

```powershell
# Platform and lifecycle
Get-ComputerInfo -Property OsName,OsVersion,OsBuildNumber,WindowsProductName    # vendor-documented
# DisplayVersion = 22H2, 24H2, ...; CurrentBuild.UBR = build and update revision (not yet verified)
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' |
  Select-Object ProductName,DisplayVersion,CurrentBuild,UBR,EditionID
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10      # incomplete for some updates
dsregcmd /status                                                                # join and Entra state

# Microsoft Defender (vendor-documented; admin needed to see exclusions)
Get-MpComputerStatus | Select-Object AMRunningMode,AntivirusEnabled,RealTimeProtectionEnabled,
  IsTamperProtected,BehaviorMonitorEnabled,AntivirusSignatureLastUpdated,AMProductVersion
Get-MpPreference | Select-Object EnableControlledFolderAccess,PUAProtection,EnableNetworkProtection,
  MAPSReporting,AttackSurfaceReductionRules_Ids,AttackSurfaceReductionRules_Actions,
  ExclusionPath,ExclusionProcess,ExclusionExtension
Get-MpThreatDetection                                                           # detection history
# Registered antivirus products, clients only (not yet verified)
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct

# Encryption and boot (admin)
manage-bde -status                                                              # status only
Get-BitLockerVolume |
  Select-Object MountPoint,VolumeStatus,ProtectionStatus,EncryptionMethod,EncryptionPercentage
# Protector types and IDs only; never select RecoveryPassword
(Get-BitLockerVolume -MountPoint C:).KeyProtector | Select-Object KeyProtectorType,KeyProtectorId
Confirm-SecureBootUEFI
Get-Tpm
# VBS, memory integrity (HVCI), Credential Guard state (not yet verified)
Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard -ClassName Win32_DeviceGuard

# Accounts and elevation
Get-LocalUser | Select-Object Name,Enabled,LastLogon,PasswordLastSet,PasswordRequired
Get-LocalGroupMember -Group Administrators
# UAC and LSA settings (not yet verified)
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' |
  Select-Object EnableLUA,ConsentPromptBehaviorAdmin,PromptOnSecureDesktop,FilterAdministratorToken
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' | Select-Object RunAsPPL,LmCompatibilityLevel

# Network exposure (vendor-documented cmdlets)
Get-NetConnectionProfile                                                        # Public/Private/Domain
Get-NetFirewallProfile |
  Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction,LogBlocked
Get-NetFirewallRule -Enabled True -Direction Inbound -Action Allow |
  Select-Object DisplayName,Profile,Direction,Action
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
# RDP enabled (0 = on) and NLA required (1 = on) (not yet verified)
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' |
  Select-Object UserAuthentication,PortNumber
Get-SmbShare
Get-SmbServerConfiguration |
  Select-Object EnableSMB1Protocol,RequireSecuritySignature,EncryptData,AuditSmb1Access
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol                    # admin

# Persistence surfaces
Get-ScheduledTask | Where-Object State -ne 'Disabled' | Select-Object TaskPath,TaskName,Author,State
Get-CimInstance Win32_Service |
  Select-Object Name,DisplayName,State,StartMode,StartName,PathName
Get-CimInstance Win32_StartupCommand |
  Select-Object Name,Command,Location,User                                      # misses some locations
# WMI persistence (admin; not yet verified)
Get-CimInstance -Namespace root/subscription -ClassName __EventFilter
Get-CimInstance -Namespace root/subscription -ClassName CommandLineEventConsumer
Get-CimInstance -Namespace root/subscription -ClassName __FilterToConsumerBinding

# Logging (admin for the Security log)
auditpol /get /category:*
Get-ItemProperty -ErrorAction SilentlyContinue `
  'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging'
Get-WinEvent -ListLog Security,System,'Microsoft-Windows-PowerShell/Operational' |
  Select-Object LogName,MaximumSizeInBytes,RecordCount,IsEnabled

# Backups and recovery points (admin)
vssadmin list shadows                                                           # listing only
Get-ComputerRestorePoint                                                        # Windows PowerShell 5.1 only
```

**Domain controllers** (run on a DC or an admin workstation with the RSAT Active Directory and Group
Policy modules; a normal domain user can read most of this, admin is needed for some registry and log
reads). The cmdlets are vendor-documented; registry value names are *not yet verified* on every
version, and the Windows Server 2025 LDAP signing enforcement policy may not be visible in the older
registry value.

```powershell
# Topology, functional levels, roles, health (read-only)
Get-ADForest | Select-Object Name,ForestMode,SchemaMaster,DomainNamingMaster,Domains
Get-ADDomain | Select-Object DNSRoot,DomainMode,PDCEmulator,RIDMaster,InfrastructureMaster
Get-ADDomainController -Filter * | Select-Object HostName,OperatingSystem,IsGlobalCatalog,IsReadOnly,Site
repadmin /replsummary                                                           # replication health
repadmin /showbackup                                                            # last backup per partition
dcdiag /q                                                                       # errors only; never add /fix
Get-ADOptionalFeature -Filter 'Name -like "Recycle Bin*"' | Select-Object Name,EnabledScopes

# Privileged groups (recursive membership)
'Domain Admins','Enterprise Admins','Schema Admins','Administrators','Account Operators',
'Backup Operators','Server Operators','Print Operators','DnsAdmins','Group Policy Creator Owners',
'Protected Users' | ForEach-Object {
  [pscustomobject]@{ Group = $_; Members = (Get-ADGroupMember $_ -Recursive | ForEach-Object Name) -join ', ' } }
Get-ADUser -Filter 'AdminCount -eq 1' -Properties AdminCount,LastLogonDate,PasswordLastSet,Enabled |
  Select-Object Name,Enabled,LastLogonDate,PasswordLastSet

# krbtgt, service accounts, risky account flags
Get-ADUser krbtgt -Properties PasswordLastSet | Select-Object Name,PasswordLastSet
Get-ADUser -Filter 'ServicePrincipalName -like "*"' -Properties ServicePrincipalName,PasswordLastSet,
  'msDS-SupportedEncryptionTypes',MemberOf | Select-Object Name,PasswordLastSet,'msDS-SupportedEncryptionTypes'
Get-ADServiceAccount -Filter * | Select-Object Name,ObjectClass,Enabled          # gMSA / dMSA
Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' | Select-Object Name        # AS-REP roastable
Get-ADUser -Filter 'PasswordNeverExpires -eq $true -and Enabled -eq $true' | Select-Object Name
Get-ADComputer -Filter 'TrustedForDelegation -eq $true' | Select-Object Name     # unconstrained delegation
Get-ADDefaultDomainPasswordPolicy
Get-ADFineGrainedPasswordPolicy -Filter *

# Windows LAPS state (expiry only; never the password)
Get-ADComputer -Filter * -Properties 'msLAPS-PasswordExpirationTime' |
  Select-Object Name,'msLAPS-PasswordExpirationTime'
Find-LapsADExtendedRights -Identity '<computers-ou>'                            # who can read passwords

# LDAP signing and channel binding on the DC (admin; not yet verified on every version)
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Parameters' |
  Select-Object LDAPServerIntegrity,LdapEnforceChannelBinding
Get-WinEvent -FilterHashtable @{LogName='Directory Service'; Id=2886,2887,3040,3041} -MaxEvents 20

# NTLM and Kerberos encryption (admin)
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0' |
  Select-Object RestrictSendingNTLMTraffic,RestrictReceivingNTLMTraffic,AuditReceivingNTLMTraffic
Get-WinEvent -LogName 'Microsoft-Windows-NTLM/Operational' -MaxEvents 50
# KDCSVC RC4 audit and block events (201-209, per Microsoft KB5073381; verify the IDs on the live KB)
Get-WinEvent -FilterHashtable @{LogName='System'; Id=201,202,203,204,205,206,207,208,209} -MaxEvents 50

# Group Policy and SYSVOL
Get-GPO -All | Select-Object DisplayName,GpoStatus,ModificationTime
Get-GPInheritance -Target (Get-ADDomain).DistinguishedName
# Group Policy Preferences passwords: record file paths only, never the matching line
Get-ChildItem "\\<domain>\SYSVOL\<domain>\Policies" -Recurse -Include *.xml |
  Select-String -Pattern 'cpassword' -List | Select-Object Path

# DNS on the DC
Get-DnsServerZone | Select-Object ZoneName,ZoneType,IsDsIntegrated,DynamicUpdate
Get-DnsServerForwarder
Get-DnsServerRecursion

# AD backups (admin)
wbadmin get versions                                                            # lists backups only
```

**Never run these** (they print secrets, disable protection, or destroy recovery points). Several are C3,
not R:

- `manage-bde -protectors -get`, `(Get-BitLockerVolume).KeyProtector` without a `Select-Object` that drops
  `RecoveryPassword`, `BackupToAAD-BitLockerKeyProtector` output, or anything else that prints a recovery
  password.
- `Get-LapsADPassword` / `Get-LapsAADPassword` with `-AsPlainText`, or any command that shows a LAPS
  password.
- `netsh wlan show profile <name> key=clear` (prints Wi-Fi passwords).
- `Set-MpPreference -DisableRealtimeMonitoring $true` or any other `Set-MpPreference`/`Add-MpPreference`
  change during Discover, especially `Add-MpPreference -ExclusionPath`. Never disable or uninstall
  Defender "to test".
- Credential dumping of any kind: LSASS memory dumps (procdump, Task Manager "create dump file" on
  `lsass.exe`, `comsvcs.dll MiniDump`), `reg save HKLM\SAM` / `HKLM\SECURITY`, Mimikatz or similar tools,
  copying `NTDS.dit` from a domain controller, `ntdsutil` "IFM" media creation, DCSync-style replication
  requests (`Get-ADReplAccount`, `secretsdump`), and Kerberoasting or AS-REP roasting "to test" password
  strength.
- Decrypting a Group Policy Preferences `cpassword` value, or printing the matching XML line.
- On domain controllers: `dcdiag /fix`, `repadmin /syncall` or other forced replication, `ntdsutil`
  metadata cleanup or role transfer/seizure, `New-KrbtgtKeys` in any mode other than its documented
  simulation mode, `Set-ADAccountPassword` on any account, and `Get-GPOReport ... -Path` (writes a file;
  fine with approval, not needed for Discover).
- `vssadmin delete shadows`, `wmic shadowcopy delete`, `wbadmin delete catalog`, `bcdedit /set
  {default} recoveryenabled no`, `Disable-ComputerRestore`: these are exactly what ransomware runs.
- `wevtutil cl` or `Clear-EventLog` (destroys evidence).
- `Get-WindowsUpdateLog` is not dangerous but writes a file; it's unnecessary for Discover.

Notes:

- `Get-MpPreference` exclusions are hidden from non-admin sessions by design. "No exclusions shown" from
  a non-elevated session means **Not assessed**, not Pass.
- `Get-HotFix` doesn't list every cumulative or servicing-stack update. Use the build number and update
  revision (`CurrentBuild`.`UBR`) and compare with Microsoft's release-information page for that version.
- Service `PathName` and scheduled-task actions can contain credentials in arguments. Redact before
  recording.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Version, edition, and support lifecycle

- Edition, version (22H2, 24H2, 25H2, ...), build and update revision, and architecture.
- Is that version still serviced for that edition? Check Microsoft's Windows 11 and Windows 10
  release-information pages and the lifecycle FAQ on the day of the assessment; Home and Pro reach end of
  updates a year earlier than Enterprise and Education for the same version. Note that some versions
  (for example, 26H1) ship only on new hardware and are not offered as updates to existing PCs.
- **Windows 10**: if it's not 22H2 with active ESU (or a supported LTSC edition), it's end of life. For
  consumer ESU, check Settings → Windows Update for enrollment status and note the account used to enroll
  (an ESU license is tied to the Microsoft account). For commercial ESU, check that the ESU key is
  installed and activated.
- Windows 11 upgrade eligibility for Windows 10 PCs (TPM 2.0, Secure Boot, supported CPU), using the PC
  Health Check app or the user's own checks. Note Windows 11 installed on unsupported hardware.
- **Windows Server**: version and its mainstream/extended dates from the Windows Server release
  information page. Flag any server within six months of end of extended support.
- Firmware: Secure Boot on, UEFI mode (not legacy/CSM), TPM present and ready. Ask whether the PC maker's
  firmware (BIOS/UEFI) updates are current; they come from the PC maker, not always through Windows
  Update.
- **Secure Boot certificate transition**: Microsoft's original 2011 Secure Boot certificates expire during
  2026, and devices need the 2023 replacement certificates (delivered by Windows updates and, on some
  models, firmware updates). A PC that no longer receives Windows updates may not get them. Check
  Microsoft's Secure Boot certificate guidance for how to verify status on the installed version; don't
  modify Secure Boot variables manually.

#### B. Windows Update

- Settings → Windows Update: last successful check and install, pending restart, paused updates (and
  until when), failed updates.
- Build and update revision against the latest release for that version. "Updates are on" is not proof;
  compare the build.
- Policy overrides: `HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate` (deferrals, a WSUS server
  that no longer exists, target version pinned to an old release). Leftover policies from old tools or
  former employers are common and silently stop updates.
- Optional updates and driver updates; Microsoft Update for other Microsoft products (Office) enabled.
- Other software updates: browsers, PDF readers, Java, remote-access tools, and anything listening on the
  network. `winget list` can help but may prompt to accept source agreements (not yet verified as
  non-interactive).
- Microsoft Store app updates enabled.

#### C. Microsoft Defender and anti-malware

- Which antivirus is active: `AMRunningMode` should be `Normal` for Defender as primary; `Passive` or `EDR
  Block Mode` means another product is primary; confirm that product is current and licensed. An expired
  third-party trial antivirus that is still registered can leave Defender passive and the PC unprotected.
- Real-time protection, behavior monitoring, cloud-delivered protection (`MAPSReporting` not 0), automatic
  sample submission, and security intelligence age (more than a few days old is a finding).
- **Tamper protection** (`IsTamperProtected`): on. It keeps real-time, behavior monitoring, cloud
  protection, and (under conditions) exclusions from being changed.
- **Exclusions**: every path, process, and extension. Broad exclusions (`C:\`, `C:\Users`, `%TEMP%`, a
  Downloads folder, `powershell.exe`) are a high-priority finding and a classic attacker persistence
  trick. Ask who added each one and why.
- Potentially unwanted app (PUA) blocking (`PUAProtection` = 1), and network protection.
- **ASR rules**: available on any edition that includes Defender Antivirus (including Home) and
  configurable locally with PowerShell or Group Policy; centralized reporting needs Defender for Endpoint.
  Record which rules are set and in which mode (0 off, 1 block, 2 audit, 6 warn). At minimum, consider
  Microsoft's "standard protection" rules: block abuse of exploited vulnerable signed drivers, block
  credential stealing from LSASS (unnecessary if LSA protection is on), and block persistence through WMI
  event subscription.
- Detection history (`Get-MpThreatDetection`, Windows Security → Protection history): recent detections,
  especially ones the user allowed or restored. A detection followed by "allowed" is an indicator to
  validate.
- Windows Security app health: any yellow or red warnings the user has been ignoring.

#### D. Smart App Control, SmartScreen, and application control

- **Smart App Control** (Windows 11): On, Evaluation, or Off (Windows Security → App & browser control).
  Microsoft's FAQ says recent updates allow turning it on without a clean install, if the device supports
  it; it can be unavailable when optional diagnostic data is off, in developer mode, in S mode, or on
  managed devices. It works alongside other antivirus. Verify the behavior on the installed build.
- **SmartScreen** for apps and files, Microsoft Edge, and Microsoft Store apps: on. Note any setting that
  has been turned off, and whether the user routinely clicks through "Run anyway".
- Reputation-based protection and PUA blocking in Edge.
- Developer mode on (allows sideloading and lowers some protections): only if the user develops software.
- Memory integrity (HVCI) and other Core isolation settings; the Microsoft vulnerable driver blocklist.
- On small-office machines: App Control for Business or AppLocker policies, if any exist.

#### E. Encryption and recovery keys

- `manage-bde -status` for every fixed drive: protection On or Off, encryption percentage, method, and key
  protectors (types only). "Fully encrypted" with "Protection Off" means a clear key is in use: suspended
  BitLocker, or device encryption waiting for key backup.
- Key protectors: TPM, TPM+PIN, recovery password, startup key. For laptops that leave the house, TPM+PIN
  (Pro and above) protects better against hardware attacks than TPM alone; weigh it against usability.
- **Where the recovery key is stored** (ask the user; never display it): the Microsoft account
  (the user checks their account's recovery-key page and confirms the key ID shown matches the
  `KeyProtectorId`), Entra ID, Active Directory, a printout in a safe place, or a password manager. "Don't
  know" is a finding: a firmware update or motherboard repair can trigger recovery and lose all data.
- Device encryption eligibility (System Information → "Device Encryption Support"); since Windows 11
  24H2, more devices qualify. Device encryption on a local-account-only PC stays unprotected.
- Removable drives that carry sensitive data (BitLocker To Go).
- Small servers: system and data volumes encrypted where the threat model includes theft; recovery keys
  stored somewhere other than the server itself.

#### F. Accounts, administrators, and UAC

- List local accounts and members of Administrators. Ideally: one standard account for daily use, a
  separate admin account (or the user approves elevation with a separate credential), and no unknown or
  leftover accounts.
- The built-in Administrator account: disabled (default on clients). Guest: disabled.
- Accounts with `PasswordRequired` false or no password, and accounts that haven't signed in for a long
  time.
- **UAC**: `EnableLUA` = 1. `ConsentPromptBehaviorAdmin` = 0 means admins elevate silently: a finding.
  Prompt on the secure desktop. UAC is not a security boundary by Microsoft's definition, but turning it
  off removes useful friction against malware.
- **Administrator protection** (newer Windows 11 builds): if available on the installed build, whether
  it's on. Availability and defaults have changed during 2025–2026; verify on the device.
- **LSA protection** (`RunAsPPL`) and Credential Guard state (from `Win32_DeviceGuard`).
- NTLM settings (`LmCompatibilityLevel`), especially on servers and older machines.
- Family Safety child accounts versus admin accounts for children.

#### G. Microsoft account, sign-in, and Windows Hello

- For Microsoft-account sign-ins (ask the user to check, from the account's security page): two-step
  verification on, a passkey or authenticator app rather than SMS where possible, current recovery email
  and phone, recent sign-in activity reviewed, and no unknown devices.
- The Microsoft account protects much more than Windows: OneDrive files, Outlook mail, BitLocker keys,
  ESU license, Store purchases, and saved passwords in Edge if synced.
- **Windows Hello**: PIN, face, or fingerprint configured; the Hello PIN is device-bound, so a PIN is
  preferable to signing in with the account password. Check whether "only allow Windows Hello sign-in for
  Microsoft accounts" (passwordless) is on.
- Lock screen: automatic lock after inactivity, sign-in required on wake, Dynamic Lock if useful.
- Work or school accounts added under Access work or school: which tenant, and whether the user expects
  that management.

#### H. Windows Firewall and network profiles

- Network profile per connection (`Get-NetConnectionProfile`): home and office networks Private (or
  Domain), anything else Public. A laptop that marks a café network as Private exposes sharing services.
- All three firewall profiles enabled, inbound default Block. Third-party firewalls registered instead.
- Inbound allow rules: which programs and ports, on which profiles. Rules for unknown programs, for "Any"
  program on broad ports, or created by remote-access or game-server installs. Rules on the Public
  profile deserve the most scrutiny.
- Listening ports (`Get-NetTCPConnection -State Listen`) mapped to owning processes; anything listening
  on all addresses that the user can't explain.
- Firewall logging of dropped packets (useful for incidents; off by default).
- Network discovery and file and printer sharing: on only for networks where they're used.
- LLMNR and NetBIOS over TCP/IP: candidates for disabling on networks that don't need them (they enable
  name-poisoning attacks on the local network). Verify impact first.

#### I. Remote Desktop and remote-access tools

- **RDP** (`fDenyTSConnections` = 0 means enabled): who is allowed (Remote Desktop Users plus
  Administrators), whether **Network Level Authentication** is required (`UserAuthentication` = 1),
  which firewall profiles allow it, and whether it's reachable from the internet (router port forward,
  UPnP, or a cloud VM's public address). Internet-exposed RDP is a top ransomware entry point: high
  priority even with strong passwords. Changing the port is not a fix.
- Account lockout policy on machines that accept RDP or SMB logins.
- **Third-party remote-support and RMM tools**: list every installed or running remote-access product
  (installed programs, services, scheduled tasks, startup items, and portable executables in Downloads or
  temp folders). For each: who installed it, whether it's still needed, whether it runs unattended
  (always-on access) or only on demand, which account it's tied to, and whether that account has MFA. A
  tool the user installed because someone phoned them is a P0 indicator (see Respond).
- Remote-assistance features: Quick Assist and Remote Assistance enabled? Fine when used on demand with
  someone the user trusts; note that scammers ask victims to open Quick Assist.
- WinRM / PowerShell remoting (`Get-Service WinRM`, listener configuration): normally off on home PCs; on
  servers, restricted to admin networks.
- OpenSSH Server (optional feature): installed? If so, keys only and restricted by firewall rules.
- VPN clients and their always-on settings; split tunneling on work laptops.

#### J. SMB and file sharing

- SMBv1 server and client: not installed (`SMB1Protocol` feature state Disabled; `EnableSMB1Protocol`
  False). SMBv1 is not installed by default on Windows 11, Windows Server 2019 and later, or most Windows
  10 editions, but upgrades from older systems may still have it. If something "needs" SMBv1 (an old NAS,
  scanner, or media player), that device is the finding; update or replace it.
- Shares (`Get-SmbShare`): non-default shares, who has access, "Everyone" with write or full control,
  whole-drive shares (`C:\` shared), and shares of the user profile. Default admin shares (`C$`,
  `ADMIN$`, `IPC$`) are normal.
- SMB signing: required by default on Windows 11 24H2 and Windows Server 2025. If it has been disabled to
  make an old NAS or guest share work, that's a finding; Microsoft advises fixing the remote device
  instead. Same for re-enabled insecure guest logons.
- Mapped drives and stored network credentials (Credential Manager: record target names only). A PC that
  can write to the NAS or backup share lets ransomware encrypt it too.
- Public folder sharing and nearby sharing settings.

#### K. Startup items, scheduled tasks, and services (persistence)

- Scheduled tasks outside `\Microsoft\` with actions that run scripts (`powershell`, `cmd`, `wscript`,
  `mshta`, `rundll32`), binaries in user-writable paths (`C:\Users\<user>\AppData\`, `C:\ProgramData\`,
  `%TEMP%`), encoded command lines, or random-looking names.
- Services: `PathName` in user-writable folders, unquoted paths containing spaces, unknown publishers,
  services running as LocalSystem that belong to tools nobody remembers installing.
- Startup locations: Run and RunOnce registry keys (machine and user), the Startup folders, Task Manager
  → Startup apps. Microsoft Sysinternals Autoruns gives the most complete view; it's a vendor tool, but
  explain and get approval before downloading it (core tool-use contract).
- WMI event subscriptions in `root\subscription` (rare on clean home PCs).
- Browser extensions in each browser profile: unknown or broad-permission extensions are a common
  credential-theft path.
- Installed programs: unknown, unused, "cleaner"/"optimizer" tools, cracked software, and anything
  installed around the time of a suspected incident.

#### L. LAPS and shared admin passwords (small offices)

- Do several PCs share the same local admin password? If yes, compromise of one PC exposes all of them
  (lateral movement).
- **Windows LAPS** is built into supported Windows 11, Windows 10 (with the April 2023 update or later,
  while still receiving updates), and Windows Server 2019 and later. It backs up to Entra ID (Entra-joined
  devices; Entra ID Free or higher) or Active Directory (domain-joined devices), not both. It doesn't
  serve workgroup PCs with no directory: for those, record the shared-password risk and use unique
  passwords stored in a password manager.
- The legacy Microsoft LAPS MSI is deprecated and blocked on Windows 11 23H2 and later. If it's still in
  use, plan the move to Windows LAPS. Note that legacy emulation mode stores passwords in clear text in
  AD.
- Who can read LAPS passwords (AD permissions or Entra roles), rotation age, and the
  `Microsoft-Windows-LAPS/Operational` event log for errors.

#### M. Logging and monitoring

- Security log size (default sizes are small and roll over in days on busy machines), System log, and the
  Defender, PowerShell, Task Scheduler, and RDP-related logs.
- Audit policy (`auditpol`): logon/logoff, account management, process creation (with command line, if
  wanted), and policy change events enabled. Home editions have limited local policy tools; record what
  you can read.
- **PowerShell logging**: script block logging for Windows PowerShell 5.1 (policy key
  `HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging`) and separately for PowerShell
  7 (`PowerShellCore` policy key and log). Module logging and transcription. Script block logs may contain
  secrets that scripts handled; Microsoft recommends protected event logging when using it beyond
  diagnostics.
- Whether logs leave the machine (small offices: Windows Event Forwarding or a log collector), and whether
  anyone looks at Defender alerts.
- Time synchronization working (needed for correlating events).

#### N. Backups, recovery, and ransomware resilience

- **What's backed up and where**: File History (to an external or network drive), Windows Backup
  (OneDrive folder backup of Desktop, Documents, Pictures), OneDrive version history and recycle bin,
  system images, or a third-party tool. Ask for the date of the last good backup and the last tested
  restore.
- **Is any copy out of ransomware's reach?** A backup drive that stays plugged in, or a network share the
  user's account can write to, will be encrypted along with the PC. Look for an offline, versioned, or
  immutable copy (rotated external drive, cloud backup with version history, NAS snapshots the PC can't
  delete).
- OneDrive: sync is not a backup on its own; deletions and encryption sync too. Check that version
  history exists and how long the retention is for the user's plan (verify on the account).
- **Controlled Folder Access** (`EnableControlledFolderAccess`: 0 off, 1 block, 2 audit, 3 block disk
  modification only, 4 audit disk modification only). Off by default; requires Defender Antivirus active
  with real-time protection. Default protected folders include Documents, Pictures, Videos, Music, and
  Favorites (and their OneDrive Known Folder Move locations). Note any allowed apps, and data stored in
  folders CFA doesn't cover.
- Volume shadow copies and System Restore: present? (Useful but not a backup; ransomware deletes them.)
- Windows Recovery Environment enabled (`reagentc /info`, not yet verified as read-only on all builds) and
  recovery media available.
- Small servers: backup of system state and data, off-server copy, restore tested, backup credentials not
  usable from the server's normal admin account.

#### O. Physical security and data exposure

- Laptop theft: encryption with key backed up (domain E), sign-in required on wake, no passwords on
  sticky notes.
- Booting from USB allowed in firmware, firmware password set on high-risk laptops (optional).
- Thunderbolt/DMA protection (Kernel DMA Protection in System Information).
- Find my device enabled.
- Disposal: devices being sold or recycled are reset with "clean the drive" or securely erased (advice
  only; never automate).

#### P. Active Directory domain controllers (small office and homelab)

Not applicable when there is no domain. Run this domain once per domain, plus the per-server domains
(A–O) on each DC. Microsoft's guidance for larger estates (enterprise access model, Active Directory
security best practices) is linked in [references.md](references.md); this domain covers the checks
that matter most at small scale.

- **Topology and support**: how many DCs, their Windows Server versions and support dates (domain A),
  domain and forest functional levels, which DC holds the FSMO roles, whether the DCs are physical or
  virtual and who administers the hypervisor. `repadmin /replsummary` with no failures and `dcdiag /q`
  with no errors. **A single DC** is a finding (P3, or P2 if there is also no tested backup): losing it
  loses every account and Group Policy.
- **What else runs on the DC**: a DC should run AD DS, DNS, and perhaps DHCP, and little else. File
  shares, line-of-business apps, remote-support tools, web browsing, email, or a print server on a DC
  give everyone who uses those services a path into tier 0. Internet exposure of any DC port (RDP, LDAP,
  SMB, DNS) is P1.
- **Tier-0 accounts and Domain Admins membership**: list members (recursive) of Domain Admins,
  Enterprise Admins, Schema Admins, built-in Administrators, and the operator groups (Account, Backup,
  Server, Print Operators), plus DnsAdmins and Group Policy Creator Owners. At small scale, expect two or
  three named admin accounts, each **separate from the person's daily account** (no email or browsing
  as a domain admin), plus the built-in Administrator kept as a break-glass account with a long unique
  password stored offline. Findings: daily-use accounts in Domain Admins, service accounts or an IT
  provider's shared login in Domain Admins, members in operator groups (normally empty), Enterprise and
  Schema Admins with permanent members, `AdminCount = 1` accounts that are disabled or stale, and accounts
  nobody can name. Ask whether domain admins sign in to ordinary PCs: each such sign-in leaves
  credentials an attacker on that PC can reuse.
- **Protected Users**: whether admin accounts are members (no NTLM, no RC4/DES, no delegation, no cached
  logons, four-hour tickets). Microsoft warns not to add every privileged account at once, and never
  service or computer accounts; keep the break-glass account out until it has been tested.
- **Windows LAPS**: every member PC and server has a unique, rotating local admin password (domain L),
  passwords are **encrypted** in AD (requires Windows Server 2016 domain functional level), and only
  Domain Admins or a named admin group can read or decrypt them (`Find-LapsADExtendedRights`). On DCs,
  whether Windows LAPS backs up the **DSRM** password (AD only, and only with encryption enabled). If not,
  ask whether anyone knows each DC's DSRM password and where it is stored; nobody knowing it is a
  recovery finding.
- **krbtgt**: `PasswordLastSet`. Never reset since the domain was built (often years) is a finding
  (P3), and it must be reset in any incident where a domain admin or DC may have been compromised. Note
  any read-only DC `krbtgt_<number>` accounts; they are separate.
- **Service accounts**: user accounts with SPNs are open to Kerberoasting (any domain user can request a
  ticket and crack it offline), so a weak or old password on one is P2, and P1 if it is also a Domain
  Admin. Prefer group managed service accounts (gMSA; Windows Server 2025 adds delegated MSAs, which
  need a Windows Server 2025 DC and current updates, since an early privilege-escalation issue with them
  was fixed in 2025). Also flag accounts that don't require Kerberos pre-authentication, passwords that
  never expire on privileged accounts, and computers or users trusted for unconstrained delegation
  (other than DCs).
- **Kerberos encryption (RC4)**: Microsoft's phased change for CVE-2026-20833 (KB5073381) moved DCs to
  AES-only by default for accounts without explicit settings during 2026, with enforcement in the July
  2026 updates. Check that the DCs have those updates, review KDCSVC events 201–209 for anything still
  asking for RC4 (old NAS units, appliances, Linux or Java clients), and flag accounts explicitly set to
  allow RC4. Verify the current phase on the live KB.
- **LDAP signing and channel binding**: on each DC, whether unsigned SASL binds and clear-text simple
  binds are rejected (Windows Server 2025 new deployments require signing by default; 2022 and earlier,
  and upgraded DCs that kept old policy, don't) and whether channel binding is "When supported" or
  "Always" rather than "Never". Directory Service events 2886/2887 (unsigned binds allowed) and 3040/3041
  (unprotected LDAPS binds) mean the DC is still permissive. Scanners, printers, firewalls, VPNs, and
  NAS units using LDAP for user lookups are the usual reasons; they should use LDAPS or signed binds.
- **SMB signing**: required for inbound connections on DCs (the Default Domain Controllers Policy has long
  required it) and required on members where supported. Windows 11 24H2 Pro, Enterprise, and Education
  require inbound and outbound signing by default; Windows Server 2025 requires outbound signing by
  default; Windows 11 Home requires neither. A GPO that turns signing off domain-wide is P2.
- **NTLM**: NTLMv1 and LM refused (`LmCompatibilityLevel` 5 on DCs by policy), NTLM auditing enabled on
  DCs (enhanced NTLM auditing is available on Windows Server 2025 and Windows 11 24H2), and a list of what
  still uses NTLM. Microsoft has announced that network NTLM will be disabled by default in a future
  major Windows Server release, so the inventory is worth starting now. Restricting NTLM domain-wide is
  a project, not a toggle; record the current state.
- **Group Policy hygiene**: who can edit or link GPOs (Group Policy Creator Owners, delegated edit
  rights on individual GPOs, and write access to SYSVOL); the Default Domain Policy holding only password
  and account policies; **Group Policy Preferences passwords** (`cpassword` in SYSVOL XML; P1, since any
  domain user can read and decrypt them) and credentials in logon scripts under NETLOGON; disabled,
  unlinked, or empty GPOs that nobody can explain; and whether a Microsoft security baseline (Security
  Compliance Toolkit) or an equivalent is applied. A recently modified GPO that nobody remembers changing
  is an indicator (see Respond).
- **Password and lockout policy**: domain password policy (length at least 14 for people, or a
  passphrase policy; fine-grained policies for admins), account lockout threshold set, and no accounts
  with "password not required".
- **DNS on the DC**: AD-integrated zones accept **secure dynamic updates only**; recursion and
  forwarders configured on purpose; the DC's DNS is not reachable from the internet (open resolver).
  Members of DnsAdmins can run code on DCs; keep it empty.
- **Auditing on DCs**: advanced audit policy for account management, security group management,
  directory service changes, Kerberos authentication and service tickets, and logon events; Security log
  large enough to keep weeks, not hours; logs forwarded off the DC where possible.
- **AD backup and recovery**: a **system state** (or full-server) backup of at least one DC, taken more
  often than the forest's tombstone lifetime (`repadmin /showbackup` shows the last one), with one copy
  offline or immutable and not deletable with domain admin credentials; the AD Recycle Bin enabled; a
  restore tested (to an isolated network); and the DSRM password retrievable. VM-level backups of a DC
  count only if the backup product is AD-aware.
- **Adjacent tier-0 systems**: an Entra Connect (Microsoft Entra Connect Sync or Cloud Sync agent) server,
  AD Certificate Services, backup servers that hold DC backups, and the hypervisor. Record that they
  exist and who administers them; AD Certificate Services misconfiguration is a specialist review.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, find out what relies on the current state:

- **Who uses the PC, and how**: other family members, children, a shared office account. Removing admin
  rights or changing sign-in affects all of them.
- **Remote access paths in use**: RDP, a remote-support tool, or VPN that the user or an IT provider
  relies on, including the agent's own session. Don't remove the path you are connected through.
- **Devices that depend on SMB or old protocols**: scanners that scan to a folder, old NAS units, media
  players, CNC or lab equipment. They break when SMBv1 is removed or signing is required.
- **Software that conflicts with security features**: games with anti-cheat drivers (memory integrity),
  backup and disk tools (Controlled Folder Access, ASR), line-of-business apps that spawn child processes
  from Office (ASR rules), apps that write to Documents (CFA).
- **Encryption and boot**: any firmware update, TPM clear, Secure Boot change, or BIOS-mode change can
  trigger BitLocker recovery. The recovery key must be confirmed retrievable first.
- **Central management**: Intune, Group Policy, or an IT provider's RMM agent will override or fight
  local changes.
- **For servers**: every user, share, mapped drive, printer, and application that depends on it, and
  whether it's the only domain controller or DNS server.
- **For domain controllers**: every device and app that authenticates against AD or queries it over
  LDAP (printers and scanners with address books, firewalls and VPNs, NAS units, Wi-Fi RADIUS, line-of-
  business apps, Linux hosts joined with SSSD or Samba), every service that runs under a domain account,
  and every GPO the change touches. A domain-wide policy change reaches every PC at its next Group Policy
  refresh (about every 90 minutes), and a DC change that breaks authentication can lock out the admin
  who made it. Confirm a working break-glass account and a current system-state backup first.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Windows 10 without ESU | Upgrade to Windows 11 if eligible; otherwise enroll in ESU (22H2 required) as a bridge, then replace the PC. | Upgrade takes hours and needs a backup first; ESU needs a Microsoft account (consumer) or a purchased key (commercial) and ends on a fixed date. |
| Windows 11 version out of servicing | Install the current feature update. | Reboots, possible driver or app issues; back up first. |
| Updates paused, failing, or blocked by stale policy | Remove stale policies, resume updates, fix the failure. | Reboots; a backlog may take several restarts. |
| Defender off, passive with an expired third-party AV, or stale signatures | Remove the expired product so Defender becomes active; update signatures. | Brief window during the switch; check nothing else relied on the old product. |
| Tamper protection off | Turn it on in Windows Security. | Scripts or tools that change Defender settings stop working (intended). |
| Broad Defender exclusions | Remove each exclusion that isn't justified; narrow the rest to specific files. | The excluded app may be scanned or blocked; test it. If no one can explain an exclusion, treat it as an indicator. |
| No ASR rules | Enable the standard protection rules in block mode; add others in audit mode first, then block. | Some apps (Office add-ins, scripts, admin tools) may be blocked; review audit events before blocking. |
| Smart App Control or SmartScreen off | Turn SmartScreen back on; consider Smart App Control where available. | Unsigned or rare apps get blocked or warned; developers and hobbyists may find SAC too strict. |
| Drive not encrypted, or protection off | Turn on BitLocker or device encryption and back up the key (Microsoft account, Entra ID, AD, or a printed copy). | Encryption runs in the background; performance impact is usually small. Losing the key loses the data. |
| Recovery key location unknown | Have the user locate the key and confirm the key ID matches, or add a new recovery password protector and store it safely. | None if done before a recovery event; essential before any firmware or hardware work. |
| Daily use of an admin account | Create a standard account for daily use; keep one admin account for elevation. | User must enter admin credentials for installs; some old apps may need fixes. |
| UAC disabled or silent elevation | Re-enable UAC and prompt for consent. | More prompts; reboot required when re-enabling UAC. |
| Microsoft account without two-step verification | Turn on two-step verification with an authenticator app or passkey; update recovery info. | User needs the second factor to sign in on new devices; keep recovery codes safe (the agent never sees them). |
| No Windows Hello PIN | Set up a PIN (and biometrics if available). | Very low; the PIN is device-specific. |
| Firewall off or network marked Private on untrusted networks | Turn the firewall on for all profiles; set untrusted networks to Public. | Sharing and casting stop working on those networks (intended). |
| Unknown inbound firewall rules | Disable (don't delete) unexplained rules, observe, then remove. | The related app may lose incoming connections. |
| RDP exposed to the internet | Remove the router port forward; use a VPN, or a vendor gateway with MFA, for remote access. Require NLA. | Remote users need a working VPN first; test before removing. |
| RDP enabled but unused | Turn off Remote Desktop. | Nobody can connect over RDP. |
| Unneeded or unattended remote-support tools | Uninstall tools nobody owns; switch needed ones to on-demand mode with MFA on the vendor account. | The IT provider or family helper loses always-on access; agree on a replacement. |
| SMBv1 installed | Remove the SMBv1 feature; update or replace devices that need it. | Reboot; old devices that only speak SMBv1 lose access. |
| SMB signing or guest-logon protections weakened | Restore defaults; fix the remote device instead. | Old NAS or scanners may stop working until updated. |
| Over-broad shares | Restrict share and folder permissions to named users; remove whole-drive shares. | Users who relied on open access need explicit permission. |
| Suspicious persistence entries | Treat as an indicator; investigate before removing (see Respond). | Removing an unknown entry can destroy evidence or break a legitimate app. |
| Shared local admin password across PCs | Deploy Windows LAPS (Entra ID or AD), or set unique passwords in a password manager for workgroup PCs. | Helpers who used the shared password need the new retrieval method. |
| Legacy Microsoft LAPS | Migrate to Windows LAPS. | Plan the migration per Microsoft's guide; avoid long-term legacy emulation mode. |
| No PowerShell script block logging | Enable it (and protected event logging in offices that collect logs). | Logs may capture sensitive script content; increase log size. |
| Small Security log | Increase log sizes; forward logs in offices. | Disk use. |
| No backup, or backup always connected | Add a versioned backup with one copy offline or immutable; test a restore. | Cost of a drive or cloud plan; a routine to rotate drives. |
| Controlled Folder Access off | Enable in audit mode, review blocks for a week, then block mode. | Legitimate apps that save to Documents or Pictures may need to be allowed. |
| LSA protection off | Enable LSA protection (or rely on Credential Guard where enabled). | Some third-party drivers or plugins that load into LSA may fail; check audit events first. |
| Memory integrity off | Turn it on in Core isolation. | Incompatible drivers (some games, old hardware) block it or fail; check the incompatible-driver list first. |
| Server near end of support | Plan the migration to a supported Windows Server version or a cloud service. | Project, licensing cost, downtime window. |
| Single domain controller | Add a second DC (it can be a small VM on different hardware), or for very small offices consider whether Entra ID join without on-premises AD fits. | Licensing and one more server to patch; replication must be monitored. |
| Daily accounts in Domain Admins, or an IT provider's shared admin login | Create separate named admin accounts used only for administration; remove daily accounts from Domain Admins; give the provider named accounts with MFA on their remote path. | Admins sign in twice; scripts or scheduled tasks running as the old account break and must move to a gMSA. |
| Members in Account/Server/Backup/Print Operators or DnsAdmins | Remove them; delegate the specific task on an OU instead. | Whoever relied on the membership loses that right; check scheduled backups first. |
| Admin accounts not in Protected Users | Add named admin accounts one at a time after confirming they use Kerberos with AES; keep the break-glass account out until tested. | No NTLM, no cached sign-in (admins can't sign in offline), four-hour tickets; apps that need NTLM or delegation fail for those accounts. |
| No Windows LAPS on members, or passwords unencrypted in AD | Deploy Windows LAPS by GPO with AD password encryption and a named reader group; enable DSRM password backup on DCs. | Helpers who used the shared password need the new retrieval method; requires Windows Server 2016 domain functional level for encryption. |
| krbtgt password never reset | Reset it twice, at least 10 hours (the maximum ticket lifetime) apart, after confirming replication is healthy, using Microsoft's documented procedure. | Kerberos tickets issued before the reset stop working after the second reset; some non-Windows clients may need to re-authenticate. |
| Service account with SPN and old or weak password | Move the service to a gMSA (or dMSA on Windows Server 2025), or set a long random password (25+ characters) and remove it from privileged groups. | The service must be reconfigured and restarted; test in a maintenance window. |
| RC4 still requested or allowed | Find the client or account behind each KDCSVC event and update it to AES; allow RC4 only per account, as a documented exception. | Old NAS units, appliances, or keytabs may fail until regenerated with AES keys. |
| LDAP signing or channel binding not enforced | Enable diagnostic logging (event 2889 and 3039/3074/3075), fix the clients it names (use LDAPS or signed binds), then require signing and set channel binding to "Always". | Devices still using simple binds over port 389 or unsigned binds stop authenticating. |
| NTLMv1 or LM accepted; no NTLM auditing | Set LAN Manager authentication level to refuse LM and NTLMv1 on DCs; enable NTLM auditing and start an inventory. | Very old devices that only speak NTLMv1 fail; they are the finding. |
| Group Policy Preferences passwords in SYSVOL | Treat the password as exposed: change it on every system that uses it, then delete the preference item. | Whatever used that account must be updated; any domain user may already have read it. |
| Unexplained or overly delegated GPOs | Review each with its owner; remove edit rights from non-admins; disable (don't delete) unexplained GPOs after backing them up. | Settings the GPO applied disappear at the next refresh. |
| DNS zones allow nonsecure dynamic updates | Set AD-integrated zones to secure updates only. | Non-domain devices that registered themselves stop updating their records; give them static records. |
| No AD backup, or backups older than the tombstone lifetime | Schedule a daily system-state backup of at least one DC to a target domain admins can't delete, enable the AD Recycle Bin, and test a restore in isolation. | Disk space; the Recycle Bin can't be turned off once enabled. |

Changing the RDP port, renaming the Administrator account, and hiding the computer from the network are
supplementary only. Never recommend them as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (internet-exposed RDP, end-of-life OS,
disabled antivirus, unknown remote-access tools) → high-priority hardening (encryption with key backup,
MFA, admin separation, backups) → routine maintenance → optional defense in depth. Then ask for approval
(core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Windows specifics:

- **Before any change:** confirm a current backup of the user's data, confirm the BitLocker recovery key is
  retrievable (key ID matches), and create a restore point where System Restore is enabled. On a VM, take
  a snapshot. Record the current value of every setting you change.
- **Prefer the supported interface**: Settings, Windows Security, Group Policy (Pro and above), or the
  documented PowerShell cmdlet. On managed devices, make the change in Intune or Group Policy, not
  locally. Avoid raw registry edits when a cmdlet or policy exists.
- **Keep a way back in.** If connected remotely, never disable the remote path you're using, the only
  admin account, or the firewall rule that allows your session. Before removing admin rights from an
  account, confirm another admin account works by signing in with it.
- **Defender changes:** with tamper protection on, re-read settings after every change to confirm it
  applied. Never turn off tamper protection or real-time protection to make a change easier.
- **ASR and Controlled Folder Access:** start in audit mode, review events (Defender operational log) for
  a few days, add narrow allowed apps or exclusions, then switch to block. Never add broad folder
  exclusions to silence blocks.
- **BitLocker:** turning it on is C2 (reboot may be needed, recovery key must be saved first). Adding TPM+PIN
  changes the boot experience: make sure the user knows the PIN. Before firmware updates, Secure Boot
  changes, or hardware repairs, suspend BitLocker only for the documented number of reboots and only
  with approval; resume and verify protection afterwards.
- **Feature updates and Windows 11 upgrades:** C2. Back up, check app and driver compatibility, have the
  recovery key, and allow time. Don't use unofficial upgrade or bypass tools on the user's behalf.
- **SMBv1 removal:** C2 (reboot). Enable SMBv1 access auditing first on servers to find clients that
  still use it.
- **Remote-access tool removal:** uninstall through the vendor's uninstaller or Settings → Apps, then
  revoke the device from the vendor's web console and change that account's password. If the tool may
  have been installed by an attacker, go to Respond first and preserve evidence.
- **Firewall rules:** disable before deleting, and test the affected app between steps.
- **Domain controllers and domain-wide policy:** every change is **C2** at least. Before starting: a
  system-state backup newer than the change window, replication healthy, a tested break-glass account,
  and console (not only RDP) access to at least one DC. Make GPO changes in a new, narrowly linked GPO
  (one test OU first), back up existing GPOs (`Backup-GPO`) before editing them, and wait for refresh or
  run `gpupdate` on a test machine before widening the link.
- **Privileged group cleanup:** remove one membership at a time and confirm the person or service still
  works. Never remove the last working Domain Admins member, and never remove the account you are
  signed in with.
- **LDAP signing, channel binding, NTLM restrictions:** audit first, fix the clients the events name,
  then enforce on one DC before the others. Keep the previous setting recorded so it can be restored
  quickly if a critical device stops authenticating.
- **Routine krbtgt reset:** use Microsoft's procedure (or its `New-KrbtgtKeys` script, simulation mode
  first). Reset once, confirm replication of the change to every writable DC, wait at least the maximum
  ticket lifetime (10 hours by default), then reset the second time. Never do both resets in quick
  succession outside an incident.
- **Windows LAPS rollout:** link the policy to a test OU first; confirm a password appears (expiry
  visible) and an authorized admin can retrieve it before linking it more widely.
- **If something breaks:** roll back the single change (restore the recorded value, the restore point,
  or the VM snapshot), and report. Use Windows Recovery Environment only with the user present.

After each change, follow the core "after a change" steps: re-read the setting, check that Windows
Security shows no new warnings, confirm sign-in, network access, backups, and the user's key apps still
work, and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Displaying, copying, or transmitting BitLocker recovery passwords, LAPS passwords, Wi-Fi keys, or
  Microsoft account recovery codes.
- Decrypting a BitLocker volume, clearing the TPM, changing the boot mode (legacy to UEFI, `mbr2gpt`),
  editing Secure Boot keys or variables, or flashing firmware as security remediation.
- "Reset this PC", clean installs, disk partitioning, or `diskpart`/`format` operations.
- Deleting shadow copies, restore points, File History versions, OneDrive version history, or backups.
- Disabling Defender, tamper protection, or the firewall as a troubleshooting step.
- Running debloat, "privacy", or hardening scripts downloaded from the internet that change many settings
  at once.
- On domain controllers: restoring AD (authoritative or non-authoritative restore, DSRM boots), forest
  recovery, seizing or transferring FSMO roles, metadata cleanup, demotion, raising functional levels,
  schema changes, rapid back-to-back krbtgt resets, AD Certificate Services changes, and anything that
  modifies `NTDS.dit` or SYSVOL directly: refer to someone experienced with AD, using Microsoft's forest
  recovery guide. The same applies to Exchange or other server roles beyond simple settings.
- Reading, decrypting, or recording any account's password or hash from AD, including LAPS and DSRM
  passwords and Group Policy Preferences `cpassword` values.
- Paying for, downloading, or running ransomware decryptors (see core Respond guidance).

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the Windows-specific
steps in [incident-response.md](incident-response.md).

Windows P0 indicators include: a remote-access tool the user didn't knowingly install or that was
installed during a phone call; ransom notes or mass-renamed files; Defender turned off, tamper protection
off, or broad exclusions nobody added; new admin accounts; Security log cleared (event 1102); shadow
copies deleted; BitLocker enabled unexpectedly with an unknown key; or sign-in alerts on the Microsoft
account from unknown locations. On domain controllers, also: an unexpected member of Domain Admins,
Enterprise Admins, or another privileged group (events 4728, 4732, 4756); a new or modified GPO nobody
made, especially one that runs scripts or scheduled tasks; replication requests from a computer that
isn't a DC (DCSync); a new DC, trust, or `AdminSDHolder` change; or a krbtgt or DSRM password change
nobody made.

---

## Worked example (invented)

### WIN-001: Remote Desktop exposed to the internet on a small-office PC

**Confidence:** Confirmed
**Priority:** P1. RDP reachable from the internet is a common ransomware entry point; it allows unlimited
password attempts against every account in Administrators and Remote Desktop Users.
**State:** Open
**Component:** Remote Desktop Services, Windows 11 Pro 25H2 (build verified against release information)
**Evidence:** Observed 2026-02-03: `fDenyTSConnections` = 0 and `UserAuthentication` = 1 (NLA required);
inbound firewall rule "Remote Desktop - User Mode (TCP-In)" enabled on Private and Public profiles. The
user's router forwards TCP 3389 from its WAN address `203.0.113.10` to the PC at `192.0.2.25`. Security
log shows hundreds of failed logons (event 4625) per day from many external addresses, including
`198.51.100.77`, against the names `administrator` and `admin`; no successful remote logons from
external addresses (event 4624, logon type 10) in the retained log (seven days).
**Expected secure state:** RDP not reachable from the internet; remote access through a VPN or a gateway
with MFA (Microsoft Remote Desktop security guidance; CISA ransomware guidance).
**Exposure and prerequisites:** anyone on the internet; requires a valid password or an RDP
vulnerability. No account lockout policy is set. Two admin accounts exist.
**Dependencies / blast radius:** the office owner connects from home over this forward about twice a
week. The router supports WireGuard but it isn't configured.
**Recommended remediation:** set up the router's VPN and confirm the owner can connect to RDP through it;
then remove the port forward. Separately: set an account lockout policy, remove the Public profile from
the RDP firewall rule, and increase the Security log size so a longer history is retained.
**Operation class:** C2 (removes the owner's current remote path; router change).
**Approval required:** Yes.
**Verification:** an external check (with approval) no longer reaches TCP 3389; the owner connects over
the VPN; failed external logon events stop.
**Rollback:** re-create the port forward (not recommended; restrict it by source address if the VPN
fails).

---

## Version history

- **1.0** (2026-10-30): Initial version.
- **1.1** (2026-10-31): Added small-office and homelab Active Directory domain controller coverage:
  deployment variants for DCs and virtualized DCs, DC detection ports and announcements, read-only DC
  baseline commands, assessment domain P (tier-0 accounts and Domain Admins, Protected Users, Windows LAPS
  with DSRM backup, krbtgt, service accounts and gMSA/dMSA, Kerberos RC4 phase-out, LDAP signing and
  channel binding, SMB signing, NTLM auditing and deprecation, Group Policy hygiene, DNS, auditing, AD
  system-state backup), DC recommendations, remediation rules and hard stops, DC incident indicators and
  Respond steps, and Microsoft references.
