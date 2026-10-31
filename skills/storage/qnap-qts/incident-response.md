# QNAP QTS and QuTS hero: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only QNAP-specific steps.

## Recognizing a QNAP campaign

QNAP devices have been hit by repeated mass campaigns (ransomware families such as DeadBolt, Qlocker,
eCh0raix, and Checkmate, and persistent malware such as QSnatch). Patterns differ, and new ones appear, so
treat these as examples, and check QNAP's security advisories and news for an active campaign that
matches what you see:

- The QTS login or web page replaced by a ransom note, or a note file in many folders.
- Files renamed with a new extension, or moved into password-protected archives.
- Snapshots or backup jobs deleted or failing; Malware Remover or firmware updates failing or blocked.
- Unexpected admins, apps, scheduled tasks, startup scripts, or `/etc/hosts` entries.
- High CPU or disk activity with no matching user workload.

Record which pattern matches, but don't rely on the label alone: the same symptom can have several causes.

## Triage and containment

- **Isolate without powering off.** Unplug the NAS from untrusted networks at the router or switch, remove
  port forwards and UPnP mappings, and disable myQNAPcloud remote access, ideally from a clean device. For
  QuTScloud, disconnect the VM's virtual NIC on the hypervisor.
- **Don't reboot or shut down unless the user decides to.** Some campaigns leave a running process,
  decryption key exchange, or in-memory state that is lost at reboot; some encrypt more on restart. Weigh
  evidence and spread with the user, and follow QNAP's advisory for that campaign if one exists (QNAP has,
  for some campaigns, given specific instructions about whether to keep the device running).
- **If the storage pool is degraded, rebuilding, or reporting I/O errors, don't power-cycle or run any
  repair.** Get specialist help; see the hard stops in [SKILL.md](SKILL.md).
- **Stop replication and sync paths that could spread damage.** Pause Hybrid Backup Sync, RTRR, Qsync, and
  cloud sync jobs after checking that pausing them won't delete or roll over recovery points. Don't change
  snapshot retention or delete anything.
- **Protect backup destinations** the NAS can write to (USB disks, other NAS units, cloud buckets):
  disconnect them, or revoke the NAS's credentials at the destination, from a clean device.

## Evidence to preserve (QNAP-specific)

- A photo or screenshot of any ransom note or replaced login page, and a copy of note files, including
  any payment address or identifier (record it; never pay or contact on the user's behalf).
- QuLog Center / system and access logs, exported off the NAS.
- Current online users and sessions as shown in the UI.
- Users and the administrators group, with recent changes; the QNAP ID bound to myQNAPcloud.
- App list with versions and sources (`/etc/config/qpkg.conf` read-only, or App Center screenshots).
- Persistent crontab, the user-defined startup script (if present), and `/etc/hosts`.
- Container Station containers, images and digests, mounts, and published ports.
- QuFirewall rules, router port forwards and UPnP table, myQNAPcloud settings, reverse-proxy routes, and
  certificates.
- SSH authorized keys for every account.
- Snapshot list and backup-job history (what still exists and when the last good copy was made).
- Security Center, Security Counselor, and Malware Remover results, **before** acting on their fixes. A
  Malware Remover run can remove evidence along with malware; record its findings first.
- A sample of affected files (copied, never altered), for identification by a specialist or a reputable
  ransomware-identification service.

## Scope checks specific to a NAS

- Every client that maps or mounts the NAS's shares, since ransomware may have run on a workstation and
  encrypted shares over SMB. Check whether file changes came from a client account or a NAS-side process.
- Every system that shares the NAS's admin credentials, or that the NAS backs up to or replicates with.
- The QNAP ID linked to the NAS: its MFA, recovery options, and recent activity.
- Other QNAP devices on the same network or same QNAP ID; mass campaigns hit every exposed device.

## Eradication and recovery

- Follow QNAP's advisory for the specific campaign if one exists: it may give a fixed firmware or app
  version, a Malware Remover version, and specific recovery steps. Verify it on QNAP's own site.
- If firmware integrity is in doubt, use QNAP's current documented reinstall or reset procedure for the
  exact model and firmware, or QNAP support. Never improvise firmware flashing or storage repair.
- Snapshots on the compromised NAS may have been deleted or altered. Prefer a backup held outside the
  NAS's admin boundary, taken before the earliest plausible compromise. If on-NAS snapshots survive,
  restore from them only after the initial access path is closed.
- Don't pay a ransom or use a third-party decryptor on the only copy of data. If a decryptor is
  considered, a specialist should test it on copies. Paying is the owner's decision and may carry legal
  implications; refer them to law-enforcement guidance (see the core playbook).
- Rebuild containers from verified images; rotate every secret the NAS held.
- Before reconnecting: firmware and all apps at fixed versions, `admin` disabled, MFA on every admin,
  unauthorized apps, tasks, startup scripts, containers, and SSH keys removed, `/etc/hosts` clean, no port
  forwards or UPnP mappings, myQNAPcloud limited or off, and the initial access path closed.

## Quick checklist tailored for a QNAP NAS

When the user says "I think my QNAP has been hacked" or "my files are encrypted," start with the core
quick checklist, plus:

- [ ] From a clean device, remove port forwards and UPnP mappings and disable myQNAPcloud (or isolate the
      NAS at the switch), without powering it off.
- [ ] Photograph the ransom note or login page; check QNAP's security advisories for a matching active
      campaign and its instructions.
- [ ] Pause backup and sync jobs; disconnect backup disks attached to the NAS.
- [ ] Find which workstation or account is modifying files, if any; isolate it too.
- [ ] Export logs and capture apps, users, scheduled tasks, startup script, and Container Station before
      running Malware Remover or changing anything.
