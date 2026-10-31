# Backup Tools: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only backup-specific steps. During an incident, backups are the recovery path:
protect them before anything else.

## Triage and containment

- **Cut the attacker's reach into the backups first**, from a clean device:
  - Revoke or disable the cloud application keys (B2) or access keys (Wasabi) stored on compromised
    clients, after recording their IDs and scopes. Check the provider console for recently created keys,
    retention changes, lifecycle rule changes, and deletions.
  - On Borg repository servers, disable the compromised clients' SSH keys; on rest-server, remove their
    htpasswd entries or stop accepting their connections.
  - Disconnect attached backup disks and shares from compromised machines.
- **Stop scheduled pruning and retention everywhere** (restic `forget --prune`, `borg prune`/`compact`,
  Borgmatic, Veeam retention, Duplicati retention, cloud lifecycle rules) so the last good recovery points
  don't age out while you investigate. Don't delete anything.
- **Don't turn append-only off or run normal-mode writes against an append-only Borg repository** that
  may have been tampered with: that commits any pending deletions. Work on a preserved copy.
- **Veeam B&R server compromised or suspected:** isolate it from the network (it holds credentials to
  every protected system), keep it powered on for evidence if safe, and treat all credentials in its
  credentials manager as exposed.
- **Pause backups from infected systems** so encrypted data doesn't push out good versions where retention
  is count-based, but keep the existing backup history untouched.

## Evidence to preserve (backup-specific)

- Job lists, schedules, last-run results, and logs from every backup tool (Veeam session logs, Duplicati
  logs, Borgmatic and restic logs, systemd journal entries for timers).
- Snapshot and archive listings (`restic snapshots`, `borg list`) with times and hosts, and restic key
  lists; Borg's `transactions` file in append-only repositories (it lists transaction IDs with
  timestamps, used to identify suspect transactions).
- Cloud provider audit information: key lists with creation times, bucket settings, object lock and
  lifecycle configuration, recent deletions and version listings, account login history.
- rest-server and SSH logs on repository servers.
- Veeam configuration backup and the list of accounts in its credentials manager (names and targets, not
  passwords).
- Size and change-rate history of recent backups (a spike marks when encryption started).

## Scope checks specific to backups

- Every system whose credentials were stored in the backup server or backup tool (Veeam credentials
  manager, Duplicati server database, scripts with share passwords): treat them as exposed.
- Every repository the compromised client could reach with its stored credentials, and every other
  client sharing the same key or repository.
- Whether backup data itself was read (exfiltration): backups contain everything, so a stolen repository
  password plus repository access is a data breach.
- The earliest backup that predates the compromise, for each system, and whether its repository is
  outside the attacker's reach.

## Eradication and recovery

- Restore to clean, rebuilt systems, not onto compromised ones. Restore first to a separate location, scan
  and check the data, then put it into service.
- Choose recovery points from before the earliest plausible compromise; persistence (scheduled tasks,
  web shells, keys) is often included in later backups.
- Repository damage or tampering (failed `check`, missing packs or segments) is a hard stop for
  improvised repair: preserve a copy and follow the tool's current documentation or a qualified person.
- Rotate every repository password and key, SSH key, cloud key, and stored credential that was exposed;
  escrow the new ones offline.
- Before resuming normal backups: append-only or immutable copies in place, pruning moved to a trusted
  host, keys scoped per client and bucket, backup server patched and isolated, and the initial access path
  closed.

## Quick checklist tailored for backups

Start with the core quick checklist, plus:

- [ ] From a clean device, revoke the backup credentials stored on compromised machines and check the
      cloud console for new keys, retention changes, lifecycle changes, and deletions.
- [ ] Stop all pruning and lifecycle deletion; don't turn append-only off.
- [ ] Disconnect backup disks and shares from compromised machines.
- [ ] Identify the last good recovery point for each system and confirm it is out of the attacker's reach.
- [ ] Isolate a compromised Veeam or other backup server and treat its stored credentials as exposed.
