---
name: backup-tools
description: >-
  Security assessment, hardening, remediation, and incident response for backup software and offsite
  backup targets: Restic (and rest-server), BorgBackup and Borgmatic, Veeam Agent and Veeam Backup &
  Replication Community Edition, Duplicati, and the Backblaze B2 and Wasabi cloud targets. Use when
  reviewing repository passwords and keys, append-only or immutable copies, 3-2-1 coverage, restore
  testing, backup server exposure, and scoped cloud keys, or when ransomware or an intruder may have
  deleted or encrypted backups.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Restic and rest-server, BorgBackup 1.4.x (2.x is beta at review; verify), Borgmatic, Veeam Agent and Backup & Replication Community Edition (v12/v13; verify), Duplicati 2.x, Backblaze B2, Wasabi (verify the live versions)"
  audience: "home, work, homelab"
  finding_prefix: "BAK"
  modes: "discover, recommend, remediate, respond"
---

# Backup Tools Security

Act as a careful, evidence-driven backup and recovery engineer. Identify, explain, prioritize, remediate
(only when authorized), and verify weaknesses that would let an attacker or a mistake destroy, encrypt,
read, or silently corrupt backups, or that would make a restore fail when it's needed. Ransomware
operators look for and delete backups before encrypting production, so the central question in every
assessment is: **if the protected system and its admin credentials were fully compromised right now,
which backup copies would survive, and could they actually be restored?**

## How to use this skill

This skill holds only backup-tool-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Backup-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

Related skills: NAS-native backup ([synology-dsm](../synology-dsm/SKILL.md) Hyper Backup and snapshots,
[qnap-qts](../qnap-qts/SKILL.md), [truenas](../truenas/SKILL.md)); hypervisor backup and Proxmox Backup
Server ([proxmox-ve](../../virtualization/proxmox-ve/SKILL.md)); ZFS snapshot replication
([zfs-and-ceph](../zfs-and-ceph/SKILL.md)); self-hosted S3 targets
([object-storage](../object-storage/SKILL.md)); and the client operating systems
([linux](../../operating-systems/linux/SKILL.md), [windows](../../operating-systems/windows/SKILL.md),
[macos](../../operating-systems/macos/SKILL.md)) and container hosts
([docker](../../containers/docker/SKILL.md)).

## Backup-specific principles

- **A backup the client can delete is not ransomware protection.** If the credentials stored on the
  protected machine can delete, prune, or overwrite the repository, an attacker on that machine can too.
  At least one copy must be append-only, immutable (object lock), or offline, and pruning must run from a
  separate, more trusted place.
- **The repository password or key is the backup.** Restic, Borg, Duplicati, and Veeam encryption can't
  be bypassed by the vendor. If the only copy of the password or key file is on the machine being backed
  up, losing that machine loses the backups. Equally, a password stored in plaintext next to the job means
  anyone who reads the job can read every backup.
- **Success emails are not restores.** Only a restore of representative data to a separate location,
  checked for content, proves recoverability. Repository checks (`restic check`, `borg check`) prove
  integrity, not that the right data is included.
- **The backup server is a high-value target.** Veeam Backup & Replication servers hold credentials for
  every protected system and have repeatedly had critical, actively exploited vulnerabilities. Treat any
  backup server as tier-zero: patched quickly, not domain-joined where the vendor advises against it, and
  unreachable from untrusted networks.
- **Cloud immutability is a one-way door.** Compliance-mode object lock can't be shortened or removed (on
  Wasabi, only with vendor support involvement). Size retention deliberately, start with governance mode
  where offered, and know that the cost of locked data is fixed for the retention period.
- **Never handle secret values.** Record that a password, key file, or application key exists, where it
  lives, who can read it, and its scope. Never print, copy, or log the value.

## Deployment variants

Identify every tool and target in Discover; most environments mix several.

| Variant | How to recognize it | What changes |
|---|---|---|
| **Restic, direct to a backend** (local disk, SFTP, S3, B2, rclone) | `restic` binary; `RESTIC_REPOSITORY` and password settings in scripts, systemd units, or wrappers (autorestic, resticprofile, Backrest). | Clients hold backend credentials; deletion rights depend on the backend's key or account. |
| **Restic with rest-server** | rest-server process, default port 8000; `.htpasswd` in its data directory. | `--append-only` and `--private-repos` decide whether a client can delete or see other clients' data. |
| **BorgBackup / Borgmatic over SSH** | `borg` and often `borgmatic`; `authorized_keys` on the repository server with `borg serve` forced commands. | Append-only is set per key (forced command) or per repository; Borgmatic config holds passphrase settings and hooks. Borg 2.x (beta at review) changes repository format; don't mix. |
| **Hosted Borg/Restic providers** | Repository URL at a storage provider. | The provider's account, MFA, and append-only or snapshot features become part of the assessment. |
| **Veeam Agent (Windows, Linux, macOS), standalone** | Veeam Agent installed; targets local, share, or repository. | Share credentials on the client; no server-side immutability unless the target provides it. |
| **Veeam Backup & Replication Community Edition** | Backup server (Windows, or the v13 Linux-based appliance; verify); console connects to the server. | Backup server, proxies, and repositories are separate components; hardened (immutable) Linux repository and object storage immutability are available depending on version and edition (verify). Workload limit applies to the free edition. |
| **Duplicati** | Web UI on port 8200; server or tray icon. | Server database holds job credentials and passphrases; protection depends on the settings encryption key and UI access control. |
| **Backblaze B2 / Wasabi as offsite target** | Bucket and key configured in a backup tool; account in the provider console. | Account MFA, key scoping, object lock, versioning, and lifecycle rules decide whether a stolen key can delete backups. |
| **NAS or hypervisor built-in backup** | Hyper Backup, QNAP HBS, TrueNAS tasks, Proxmox Backup Server. | Assess with the platform's skill; use this skill's independence, key, and restore-test checks. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match. Most backup tools are
clients with no listener; find them on the hosts, not the network.

- **Restic rest-server:** HTTP or HTTPS on TCP 8000 by default; S3-like REST paths per repository; a
  `/metrics` endpoint when Prometheus is enabled.
- **Borg:** no listener of its own; runs over SSH (22) with `borg serve` as a forced command on the
  repository server.
- **Duplicati:** web UI on TCP 8200 (later instances try further ports); listens on loopback only by
  default; page title mentions Duplicati.
- **Veeam Backup & Replication:** the console connects to the backup server on TCP 9392 (vendor-documented
  in the ports reference; verify the live version's port list, which also covers the REST API, web UI,
  proxies, and hardened repositories). Windows hosts show Veeam services; certificates may name Veeam.
- **Backblaze B2 / Wasabi:** outbound HTTPS from clients to the providers' API and S3 endpoints; no
  inbound listener.
- No backup-specific MAC address vendors (software on general-purpose hosts).

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Candidate read-only commands, **vendor-documented** for current releases unless marked; check
`--help` first. Every command that opens a repository needs its password: use the existing password file
or command with the user's agreement, never echo it, and never pass it on the command line where it
lands in shell history or the process list.

```sh
# Restic
restic version
restic snapshots --compact            # what is backed up, when, from which host
restic key list                       # key IDs, users, hosts, creation times (no secrets)
restic stats --mode raw-data          # repository size
restic check                          # integrity of structure (read-only by default; can take long)

# Borg / Borgmatic
borg --version
borg info <repo>                      # encryption mode (repokey vs keyfile), size
borg list --last 10 <repo>
borg config <repo> append_only        # repository-level append-only flag (run on the server)
borgmatic --version
borgmatic config validate             # on recent versions; verify the subcommand name
borgmatic list --last 5               # verify flags on the installed version
```

- On a Borg repository server, read `authorized_keys` for each backup key's forced command
  (`borg serve --append-only`, `--restrict-to-path`, `--restrict-to-repository`) and options such as
  `restrict`. Record which keys can write in normal (deleting) mode.
- On a rest-server host, read its service definition for `--append-only`, `--private-repos`, `--no-auth`,
  `--tls`, and listen address; check `.htpasswd` exists (never copy it).
- Duplicati, Veeam, B2, and Wasabi are mostly assessed through their UI or provider console: job lists,
  last results, encryption settings, retention, repository or bucket settings, key lists. Screenshots or
  exported settings with secrets redacted are good evidence. Duplicati's job export may include
  passphrases and credentials; don't export to an unencrypted file.
- B2 and Wasabi: list application keys, their bucket and prefix restrictions, capabilities, and expiry
  (B2 `b2 key list` in the official CLI, or the web console; Wasabi access keys and IAM policies in its
  console). Bucket object lock, default retention, versioning, and lifecycle settings per bucket.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, versions, and lifecycle

- Every backup job: tool and version, source systems and data, destination, schedule, retention, last
  success, and who owns it. Systems with **no** backup are findings too.
- Tool versions vs. current releases and security advisories (core: triage). For Veeam, check the vendor's
  per-release vulnerability KB articles and CISA KEV; Veeam servers on unpatched builds with known
  exploited flaws are P0/P1 candidates.
- Supported status: Borg 1.x vs. 2.x (beta at review; don't use for production), Veeam version support
  and Community Edition limits, Duplicati stable vs. canary channel.
- Wrappers and schedulers (Borgmatic, resticprofile, autorestic, Backrest, cron, systemd timers, Task
  Scheduler) and the account they run as.

#### B. Repository passwords, encryption keys, and secrets handling

- Is every repository encrypted? Restic always is; Borg can be `none` or `authenticated` only (not
  confidential); Duplicati jobs can be unencrypted; Veeam job encryption is optional.
- Where the repository password or passphrase lives: password file (owner and mode), environment variable
  in a unit or crontab (readable by whom?), `--password-command` / `BORG_PASSCOMMAND` /
  `encryption_passcommand` pulling from a secret store, or plaintext in a script or Compose file.
- Borg key mode: `repokey` (key in the repository, protected by passphrase) vs. `keyfile` (key on the
  client; losing the client loses the backups unless the key was exported). Has `borg key export` been
  done and stored safely?
- Restic: multiple keys (`restic key list`): are all expected? Any for retired hosts or people?
- Veeam: encryption password storage and hint; configuration backup encryption (needed to restore stored
  credentials); the credentials manager's accounts (which systems they reach and with what privilege).
- Duplicati: settings encryption key configured (the server warns in its logs if not); UI password set;
  per-job passphrases.
- **Offline escrow:** is there a copy of every repository password and key, plus the cloud account
  recovery information, somewhere that survives loss of all the protected systems (for example, a
  printed sheet in a safe or a second password manager vault)?

#### C. Deletion resistance: append-only, immutability, and offline copies

- For each repository, can the credentials on the protected client delete or overwrite existing backups?
  - rest-server: started with `--append-only`?
  - Borg: client keys forced to `borg serve --append-only`, or repository `append_only 1`? Who runs
    `prune` and `compact`, and from where? A prune from a normal-mode key makes earlier deletions
    permanent, so the pruning host must be trusted and checks (`borg check`) should run first.
  - Restic with S3/B2/Wasabi: does the client's key have delete rights? Is there object lock or versioning
    with a lifecycle that keeps old versions long enough? Does the tool's documented behavior work with
    locked objects (prune may fail on locked data)? Verify on the tool's documentation.
  - Veeam: hardened (immutable) repository or object storage immutability configured? Immutability period
    vs. retention? Is the hardened repository's host free of SSH and other admin paths per vendor
    requirements?
  - B2: object lock on the bucket with default retention? Keys without `deleteFiles`,
    `bypassGovernance`, `writeFileRetentions`, and `writeBucketRetentions` for clients?
  - Wasabi: bucket created with object lock (only possible at creation) or the Compliance feature (the two
    are mutually exclusive)? Retention period?
- Offline or air-gapped copies (rotated USB disks, tape, a powered-off target): how often rotated, and
  when last tested?
- Prune and retention policies: an attacker who can add fake snapshots can make `--keep-last`-style
  policies delete real ones; restic's documentation recommends `--keep-within` for append-only
  repositories.

#### D. 3-2-1 coverage and independence

- At least three copies, on two different media or systems, one offsite, and at least one immutable or
  offline (often stated as 3-2-1-1-0: zero errors in restore verification).
- **Administrative independence:** list the credentials that could delete each copy. If one account
  (domain admin, NAS admin, hypervisor root, the cloud account owner) can delete all copies, the copies
  aren't independent.
- Cloud account security for the offsite copy: MFA on the B2 or Wasabi account owner, recovery email
  security, separate account from everyday use, and whether the master key (B2) or root access key (Wasabi)
  is used by any backup client (it shouldn't be).
- Coverage of what matters: databases (dumped or quiesced, not just file-copied while running),
  application data in containers, hypervisor VMs, configuration of network devices, password manager
  exports, and the backup system's own configuration.

#### E. Restore testing and recoverability

- Date and scope of the last real restore test, per job, to a separate location; who did it; what was
  checked (files open, database starts, VM boots).
- Repository integrity checks: `restic check` (and periodically `--read-data` or `--read-data-subset`),
  `borg check` (and `--verify-data` before pruning in append-only setups), Veeam health checks and
  SureBackup where available, Duplicati verification.
- Restore time vs. recovery objectives (RTO), especially from the cloud (download bandwidth, egress
  limits or fees).
- Documented restore procedure that works without the protected systems (where the tool installer,
  passwords, and repository addresses are).

#### F. Backup server and service exposure

- rest-server: TLS on (otherwise HTTP Basic credentials travel in clear text); `--no-auth` absent;
  `--private-repos` on for multi-client servers; listen address; reachable only from backup clients;
  `--proxy-headers` used only behind a trusted proxy; metrics protected.
- Borg repository server: SSH key-only, no password login for the backup account, forced commands with
  `restrict`, one key per client, no shell access for backup keys.
- Duplicati: UI bound to loopback (default) unless remote access is needed; if remote, password set,
  `--webservice-allowed-hostnames` set, HTTPS configured, and preferably reached through a VPN or SSH
  tunnel, never the internet. Pre-authentication proxy tokens (if used) long and known only to the proxy.
- Veeam B&R: server and console ports reachable only from admin networks; patched to a fixed build;
  MFA on console users (available in recent versions; verify); not domain-joined to the production domain
  where the vendor's best practices advise against it; hardened repository not domain-joined (vendor
  requirement) and without SSH.
- Any backup UI or repository exposed through port forwards, tunnels, or reverse proxies.

#### G. Cloud targets: Backblaze B2 and Wasabi

- **Key scoping:** one application key (B2) or IAM user/access key (Wasabi) per client, restricted to one
  bucket (and prefix where useful), with the minimum capabilities. The B2 master application key has every
  capability on every bucket and should never be stored on a client.
- **Key lifecycle:** expiry where the tool can handle rotation; keys for retired clients deleted; no keys
  shared across hosts.
- **Object lock and versioning:** enabled where immutability is expected; default retention set (B2
  requires a default retention for files to be immutable by default; existing files aren't covered by
  later default changes); governance vs. compliance mode, and which keys can bypass or change retention.
- **Lifecycle rules:** B2 "keep only the last version" or short hide-to-delete rules, and Wasabi
  lifecycle or noncurrent-version rules, can delete old versions an attacker overwrote. Rules should keep
  versions at least as long as the detection window.
- **Account security:** MFA, separate admin users (Wasabi sub-users / IAM), notification of key creation
  where supported, billing alerts (sudden growth can mean an attacker uploading or a backup loop).

#### H. Monitoring and alerting

- Alerts on job failure, on jobs that **stop running** (a missing success is as important as a failure),
  on unusual size changes (a sudden jump in changed data often means encryption by ransomware), and on
  repository or bucket deletions and retention changes.
- Notifications sent to a mailbox or channel the attacker on the protected system can't silence.
- Logs of backup servers forwarded off the host; Veeam and Duplicati logs retained.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state. Common hidden dependencies are:

- **Running and scheduled jobs** that use the current password file, key, SSH key, share credential, or
  cloud key. Rotating any of them breaks the next run, often without a loud error.
- **Pruning and retention** that currently runs from the client; making the repository append-only or
  immutable moves that job elsewhere, and capacity grows until it runs.
- **Cloud cost**: object lock and versioning keep data longer; compliance retention fixes the cost for the
  whole period.
- **Restore procedures and other people** (family members, colleagues) who need the passwords and
  access during an emergency.
- **Veeam proxies, repositories, and stored credentials** that depend on the backup server's domain
  membership, certificates, and accounts.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Client can delete its backups | rest-server `--append-only`; Borg `borg serve --append-only` per key; cloud keys without delete; prune from a separate admin host. | Capacity grows until the admin host prunes; pruning must be monitored. |
| No immutable or offline copy | Add a locked bucket (B2/Wasabi/self-hosted with object lock), a Veeam hardened repository, or a rotated offline disk. | Cost, compliance retention can't be shortened; offline rotation needs discipline. |
| Repository password only on the client | Escrow passwords and keys offline in two places; `borg key export` for keyfile mode. | None beyond effort; skipping it risks permanent loss. |
| Plaintext password in script or unit | Move to a root-only password file or a password command reading a secret store. | Jobs need updating and a test run. |
| No restore test | Schedule a restore of representative data to a separate location; record results. | Time and temporary space. |
| B2 master key or broad key on clients | Create one bucket-restricted application key per client with minimal capabilities; delete the broad key after testing. | Each client reconfigured. |
| Lifecycle deletes old versions quickly | Lengthen version retention to exceed the detection window. | Higher storage cost. |
| rest-server without TLS or with `--no-auth` | Enable TLS with a valid certificate and htpasswd authentication; `--private-repos` for multi-client. | Clients need the new URL or CA. |
| Duplicati UI reachable remotely without need | Bind to loopback; reach it through an SSH tunnel or VPN; set a password and the settings encryption key. | Remote management path changes. |
| Unpatched Veeam server | Apply the vendor's fixed build after a configuration backup; restrict network access in the meantime. | Restart and job interruption during upgrade. |
| Veeam server on the production domain | Move toward a workgroup or separate management domain per vendor best practices; MFA for console users. | Significant re-architecture; plan carefully. |
| No job-stopped alerting | Alert when no successful run in N hours, independent of the job's own notifications. | Needs a monitoring service. |

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Backup-specific points:

- **Run one manual backup and one small restore after every change**, before considering it done. A job
  that silently fails is worse than the original finding.
- **Credentials:** create the new key, password entry, or SSH key and test it before removing the old one.
  `restic key add` then `restic key remove <old-id>` (C2: wrong order or wrong ID locks you out); for Borg,
  `borg key change-passphrase` only after the new passphrase is escrowed. Never remove the last working
  key.
- **Append-only changes** are C1 to C2 (the client's prune step will fail once enabled; move it first).
  Turning append-only **off** on a repository that may have been tampered with is dangerous: the next
  normal-mode write commits any pending deletions. Check the repository first.
- **Object lock and retention:** creating a locked bucket is C1; setting compliance retention is
  effectively irreversible for the retention period (treat as C3 for cost and capacity). Start with
  governance mode and a short period, test backup, prune, and restore, then extend.
- **Lifecycle rules:** adding or shortening rules deletes data (C3); lengthening them is C1.
- **Veeam upgrades:** take a Veeam configuration backup (encrypted) first, follow the vendor's upgrade
  order for server, proxies, and repositories (C2).
- **Duplicati:** setting the settings encryption key or changing UI binding restarts the server (C2); the
  key must be stored safely, because the server refuses to start without it once fields are encrypted.
- **Deleting old repositories, buckets, keys with data access, or backups** is C3 and is never part of
  routine hardening.

After each change, follow the core "after a change" steps.

### Hard stops (refer to a specialist; never automate)

- Repairing a damaged repository (`restic repair`, `borg check --repair`, rebuilding indexes, removing
  damaged packs or segments, Veeam backup file repair) as security remediation. Preserve a copy and follow
  the vendor's documentation or a qualified person; these operations can make things worse.
- Rolling back a Borg append-only repository by deleting segment files, even though the vendor documents
  the approach: it is a recovery operation, not hardening, and must be done on a preserved copy by
  someone who has read the current documentation end to end.
- Deleting backups, snapshots, versions, or buckets to free space, or shortening or bypassing retention
  locks, during an incident or under capacity pressure.
- Recovering storage underneath a backup target (RAID, filesystem, NAS volume). See the storage platform's
  skill and its hard stops.

---

## Respond

On any P0 indicator (backups or snapshots deleted, retention or lifecycle changed by nobody known, new or
unknown keys, jobs disabled, repository passwords changed, ransom notes, a sudden jump in changed data),
switch to Respond immediately. Follow the core playbook plus the backup-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### BAK-001: Offsite B2 copy deletable with the key stored on the backed-up server

**Confidence:** Confirmed
**Priority:** P2. Ransomware on the server would find the key and delete the only offsite copy; the
on-site copy is on a NAS that the same admin account controls.
**State:** Open
**Component:** Restic on a Linux file server, Backblaze B2 bucket `<offsite-bucket>`
**Evidence:** Observed 2026-10-25. The systemd unit for the nightly job sets `B2_ACCOUNT_ID`,
`B2_ACCOUNT_KEY`, and `RESTIC_PASSWORD_FILE`; the key's capabilities in the B2 console include
`deleteFiles` and `writeBucketRetentions` on all buckets. The bucket has no object lock and a lifecycle
rule keeping prior versions for 1 day. The restic password file is mode `0644`. Last restore test:
none recorded (user-reported). Server at `192.0.2.50`.
**Expected secure state:** a bucket-restricted key without delete or retention capabilities; object lock
with default retention covering the detection window; password file readable by the backup user only;
password escrowed offline; periodic restore tests (Backblaze application key and Object Lock
documentation; restic documentation on append-only use).
**Exposure and prerequisites:** local code execution on the server as any user can read the password
file; root or the backup user can read the B2 key and delete every object and version.
**Dependencies / blast radius:** the nightly restic job; a weekly `restic forget --prune` in the same unit.
**Recommended remediation:** create a new object-locked bucket with governance-mode default retention of
30 days; create an application key restricted to it with list, read, and write capabilities only; move
`forget --prune` to a separate admin workstation with its own key; set the password file to `0600`; escrow
the password offline; run and record a restore test. Alternative: add an append-only rest-server on a
separately administered host as a second offsite path.
**Operation class:** C2 (backup target and credentials change; job may fail until tested).
**Approval required:** Yes. Changes credentials, cost, and retention.
**Verification:** the next backup succeeds; a delete attempt with the new key is refused; the old key is
deleted after one good cycle; a restore of a sample directory to a scratch location matches the source.
**Rollback:** restore the captured unit file and the old key (kept until verification is complete).

---

## Version history

- **1.0** (2026-10-31): Initial version.
