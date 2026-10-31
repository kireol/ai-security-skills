---
name: object-storage
description: >-
  Security assessment, hardening, remediation, and incident response for self-hosted S3-compatible object
  storage: MinIO (community edition, its forks, and AIStor), with notes for Garage, SeaweedFS, and Ceph
  RGW. Use when auditing an object store's root credentials, access keys and policies, public or
  anonymous buckets, console and API exposure, TLS, versioning and object lock, or when a self-hosted
  bucket may have been exposed, emptied, or encrypted.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "MinIO community edition (archived upstream; verify the build and its source), MinIO forks and AIStor, Garage, SeaweedFS, and other self-hosted S3-compatible servers (verify the live version)"
  audience: "home, work, homelab"
  finding_prefix: "S3"
  modes: "discover, recommend, remediate, respond"
---

# Self-hosted Object Storage Security

Act as a careful, evidence-driven storage security engineer. Identify, explain, prioritize, remediate
(only when authorized), and verify weaknesses that could let someone read, overwrite, or delete objects in
a self-hosted S3-compatible store, take over its administration, or use it to destroy the backups it
holds. Self-hosted object storage is most often a **backup target** (for Restic, Borg-adjacent tools,
Veeam, Proxmox, or NAS replication) or an **application data store**, so a compromise usually means data
loss or data leakage elsewhere.

## How to use this skill

This skill holds only object-storage-specific guidance. It builds on the shared core, which always
applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Object-storage-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and project status pages are in [references.md](references.md).

Related skills: the host or container the store runs on ([linux](../../operating-systems/linux/SKILL.md),
[docker](../../containers/docker/SKILL.md)); backup tools that write to it
([backup-tools](../backup-tools/SKILL.md)); NAS platforms that bundle an S3 server or app
([synology-dsm](../synology-dsm/SKILL.md), [qnap-qts](../qnap-qts/SKILL.md),
[truenas](../truenas/SKILL.md)); and Ceph, whose RADOS Gateway is an S3 server
([zfs-and-ceph](../zfs-and-ceph/SKILL.md)).

## Object-storage-specific principles

- **Check the project's maintenance status first.** The MinIO community edition changed sharply in
  2025–2026 (verify the current state on the project's repository and vendor pages): reported in 2025, the
  community console was reduced to an object browser, with user, policy, and most administration moved to
  the `mc` client; prebuilt community binaries and images stopped in late 2025 (source-only
  distribution); the project entered maintenance mode in December 2025; and the upstream repository
  carries a "no longer maintained" notice and was archived in 2026. MinIO's maintained offerings are
  the AIStor editions (including a free tier). Community forks exist that restore the console or
  binaries. An unmaintained server that holds backups or is reachable from a network is a lifecycle
  finding in itself (core: triage, end-of-life rule), and a fork is a **supply-chain decision**: who
  builds it, who reviews security fixes, and how fast.
- **The root credential is everything.** MinIO's root user (`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`,
  or legacy `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`) bypasses all policies. If unset, MinIO has
  historically fallen back to the well-known default `minioadmin:minioadmin`. Garage's `admin_token`,
  SeaweedFS's admin identities, and Ceph RGW's admin users play the same role.
- **"Allow-all until configured" exists.** SeaweedFS's S3 gateway is documented to run in allow-all mode
  (no authentication) until at least one identity is configured. Never assume a fresh S3 endpoint
  requires credentials; test it (within scope).
- **Policies, not users, decide access.** Effective access is the union of user policies, group policies,
  service-account (access key) policies, bucket policies, and anonymous access settings. Read them all.
- **Immutability must exist before it's needed.** On MinIO and most S3 implementations, object lock can
  only be enabled when the bucket is created, requires versioning, and in compliance mode can't be
  shortened or removed by anyone, including root. Some servers (Garage, as of this review) don't
  implement versioning or object lock at all; verify on the live version's compatibility page.
- **Lock is only as strong as the storage under it.** Anyone with root on the host, the hypervisor, or the
  underlying disks can delete the files behind a "compliance-locked" bucket. Object lock protects against
  a compromised **client** or S3 credential, not against a compromised server.

## Deployment variants

Identify the variant in Discover. It changes which rules apply.

| Variant | How to recognize it | What changes |
|---|---|---|
| **MinIO community edition, last upstream build** | `minio --version` or `mc admin info` shows a `RELEASE.<date>` build; source matches the archived upstream project. | Treat as unmaintained: no routine fixes. Plan a migration or a maintained alternative; until then, minimize exposure (no internet, no untrusted networks). The console is an object browser only on later builds; administration is via `mc`. |
| **MinIO community fork** (restored console or rebuilt binaries) | Different image publisher or repository; version strings or branding differ. | Assess the fork's maintainer, release cadence, and security-advisory process as a supply-chain risk. A restored full admin console is a larger attack surface; restrict it like any admin UI. |
| **AIStor (MinIO's commercial line, including the free tier)** | Vendor-licensed build; license file or subscription configured; AIStor branding. | Vendor lifecycle and advisories apply. Licensing terms may limit features or node counts; verify on the vendor page. |
| **Garage** | `garage status`; S3 API, RPC, web, and admin ports as below; TOML config with `rpc_secret`. | No versioning or object lock (verify); its own key/bucket permission model instead of S3 bucket policies. The RPC secret is the cluster trust root. |
| **SeaweedFS S3 gateway** | `weed` processes (master, volume, filer, s3); filer UI; `security.toml`. | Allow-all S3 mode until an identity exists; master, volume, and filer HTTP APIs have their own (optional) JWT protection and can bypass S3 authorization entirely if reachable. |
| **Ceph RADOS Gateway (RGW)** | Part of a Ceph cluster; `radosgw` daemons. | Assess with this skill for S3 users, buckets, and policies, and with [zfs-and-ceph](../zfs-and-ceph/SKILL.md) for the cluster. |
| **NAS-bundled or container S3** (NAS app, Docker image) | Runs as a NAS app or container. | The NAS or container host is part of the trust boundary; data directories may sit on shares that other clients can reach directly. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **MinIO:** S3 API on TCP 9000 by default; `Server: MinIO` response header; S3-style XML error bodies
  (`<Error><Code>AccessDenied</Code>`); health endpoints under `/minio/health/live` and
  `/minio/health/ready`. The console has no fixed default port unless set with `--console-address`;
  deployments very commonly use 9001. Page title mentioning MinIO Console.
- **Garage:** example/default configuration uses 3900 (S3 API), 3901 (RPC between nodes), 3902 (S3 website
  endpoint), and 3903 (admin API, including `/metrics`).
- **SeaweedFS:** master 9333 (gRPC 19333), volume server 8080 (gRPC 18080), filer 8888 (gRPC 18888), S3
  gateway 8333; the all-in-one `weed mini` mode uses different ports for some services. Master and filer
  serve HTML status pages naming SeaweedFS.
- **Ceph RGW:** S3 on whatever port the deployment configured (commonly 80/443 behind cephadm or a proxy,
  7480 on older defaults); response headers or error bodies may mention RGW.
- Any HTTP service answering S3 XML (`ListAllMyBucketsResult`, `AccessDenied`) is an S3-compatible
  server worth identifying.
- No vendor MAC address: these run on general-purpose hosts, VMs, containers, or NAS units.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the server's own admin client with a **read-only** or audit credential where one exists. Using the
root credential to look is allowed only with the user's agreement, and its value must never be echoed,
logged, or stored in evidence.

MinIO `mc` (vendor-documented for recent builds; **not yet verified** on every build or fork; check
`mc --help` first, and note `mc` itself is affected by the upstream archival):

```sh
mc --version
mc alias list                         # shows endpoints AND secret keys: redact before recording
mc admin info <alias>                 # server version, nodes, drives
mc admin user list <alias>
mc admin group list <alias>
mc admin policy list <alias>
mc admin policy info <alias> <policy>
mc admin policy entities <alias>      # which users/groups have which policies (newer builds)
mc admin user svcacct list <alias> <user>
mc ls <alias>                         # buckets visible to this credential
mc anonymous get <alias>/<bucket>     # anonymous (public) access per bucket
mc anonymous list <alias>/<bucket>
mc version info <alias>/<bucket>      # versioning state
mc retention info --default <alias>/<bucket>   # default object lock retention
mc ilm rule list <alias>/<bucket>     # lifecycle rules (expiry can silently delete data)
mc replicate ls <alias>/<bucket>
mc encrypt info <alias>/<bucket>
mc admin config get <alias> identity_openid   # external identity, if used
```

Garage (**not yet verified** for every version): `garage status`, `garage key list`,
`garage key info <key>` (do not use options that print the secret), `garage bucket list`,
`garage bucket info <bucket>`.

SeaweedFS (**not yet verified**): `weed version`; in `weed shell`, `s3.configure` (shows identities;
redact secrets) and `s3.bucket.list`; read `security.toml` for which JWT keys are set (record set/not set,
never values).

Unauthenticated exposure checks, only within an authorized scope (class **R**, but they touch the
service from outside, so record source, time, and target):

```sh
curl -sI https://<s3-host>:9000/minio/health/live
curl -s https://<s3-host>:9000/                     # anonymous ListBuckets: should be AccessDenied
curl -s https://<s3-host>:9000/<bucket>?list-type=2 # anonymous ListObjects on a known bucket name
```

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, version, and lifecycle

- Product, edition (community, fork, AIStor, Garage, SeaweedFS, RGW), exact version/build, and where the
  binary or image came from (publisher, tag, **digest**, signature if any).
- Maintenance status of that source today: archived, maintenance-only, actively maintained. Check the
  project repository and vendor page live; don't rely on this skill's summary.
- Known vulnerabilities for the exact build (core: triage). Project security advisories are usually on the
  repository's security tab.
- Deployment topology: single node, single drive, erasure-coded multi-drive, multi-node; where data
  directories live and who can reach them outside S3.

#### B. Root and administrative credentials

- Is the root credential set, non-default, long, and unique? Test for `minioadmin` defaults only with
  approval and only against the target in scope; record the result, never the credential.
- Where root credentials are stored: environment files, Compose files, systemd units, Kubernetes secrets,
  NAS app settings, shell history. Who can read those files?
- Is root used by applications or backup jobs? It should be used only for administration, with day-to-day
  access through scoped users or access keys.
- Garage `admin_token` and `metrics_token`; SeaweedFS admin identities; RGW users with admin caps. Unset
  metrics tokens can expose `/metrics` without authentication on some products.
- External identity (OIDC, LDAP) configuration: which claims or groups map to admin policies.

#### C. Users, access keys, and policies

- Every user, group, and access key (service account), with attached policies. Look for `consoleAdmin`,
  `readwrite` on all buckets, `s3:*` on `arn:aws:s3:::*`, and `admin:*` actions.
- Backup-client keys: can they **delete** objects or versions, change bucket settings
  (`s3:PutBucketVersioning`, `s3:PutBucketObjectLockConfiguration`, `s3:PutLifecycleConfiguration`), or
  bypass governance retention (`s3:BypassGovernanceRetention`)? A ransomware-resilient backup key can
  write and read but not delete or reconfigure.
- One key per client or application, scoped to its own bucket or prefix; no shared keys across hosts.
- Key age, last use (where reported), expiry, and keys belonging to people or hosts that no longer exist.
- Access keys and secrets embedded in application configs, CI variables, or container environment
  variables visible through `docker inspect` (record existence and scope, never values).

#### D. Public and anonymous access

- Anonymous policy on every bucket (`none`, `download`, `upload`, `public`, or custom). Anonymous
  `upload` or `public` lets anyone write or delete.
- Bucket policies with `"Principal": "*"` or `{"AWS": ["*"]}`.
- SeaweedFS: whether any identity is configured at all (allow-all mode otherwise); anonymous bucket
  access rules.
- Garage: buckets with website access enabled, and keys with broad permissions.
- Presigned URLs in use: maximum expiry, and whether long-lived links are shared publicly.
- Unauthenticated listing of buckets or objects from outside (checked within scope).

#### E. Network exposure, console, and TLS

- Every path in: port forwards, reverse proxies, tunnels, published container ports, IPv6. Is the S3 API,
  the console, or an admin API reachable from the internet or from untrusted VLANs?
- MinIO console: bound to which address? Reachable from where? A restored full admin console (forks) is
  an admin UI and needs the same controls as any other.
- Garage admin API (3903) and RPC (3901): bound to all interfaces or to a management network? RPC should
  only be reachable by cluster nodes.
- SeaweedFS master, volume, and filer HTTP/gRPC ports: reachable by S3 clients? If so, a client can bypass
  S3 authorization through the filer or volume APIs unless JWT signing keys and gRPC mTLS are configured.
- TLS on the S3 API and console: certificate validity, hostname coverage, minimum TLS version, and
  whether clients verify certificates (backup tools configured with "skip verify" undo TLS).
- Reverse proxy behavior: does it forward `Host` correctly (S3 signatures depend on it) and avoid exposing
  admin paths publicly?

#### F. Data protection: versioning, object lock, lifecycle, replication

- Versioning state per bucket (`Unversioned`, `Enabled`, `Suspended`). Without versioning, an overwrite
  or delete is permanent.
- Object lock: enabled at creation? Default retention mode (governance or compliance) and period? Which
  identities can bypass governance? Compliance-mode periods that are longer than intended (they can't be
  shortened and will consume capacity).
- Lifecycle rules: expiry and noncurrent-version expiry. An attacker who can write a lifecycle rule can
  delete everything on the next scan; so can a mistaken rule.
- Replication targets and the credentials they use: can the source delete on the target?
- Server-side encryption: KMS configuration (MinIO KES, external KMS), where keys live, and whether loss
  of the KMS makes data unrecoverable. SSE protects disks at rest, not against a valid credential.
- Is this store itself backed up or replicated somewhere outside its administrative boundary? A bucket of
  backups with no second copy is a single point of failure.

#### G. Host, container, and underlying storage

- Who has shell or root on the host, VM, NAS, or container host? They can bypass all S3 controls by
  touching the data directory directly.
- Data directories: on a dedicated disk or share? Exported over NFS/SMB to other clients? World-readable
  permissions?
- Container settings: run as non-root, no host network unless needed, no Docker socket mount, data volume
  mounted narrowly (see [docker](../../containers/docker/SKILL.md)).
- For erasure-coded MinIO or multi-node Garage/SeaweedFS/Ceph: drive and node health as reported by the
  product. Record only; repairs are out of scope (hard stops).

#### H. Monitoring, audit, and logging

- Audit logging (MinIO audit webhook or Kafka target; RGW ops log; SeaweedFS and Garage logs): enabled,
  and sent off the host?
- Alerts for: deletions or version purges at unusual volume, policy or user changes, new access keys,
  lifecycle or object-lock configuration changes, anonymous policy changes, and authentication failures.
- Prometheus metrics endpoints: authenticated? Exposed beyond the monitoring host?
- Correct time and NTP (object lock retention and S3 request signing depend on it).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state. For an object store, common hidden
dependencies are:

- **Backup clients** (Restic, Veeam, Proxmox, NAS replication, database dumps) using a particular key,
  endpoint hostname, port, or certificate. Rotating a key or changing TLS breaks their next run, often
  silently until someone checks.
- **Applications** that store uploads or media in a bucket, often with keys in environment variables or
  config files, and sometimes relying on anonymous reads for public assets.
- **Presigned URLs and public links** that will stop working when anonymous access or keys change.
- **Replication** between sites or buckets that uses specific credentials.
- **Reverse proxies and DNS** that front the S3 API; S3 signature checks break if the host header changes.
- **Monitoring** scraping metrics endpoints.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Unmaintained MinIO community build | Plan migration to a maintained option (AIStor, a vetted fork, Garage, SeaweedFS, Ceph RGW, or a hosted provider); meanwhile, remove all untrusted exposure. | Migration takes time and capacity; feature parity varies (object lock, versioning, policies). |
| Default or weak root credential | Set a long random root credential stored in a password manager; restart. | All clients using root break; move them to scoped keys first. |
| Apps or backups using root | Create one scoped user or access key per client, bucket- or prefix-limited. | Each client must be reconfigured and tested. |
| Backup key can delete | Give backup clients write/read without delete or reconfigure rights; run pruning from a separate, more trusted admin credential. | Retention must be managed elsewhere; capacity grows until pruned. |
| Anonymous write or public bucket | Set anonymous access to `none`; serve public assets through a proxy or presigned URLs. | Public links and anonymous uploads stop working. |
| SeaweedFS allow-all mode | Configure identities (this switches authentication on for the whole gateway). | Every existing S3 client needs credentials before the change. |
| SeaweedFS internal APIs reachable | Restrict master/volume/filer ports to the cluster; configure JWT signing keys and gRPC mTLS per vendor docs. | Misconfigured keys stop writes cluster-wide; plan a window. |
| Console or admin API exposed | Bind to a management network or localhost; reach it through a VPN or SSH tunnel. | Remote admins need the new path first. |
| No versioning | Enable versioning on backup and important buckets. | Storage use grows; add noncurrent-version lifecycle rules sized to recovery needs. |
| No immutability for backups | Create a **new** bucket with object lock and a default retention (governance first, compliance once tested); point backups to it. | Can't be added to existing buckets; compliance retention can't be shortened; capacity planning required. |
| Plain HTTP or skipped verification | Enable TLS with a valid certificate; turn certificate verification on in clients. | Clients with pinned or skipped verification need updating. |
| No audit logging | Send audit logs to a separate host; alert on deletes and policy changes. | Needs a receiver; log volume. |

Geoblocking and non-standard ports are supplementary only. Never recommend them as the main fix.

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Object-storage specifics:

- **Use the product's admin client or API**, or the supported configuration method (environment file,
  config file, Helm values). Don't edit files inside the data directory or internal metadata (for MinIO,
  `.minio.sys`).
- **Credentials:** create and test the replacement credential before revoking the old one. Rotating the
  MinIO root credential usually requires a restart (C2). Never paste secrets into commands that end up in
  shell history or logs; use files or prompts.
- **Policies:** capture the current policy JSON (`mc admin policy info`) before changing it, change one
  principal at a time, and test the affected client immediately (a backup run, an app upload).
- **Anonymous access:** capture the current setting first; changing it to `none` is C1 if nothing depends
  on it, C2 if public assets or links break.
- **Object lock:** creating a locked bucket is C1; setting **compliance** retention is effectively
  irreversible for the retention period (treat as C3 for capacity: data can't be removed early). Prefer
  governance mode first and move to compliance after a successful restore test.
- **Lifecycle rules:** adding an expiry rule deletes data (C3). Removing one is C1. Review with a dry
  reading of which objects match before adding.
- **Upgrades and migrations:** a move between products, forks, or editions is a data migration (C2, with
  a verified copy and restore test before decommissioning the old store; decommissioning is C3).
- **TLS:** install certificates per vendor docs; keep the old certificate until clients are confirmed.

After each change, follow the core "after a change" steps: re-read the policy or setting, run an
authorized anonymous check from outside, and confirm each dependent client's next run succeeded.

### Hard stops (refer to a specialist; never automate)

- Healing, rebalancing, decommissioning pools, or replacing drives in an erasure-coded or multi-node
  cluster, or any manual work on a degraded cluster. Record the state; follow the vendor's documentation
  or a qualified person.
- Editing, moving, or deleting files in the data directory or internal metadata to "fix" an object or
  bucket.
- Deleting buckets, objects, versions, or delete markers, or forcing a bypass of governance retention, as
  security remediation.
- Removing or shortening object lock retention to free space during an incident.

---

## Respond

On any P0 indicator (unknown admin users or keys, policy changes nobody made, mass deletions or version
purges, new lifecycle expiry rules, anonymous write enabled, ransom notes as objects), switch to Respond
immediately. Follow the core playbook plus the object-storage-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### S3-001: Backup bucket deletable by every backup client, with no versioning

**Confidence:** Confirmed
**Priority:** P2. Any one compromised client that backs up to this store can delete every client's
backups; ransomware commonly does this before encrypting.
**State:** Open
**Component:** Self-hosted MinIO, single node, bucket `<backup-bucket>`
**Evidence:** Observed 2026-10-20 with `mc admin policy entities` and `mc admin policy info`: three hosts
share one access key with the built-in `readwrite` policy (all buckets, all actions including
`s3:DeleteObject`). `mc version info` reports the bucket `Unversioned`; no object lock. Server at
`192.0.2.40`, API on 9000, reachable only from `192.0.2.0/24`.
**Expected secure state:** one key per client, limited to its own bucket or prefix, without delete or
bucket-configuration actions; backups land in a versioned bucket with object lock retention (vendor
documentation on policies and object locking).
**Exposure and prerequisites:** an attacker with code execution on any of the three backup clients reads
the shared key from the backup tool's config and deletes all objects.
**Dependencies / blast radius:** three backup jobs use the shared key; retention pruning currently runs
from each client.
**Recommended remediation:** create a new bucket with object lock and governance-mode default retention
covering the backup retention window; create one key per client with a policy allowing `s3:PutObject`,
`s3:GetObject`, and `s3:ListBucket` on its prefix only; move pruning to a separate admin host with its own
credential; retire the shared key after all clients are moved. Alternative: if the server can't support
object lock, add a second, independent copy that the clients can't reach.
**Operation class:** C2 (backup jobs are reconfigured and may fail until tested).
**Approval required:** Yes. Changes every client's credentials and the backup target.
**Verification:** each client's next backup succeeds; a delete attempt with a client key returns
`AccessDenied`; a test restore from the new bucket succeeds; the shared key is disabled.
**Rollback:** re-enable the shared key and point clients back to the old bucket (kept until verified).

---

## Version history

- **1.0** (2026-10-31): Initial version.
