# Cloud Storage and Sync: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only cloud-storage-specific steps for three common incidents: ransomware or mass
damage spreading through sync, account takeover, and unwanted sharing or data exposure.

## Triage and containment

- **Ransomware or mass changes on a synced device: stop the spread first.**
  1. Disconnect the affected device from the network (Wi-Fi off, cable out). Don't power it off if the
     user may want forensic help later; core guidance applies.
  2. On every *other* device, pause sync in each client (Dropbox, OneDrive, Google Drive for desktop) so
     the damage doesn't overwrite their local copies, or disconnect them too.
  3. Don't delete encrypted files or empty the trash. Version history and the recycle bin are how you get
     the files back.
  4. Note the time the damage started (first encrypted or renamed file in the web app's activity view);
     it sets the restore point.
- **Account takeover (unknown sign-in, unknown device, new shares, changed recovery info):** from a clean
  device, change the password, sign out all other sessions (each service has a "sign out everywhere" or
  device list), remove unknown devices and connected apps, and check MFA methods and recovery options for
  attacker additions. For an Apple Account, follow Apple's guidance for a compromised account and check
  trusted phone numbers and devices.
- **Unwanted sharing or exposure:** remove the public link or the unwanted recipient right away (it's
  quick and reversible), after taking a screenshot of the share settings as evidence.
- **Shared folder from someone else:** if ransomware is coming from a folder another person shares into
  the account, leave the shared folder (or pause sync) and tell its owner; their device or account is
  likely the source.
- **Safety first in abuse situations:** if a current or former partner or family member may have access,
  removing them can alert them. See the safety guidance in [phones](../../mobile/phones/SKILL.md) and let
  the user decide the timing.

## Evidence to preserve (cloud-storage-specific)

- Screenshots or exports of: linked devices, connected apps, shared links and recipients, recent
  security events, and file activity or event history for the incident window.
- Dropbox events page, OneDrive and Google Drive activity panels, and Microsoft or Google account recent
  activity (sign-in times, locations, and devices).
- Ransom notes and one or two example encrypted files (copy them, don't open them); the file extension
  used can identify the ransomware family.
- Any ransomware-detection or mass-delete notification email from the service.
- Which device first showed damage, and which account it was signed in as.

## Scope checks specific to cloud storage

- **Every device signed in to the account,** including family members' devices for shared plans, and
  any device that syncs shared folders.
- **Other accounts reached from the same device:** a device infected with ransomware usually also
  exposed saved browser passwords and session cookies. Check the user's email, bank, and password manager.
- **Apps with access:** a malicious or compromised app grant can read, write, or delete everything it was
  granted; check what it did in the activity log.
- **Shared recipients:** if files were exposed, who could have opened the links, and whether the files
  contained data that requires notification (identity documents, financial or health information about
  others).
- **Backups:** confirm independent backups weren't reached through the same account or device.

## Eradication and recovery

- Clean or rebuild the infected device before it syncs again (see the operating-system skills). A device
  that still runs ransomware will re-encrypt restored files.
- **Restore in the service, not from the device:** Dropbox Rewind or version history; OneDrive "Restore
  your OneDrive" to a time before the damage (Microsoft 365 subscribers) or per-file version history;
  Google Drive version history or the Drive for desktop bulk restore where available; iCloud.com Data
  Recovery for files and Photos Recently Deleted. Restore a single folder first to check the restore
  point is clean, then the rest.
- If the cloud copies are beyond the service's retention window, restore from the independent backup.
- After a takeover: confirm unknown devices, apps, shares, MFA methods, and recovery options are gone;
  rotate any secrets that were stored in the account (API keys, recovery codes, password exports).
- Re-enable sync on one clean device at a time, and watch for new damage before reconnecting the rest.

## Quick checklist tailored for cloud storage

When the user says "my files are encrypted" or "someone got into my Dropbox/OneDrive/Drive/iCloud," start
with the core quick checklist, plus:

- [ ] Disconnect the damaged device; pause sync on every other device.
- [ ] Don't empty the trash or delete encrypted files.
- [ ] From a clean device: change the password, sign out everywhere, remove unknown devices and apps.
- [ ] Screenshot devices, apps, shares, and activity before cleaning up.
- [ ] Restore one folder to a point before the damage and check it; then restore the rest.
- [ ] Clean or rebuild the infected device before it syncs again.
