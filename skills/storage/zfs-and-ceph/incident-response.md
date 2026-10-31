# ZFS and Ceph: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only ZFS- and Ceph-specific steps.

## Triage and containment

- **Don't power off, export, or "repair" storage.** Shutting down a host with encrypted datasets loses the
  loaded keys (fine if you have them, fatal if you don't); repair and recovery operations are hard stops
  (see [SKILL.md](SKILL.md)). If the pool or cluster is unhealthy, get a qualified storage person.
- **Protect existing snapshots first.** Pause snapshot-pruning and retention jobs (sanoid, zrepl, cron
  scripts, appliance periodic tasks) so they don't age out the last good recovery points. With approval,
  place holds on the newest snapshots that predate the suspected compromise (C1). Don't destroy or
  roll back anything.
- **Stop replication that could carry damage.** Pause push replication from a suspected source, and
  revoke the source's credentials on the target from a clean device, so encrypted or deleted data
  doesn't overwrite good replicas (a forced receive can roll back or replace a replica).
- **Cut access paths without touching the pool:** disable the affected NFS/SMB shares or restrict them
  at the firewall, isolate the infected client that is modifying files, and remove the attacker's SSH
  keys from replication accounts (after recording them).
- **Ceph:** isolate the dashboard and monitoring stack from untrusted networks; disable (don't delete)
  suspicious dashboard users; for suspicious cephx entities, capture the key-free listing first, then
  revoke with approval (C2: a wrong revocation stops a legitimate client's I/O).

## Evidence to preserve (ZFS- and Ceph-specific)

- `zpool history` for every pool (records `zfs destroy`, `rollback`, `set`, `allow`, `change-key`, and
  receive commands with timestamps), exported off the host.
- `zfs list -t snapshot` with creation times, `zfs holds -r`, `zfs allow` for all datasets, and
  `zfs get -s local,received all` for affected datasets.
- Encryption status (`keystatus`, `keylocation`, `encryptionroot`) and the modification times of key
  files. Never copy key material into evidence.
- Replication tool configuration and logs, SSH `authorized_keys` and logs on both ends.
- Ceph: `ceph versions`, `ceph -s`, `ceph health detail`, `ceph config dump` (redacted), the key-free
  cephx entity and caps listing, `ceph mgr services`, dashboard user list, the cluster and audit logs,
  and the dashboard audit log if it was enabled.
- On appliances, the appliance's own audit and task logs (TrueNAS, Proxmox VE).

## Scope checks specific to ZFS and Ceph

- Which client or account changed or encrypted files: ransomware usually works through a share from an
  infected workstation, not on the storage host. Compare file-change times with share sessions.
- Every system holding replication SSH keys, ZFS key files or passphrases, or cephx keyrings
  (`client.admin` especially): any of them may be the entry point or a further victim.
- Replication targets and offline copies: were they reachable with the stolen credentials, and are their
  snapshots intact?
- Hypervisors and Kubernetes clusters consuming RBD or CephFS: a compromised client key can read or
  overwrite every image in its pool.

## Eradication and recovery

- Restore from a recovery point that predates the earliest plausible compromise, held outside the
  compromised host's admin boundary (a pull replica or offline copy). Restore into a new dataset or a
  separate system first and verify before replacing anything. Any rollback or destroy on the live pool is
  C3 and needs explicit approval and a verified recovery plan.
- If the host's integrity is in doubt, rebuild it per the platform's vendor procedure, then import or
  restore data with a qualified person if storage work is involved.
- After a suspected encryption-key compromise, `zfs change-key` is not sufficient (the master key is
  unchanged); plan migration of the data into newly created encrypted datasets.
- Rotate replication SSH keys, cephx keys for affected entities, and dashboard credentials; never reuse
  them.
- Before reconnecting: delegations narrowed, push-to-root replication removed, snapshot retention
  restored, holds reviewed, shares restricted, dashboard off untrusted networks, and the initial access
  path closed.

## Quick checklist tailored for ZFS and Ceph

Start with the core quick checklist, plus:

- [ ] Pause snapshot pruning and push replication; hold the last good snapshots (with approval).
- [ ] Isolate the client that is modifying files on the shares.
- [ ] Export `zpool history`, snapshot lists, holds, and delegations before changing anything else.
- [ ] Check replicas and offline copies from a clean device; revoke the source's access to them.
- [ ] For Ceph, capture the key-free cephx listing and dashboard users, then disable suspicious ones.
- [ ] If any pool or cluster is unhealthy, stop and bring in a qualified storage person.
