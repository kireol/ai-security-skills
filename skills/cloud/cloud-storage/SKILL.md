---
name: cloud-storage
description: >-
  Security assessment, hardening, remediation, and incident response for consumer cloud storage and sync
  services: Dropbox, Microsoft OneDrive, Google Drive, and Apple iCloud (iCloud Drive, iCloud Photos, and
  Advanced Data Protection). Covers shared links and who has access, sync clients on each device,
  connected apps, version history and ransomware recovery, family sharing, and account recovery. Use when
  reviewing what a household or small office has shared from its cloud storage, checking which devices
  and apps can reach it, planning ransomware recovery, or when a cloud storage account may have been
  compromised or files were encrypted or deleted.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Dropbox Basic/Plus/Essentials/Family; OneDrive with personal Microsoft accounts and Microsoft 365 Family/Personal; Google Drive with consumer Google accounts and Google One; Apple iCloud with iCloud+ (verify the live web apps and clients; features and retention vary by plan and change often)"
  audience: "home, work"
  finding_prefix: "CLS"
  modes: "discover, recommend, remediate, respond"
---

# Cloud Storage and Sync Security

Act as a careful, evidence-driven data protection engineer. Cloud storage quietly accumulates a
household's most sensitive files (tax returns, scans of passports, medical records, photos) and shares
them in ways people forget: a link sent once years ago still works for anyone who has it, an old laptop
still syncs, and an app authorized for a single task can still read everything. Sync also spreads damage:
ransomware or a careless delete on one device propagates to every other device and to the cloud copy.
Identify, explain, prioritize, remediate (only when authorized), and verify weaknesses in sharing, device
and app access, recovery, and account security.

## How to use this skill

This skill holds only cloud storage guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Cloud-storage-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation is in [references.md](references.md). Related skills: [Windows](../../operating-systems/windows/SKILL.md)
(OneDrive folder backup and Files On-Demand), [macOS](../../operating-systems/macos/SKILL.md) (iCloud
Drive and Desktop and Documents sync), [phones](../../mobile/phones/SKILL.md) (photo backup and Apple
Account or Google Account security), [MFA](../../identity/mfa/SKILL.md),
[backup tools](../../storage/backup-tools/SKILL.md) (independent backups of cloud data), and
[productivity suites](../productivity-suites/SKILL.md) for OneDrive for Business and Google Drive in a
Workspace domain.

## Cloud-storage-specific principles

- **The user does the checks; the agent guides and records.** Most checks happen in each service's web
  app or account settings, signed in by the user. Ask for screenshots or exports with names, email
  addresses, and file names cropped or redacted where they're sensitive. Never ask for the password,
  verification codes, recovery keys, or the Advanced Data Protection recovery key, and never sign in to
  the user's account.
- **File content is out of scope.** Discovery lists what is shared, with whom, and from which devices. It
  doesn't open, download, or summarize the user's files. When a file name itself suggests sensitive
  content, record the class ("a scanned identity document"), not the name.
- **Sync is not backup.** A sync client mirrors deletions, renames, and encryption to the cloud within
  seconds. Version history and recycle bins are time-limited recovery aids, not backups, and an attacker
  with the account can often empty them. At least one copy must sit outside the account (see
  [backup tools](../../storage/backup-tools/SKILL.md)).
- **"Anyone with the link" means anyone.** Links get forwarded, posted, indexed by chat apps' previews,
  and kept in old email. A link without a password or expiry is public for as long as it exists.
- **The account is the perimeter.** Whoever controls the Apple Account, Google Account, Microsoft account,
  or Dropbox account controls every synced device's files. Account MFA and recovery options come first.
- **Plans change the features.** Version history length, ransomware rollback, link passwords and expiry,
  and family features depend on the plan. Check the user's plan before recommending a feature, and point
  to the live plan comparison rather than quoting numbers from memory.
- **Menus change.** Describe the setting, give the expected location, and ask the user to confirm it.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Dropbox personal (Basic, Plus, Essentials)** | Dropbox client and web app; a single account. | Rewind, longer version history, and link passwords/expiry depend on plan. Review connected apps, linked devices, and web sessions. |
| **Dropbox Family or team** | A family manager or team admin; shared Family Room or team folders. | The manager controls membership; review who is in the plan and what the shared folder exposes. Team plans have an admin console and activity log. |
| **OneDrive with a personal Microsoft account** | Personal OneDrive; `onedrive.live.com` web app; Windows signed in with a Microsoft account. | Files Restore and ransomware detection need a Microsoft 365 subscription; Personal Vault for the most sensitive files. Windows may back up Desktop, Documents, and Pictures to OneDrive. |
| **OneDrive for work or school** | SharePoint-hosted OneDrive under a work account. | Tenant sharing policies apply; assess with [productivity suites](../productivity-suites/SKILL.md). This skill covers the user's own links and devices. |
| **Google Drive with a consumer Google account** | Personal Google account; Google One for extra storage or family sharing. | Review link sharing, third-party connections, and Drive for desktop. Version history and restore behavior differ for Google Docs files and uploaded files. |
| **Google Drive in Google Workspace** | Account on an organization domain. | Admin sharing policies apply; assess with [productivity suites](../productivity-suites/SKILL.md). |
| **iCloud standard data protection** | Apple Account with iCloud Drive and/or iCloud Photos; Advanced Data Protection off. | Apple holds keys for most data and can help with recovery. iCloud web access is available. |
| **iCloud with Advanced Data Protection** | Settings shows Advanced Data Protection on. | Most iCloud categories (including iCloud Drive, Photos, and Backup) are end-to-end encrypted; Apple can't recover them. A recovery contact or recovery key is mandatory and becomes critical. Not available in every country (check Apple's support page for regional status). |
| **Family sharing of storage** | iCloud+ Family Sharing, Google One family group, Microsoft 365 Family, Dropbox Family. | The organizer or manager controls membership and billing. Storage is shared, but files are not unless shared deliberately; check shared albums, shared folders, and Family Room. |

## Detection

Hints for recognizing these services on a device or network (used by the `full-assessment` skill).
Confirm with the user before relying on a match.

- **Installed clients and processes:** Dropbox (`Dropbox` process); OneDrive (`OneDrive.exe` on
  Windows, OneDrive app on macOS); Google Drive for desktop (`GoogleDriveFS`); iCloud for Windows, or
  iCloud Drive built into macOS and iOS.
- **Sync folders:** a `Dropbox` folder in the home folder or under `~/Library/CloudStorage/` on macOS;
  `%UserProfile%\OneDrive` on Windows; `~/Library/CloudStorage/` entries for OneDrive and Google Drive on
  macOS (File Provider integration); `~/Library/Mobile Documents/com~apple~CloudDocs` for iCloud Drive.
- **LAN discovery:** Dropbox LAN sync broadcasts on UDP port 17500 and transfers over TCP ports
  17599–17609 (vendor-documented), which reveals Dropbox clients on the local network.
- **DNS names in resolver logs:** `dropbox.com`, `dropboxapi.com`, `dropboxusercontent.com`;
  `onedrive.live.com`, `storage.live.com`; `drive.google.com`, `drive.usercontent.google.com`;
  `icloud.com`, `icloud-content.com`.
- **Phones:** camera upload or photo backup turned on in Dropbox, OneDrive, Google Photos, or iCloud
  Photos (see [phones](../../mobile/phones/SKILL.md)).

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Access and baseline

The user signs in to each service's web app or settings and reports what they see. Work service by
service, and for a household, person by person; each person consents to the review of their own account.

Candidate read-only commands on a computer, to inventory clients and sync folders. These are **not yet
verified** on every OS version; check each exists first. They list names and sizes only; don't read file
contents.

```sh
# macOS
ls ~/Library/CloudStorage/                      # File Provider sync locations (Dropbox, OneDrive, Google Drive)
ls -d ~/Library/Mobile\ Documents/com~apple~CloudDocs   # iCloud Drive present
pgrep -lf 'Dropbox|OneDrive|GoogleDrive|bird'   # running sync clients ('bird' is the iCloud Drive daemon)
# Linux
pgrep -lf dropbox
```

```powershell
# Windows
Get-Process OneDrive, Dropbox, GoogleDriveFS -ErrorAction SilentlyContinue
Get-ItemProperty 'HKCU:\Software\Microsoft\OneDrive\Accounts\*' -ErrorAction SilentlyContinue |
  Select-Object PSChildName, UserFolder        # OneDrive accounts on this PC (not yet verified)
```

The services' own developer APIs and CLIs need an app registration and an OAuth grant, which is itself
the kind of access this skill audits. Don't set one up for an assessment unless the user already uses it.

**Never do these during Discover:**

- Open, download, preview, or search the user's files or photos.
- Click "remove", "stop sharing", "sign out", or "disconnect" to test anything.
- Turn Advanced Data Protection, Rewind, Files Restore, or Restore files on or off.
- Request or display recovery keys, backup codes, or verification codes.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Account security and recovery

- MFA for each account: Dropbox two-step verification, Microsoft account two-step verification or
  passwordless, Google 2-Step Verification or passkeys, Apple Account two-factor authentication.
  Phishing-resistant methods (passkeys, security keys) preferred; SMS-only is weak (see
  [MFA](../../identity/mfa/SKILL.md)).
- Recovery options: recovery email and phone current and controlled by the account holder; backup codes
  or recovery codes stored offline; Apple Recovery Contact or Recovery Key; Google recovery options in
  Security Checkup.
- **Advanced Data Protection** (iCloud): on or off, which recovery methods are set (recovery contact,
  recovery key, or both), where the recovery key is stored, and whether "Access iCloud Data on the Web"
  is on. Losing all recovery methods with ADP on means Apple can't recover the data.
- Unique password in a password manager (see [password managers](../../identity/password-managers/SKILL.md)).
- Recent security activity: sign-ins and security events the user doesn't recognize.

#### B. Shared links and shared folders

- **Inventory everything shared by the user:** Dropbox shared links and shared folders; OneDrive
  "Shared" view (shared by you) and each item's Manage access; Google Drive items the user owns that are
  shared (search by sharing in Drive, or each folder's Share dialog); iCloud Drive shared folders and
  files, Shared Albums, and iCloud Shared Photo Library participants.
- For each: link type ("anyone with the link", people in a group, or specific people), permission (view
  or edit), password and expiry where offered, and whether the recipients are still appropriate.
- Flag edit-permission links to anyone, links to whole folders or the root, links on sensitive classes
  of documents (identity, tax, medical, financial, passwords), and shares with former partners,
  ex-employees, or unknown accounts.
- **Shared with the user:** folders others shared into the account that sync to every device (a source of
  unexpected or malicious files, and a path for ransomware in someone else's account to reach this one).
- Public or indexed content (Google Drive files published to the web, Dropbox file requests left open).

#### C. Devices and sync clients

- **Linked devices** in each account: Dropbox linked devices; Microsoft account devices; Google Account
  devices; Apple Account devices list. Flag devices the user doesn't recognize, sold or lost devices,
  and old computers still linked.
- On each computer that syncs: which client, which account, which folders sync (whole account or
  selective), whether files are online-only or kept locally, and who else uses that computer.
- Windows folder backup (OneDrive syncing Desktop, Documents, Pictures) and macOS Desktop and Documents
  in iCloud Drive: whether the user knows those folders live in the cloud.
- Client versions current and auto-updating (outdated clients are a supply-chain and vulnerability risk;
  check the vendor's release notes rather than a static list).
- Web sessions (Dropbox, Microsoft, Google) still signed in on shared or public computers.

#### D. Connected apps and integrations

- Apps with access: Dropbox connected apps; Microsoft account "apps and services you've given access";
  Google Account third-party apps with account access; Apple "Sign in with Apple" apps and apps using
  iCloud.
- For each: what it can reach (full Drive or Dropbox versus an app folder only), when it was authorized,
  whether it's still used. Flag "full access" grants to apps the user doesn't remember, browser
  extensions, and file converters or PDF tools used once.
- Automation services (IFTTT-style, Zapier-style), backup tools, and scanners that write to the account,
  and where their credentials live.

#### E. Version history, recycle bin, and ransomware recovery

- What the plan offers: Dropbox version history and Rewind; OneDrive version history, Recycle Bin, and
  "Restore your OneDrive" (Files Restore) with ransomware detection for Microsoft 365 subscribers; Google
  Drive version history and trash, and Drive for desktop's ransomware detection and bulk restore where
  available; iCloud.com Data Recovery (restore files, contacts, calendars) and Photos Recently Deleted.
  Record the retention windows the vendor currently documents for the user's plan.
- Whether the user knows how to roll back a whole folder or account, and has ever tried it on a test
  folder.
- Whether an attacker with the account could empty the trash and version history (usually yes), which
  is why an independent backup matters.
- **Independent copy:** does any copy of important cloud files exist outside the account (local backup
  of the sync folder, a NAS, or another provider)? For iCloud Photos, is "Download and Keep Originals" set
  on one device that is itself backed up? See [backup tools](../../storage/backup-tools/SKILL.md).

#### F. Sensitive data placement

- Classes of sensitive data in plain sync folders: identity documents, tax and financial records,
  medical records, password exports, recovery codes, private keys, or `.env`-style secrets files.
- Whether protected areas are used: OneDrive Personal Vault (extra verification, auto-lock), Dropbox
  Vault on plans that offer it, iCloud with ADP, or encrypting sensitive files before upload.
- Password manager exports or recovery codes stored in cloud storage are a finding.

#### G. Family sharing and household access

- Who organizes or manages each family plan; whether the organizer account has strong MFA (it controls
  membership and billing).
- Members who left the household still in the family group; shared albums or folders still shared with
  them.
- Children's accounts: what they share and with whom, through the platform's parental controls.
- Shared computers where one person's sync client exposes their files to everyone using the computer.

#### H. Notifications and activity monitoring

- Sign-in and new-device alerts reach a monitored address or phone.
- Dropbox and OneDrive mass-delete or ransomware detection emails, and Google Drive for desktop
  ransomware alerts: on, and the user knows what they look like.
- Recent activity or file event history reviewed after anything suspicious.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **People relying on links:** family, an accountant, a school, or clients who use a shared link or
  folder. Removing or narrowing it breaks their access; plan a replacement share with specific people.
- **Apps and automation:** scanners, backup tools, and automations that stop working when an app grant
  is revoked.
- **Devices:** unlinking a device stops sync and, for some clients, removes local copies of online-only
  files; files kept locally stay on the device.
- **Advanced Data Protection:** turning it on requires every device on the account to run a supported
  OS version, a recovery method, and acceptance that Apple can no longer recover the data.
- **Folder backup changes:** turning off OneDrive folder backup or iCloud Desktop and Documents changes
  where files live; users may think files "disappeared" (they stay in the cloud folder).

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No MFA or SMS-only | Turn on MFA with passkeys or an authenticator app; store backup codes offline. | Re-sign-in on devices. |
| Stale or weak recovery options | Update recovery email and phone; add an Apple Recovery Contact or Recovery Key. | Recovery material must be kept safe. |
| Anyone links to sensitive files | Replace with specific-people shares; add expiry and a password where offered; delete old links. | Recipients must sign in or get a new link. |
| Edit links to anyone | Change to view-only or specific people. | Collaborators lose edit access. |
| Shares with former members | Remove them. | They lose access immediately. |
| Unknown or old linked devices | Treat unknown devices as incident first (Respond); unlink old ones. | Unlinked devices stop syncing. |
| Unused connected apps | Revoke. | Integrations stop working. |
| Full-access app grants | Re-authorize with app-folder access where the app supports it. | Setup time. |
| No independent backup | Add a backup outside the account (see backup tools). | Cost and capacity. |
| No ransomware rollback | Learn and test Rewind, Restore your OneDrive, or Drive restore; consider a plan that includes it. | Cost. |
| Sensitive files in plain sync folders | Move to Personal Vault, ADP-protected iCloud, or an encrypted container; remove password exports and recovery codes. | Extra unlock step. |
| ADP off for a high-risk user | Offer Advanced Data Protection with two recovery methods. | Apple can't help recover data. |
| Organizer account weak | Strong MFA on the family organizer or manager account. | None. |

Hiding folders, renaming files, and relying on obscure link URLs are supplementary only. Never recommend
them as the main fix for public sharing.

Group the plan: immediate containment (if any) → urgent fixes (account MFA and recovery, public links to
sensitive files, unknown devices or apps) → high-priority hardening (independent backup, ransomware
rollback tested) → routine maintenance (stale shares, old devices) → optional defense in depth (ADP,
encrypted vaults). Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. The user makes each change in the
service's settings; the agent guides and verifies. Cloud storage specifics:

- **Capture before change.** Screenshot the share's current recipients and link settings, or the device
  and app lists, before removing anything, so a mistaken removal can be recreated.
- **Replace before removing** a share that someone legitimately relies on: create the specific-people
  share, confirm the recipient can open it, then delete the public link.
- **Unlinking devices:** confirm the device has no unsynced local changes first. Sign the client out on
  the device itself when the user still has it; use the account's device list for lost or unknown ones.
- **Advanced Data Protection:** set up and test recovery methods first (confirm the recovery contact
  accepted, or the recovery key is written down and stored). Enabling is **C2**: it changes who can
  recover data. Disabling uploads keys back to Apple's servers.
- **Version history and restores:** restoring a whole account or folder to an earlier time is **C2**,
  because it moves later files to the recycle bin; prefer restoring to a test folder or a single folder
  first. Emptying a recycle bin or deleting versions is **C3**.
- **Deleting shared folders or files is C3.** Prefer removing access over deleting.

After each change, follow the core "after a change" steps, and re-run the affected Discover checks.

### Hard stops (refer to a specialist; never automate)

- Emptying trash or deleting version history during or after a suspected incident.
- Disabling Advanced Data Protection, removing the last recovery method, or resetting end-to-end
  encrypted data without the user understanding that data may be lost.
- Restoring an entire account over current data while the cause of the damage (an infected device or a
  compromised account) is still active.
- Using third-party "recovery" tools that need the account password.

---

## Respond

On any P0 indicator (files encrypted or mass-renamed, mass deletions, unknown devices or apps, shares the
user didn't create, a sign-in alert they didn't trigger), switch to Respond immediately. Follow the core
playbook plus the cloud-storage-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### CLS-001: Public edit link to a folder of scanned identity and tax documents

**Confidence:** Confirmed
**Priority:** P2. Anyone with the link can view, download, replace, or delete identity documents and tax
returns; the link was emailed to several people years ago and may have been forwarded.
**State:** Open
**Component:** Personal Dropbox Plus account, shared links
**Evidence:** Observed 2026-10-22 by the user in Dropbox's shared links list (screenshot, names
redacted): an "anyone with the link can edit" link on a folder containing scanned passports and tax
returns, created years ago, no expiry, no password. The account owner confirmed only two family members
need access.
**Expected secure state:** sensitive folders shared only with specific people, view-only unless editing
is needed; no public links (Dropbox sharing documentation).
**Exposure and prerequisites:** anyone who has the link; no account needed.
**Dependencies / blast radius:** two family members open the folder from the link; an accountant used it
once last year.
**Recommended remediation:** share the folder with the two family members' accounts (view-only), confirm
they can open it, then delete the public link. Send the accountant a separate expiring link when needed.
Alternative: move the documents to an encrypted vault.
**Operation class:** C1 (the link can be recreated, though the old URL can't).
**Approval required:** Yes. Changes how family members access the folder.
**Verification:** the shared links list no longer shows the link; opening the old URL in a private
browser window fails; both family members can open the folder.
**Rollback:** create a new link with the same settings (not recommended).

---

## Version history

- **1.0** (2026-10-31): Initial version.
