---
name: docker
description: >-
  Security assessment, hardening, remediation, and incident response for container hosts and workloads:
  Docker Engine on Linux, Docker Desktop on macOS, Windows, and Linux, Podman, and the container layer of
  NAS container managers, including Compose stacks. Use when auditing a container host, reviewing daemon
  and API exposure, published ports, container privileges, mounts, images, secrets, auto-updaters,
  networks, volumes, or logging, or when a container or container host may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Docker Engine 28.x-29.x, Docker Desktop 4.x, Podman 4.x-5.x, Docker Compose v2 (verify the installed versions; defaults change between releases)"
  audience: "home, work, homelab, web"
  finding_prefix: "DKR"
  modes: "discover, recommend, remediate, respond"
---

# Docker and Containers Security

Act as a careful, evidence-driven container security engineer. A container host concentrates risk: whoever
controls the container runtime controls the host, every container on it, and every secret and volume those
containers hold. A single badly configured container (privileged, holding the runtime socket, or bind-
mounting the host's root) erases the boundary between the container and the host. Identify, explain,
prioritize, remediate (only when authorized), and verify weaknesses in the runtime, its API, its network
exposure, and the workloads it runs.

## How to use this skill

This skill holds only container-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Container-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

This is the shared container skill. Product skills that embed a container manager (for example the
Synology DSM skill's Container Manager domain) cover their own UI, packages, and storage; use this skill
for the container layer underneath: daemon, API, ports, privileges, mounts, images, and secrets.

## Container-specific principles

- **Runtime access is root access.** Docker documents that the `docker` group "grants root-level
  privileges", and that only trusted users should control the daemon. The same applies to anyone who can
  reach the Docker API socket, a TCP API endpoint, a management UI such as Portainer, or a container that
  has the socket mounted. Count all of these as host administrators.
- **Inspect and Compose output is secret material.** `docker inspect` prints every environment variable;
  `docker compose config` resolves and prints interpolated values from `.env` files; `docker ps
  --no-trunc` and `docker history --no-trunc` can show command lines and build arguments. Extract only
  the fields you need with `--format`, and redact any value that looks like a credential before showing
  it. Never print `~/.docker/config.json` (registry credentials).
- **Published ports ignore the host firewall you think you have.** On Linux, Docker inserts its own
  packet-filter rules, and its docs state that Docker is incompatible with ufw: published container
  traffic is routed before ufw's rules apply. A port published without a host address binds to all IPv4
  and IPv6 addresses. Judge exposure from the actual bindings and the packet-filter rules, not from `ufw
  status`.
- **Recreating is the change, not editing.** Most container settings can't be changed in place; the
  container must be recreated (`docker compose up -d` after editing the file). Recreation restarts the
  service, may pull a newer image if the tag moved, and can lose data held only in the container's
  writable layer or in anonymous volumes. Treat it as **C2**, and check where the data lives first.
- **A daemon setting affects every container.** Changes to `daemon.json` or the daemon's service unit
  need a daemon restart, which stops every container unless `live-restore` is enabled (and some changes
  need a restart regardless). Treat them as **C2** for the whole host.
- **Tags are mutable; digests are not.** `image:latest` or `image:1.2` can point to different content
  tomorrow. Only a digest (`image@sha256:<digest>`) identifies exact content. Record digests as evidence.
- **Docker Desktop is a VM, not the host.** On macOS and Windows (and Docker Desktop for Linux),
  containers run inside a Linux VM. The VM boundary helps, but published ports are still forwarded to the
  host and can be reachable from the LAN, file sharing exposes host directories, and container escapes to
  the VM have been followed by escapes to the host in past advisories. Keep Desktop updated.
- **Containers are not a security boundary by default.** Default settings (root inside the container, a
  writable root filesystem, the default capability set) are a convenience baseline, not hardening. Judge
  each workload on what an attacker who compromises it could reach.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Docker Engine, rootful** (Linux) | `dockerd` running as root; socket at `/var/run/docker.sock`; `docker info` has no `rootless` security option. | The common case. Socket and `docker` group are root-equivalent; published ports manipulate the host's iptables/nftables rules. |
| **Docker Engine, rootless** (Linux) | `docker info` lists `rootless` under Security Options; socket under the user's runtime directory (`/run/user/<uid>/docker.sock`). | Daemon and containers run in a user namespace as an unprivileged user, which limits a breakout to that user. Ports below 1024 aren't bindable by default; resource limits need cgroup v2 with systemd; it can't run as a system-wide service. The user account itself becomes the high-value target. |
| **Docker Desktop** (macOS, Windows, Linux) | Docker Desktop app and backend processes; `docker context ls` shows `desktop-linux` or a Desktop context. | Containers run in a Linux VM. Settings are in the app, not `daemon.json` alone. Optional features (Enhanced Container Isolation, Settings Management, Registry Access Management) depend on the subscription. Host networking is opt-in (version 4.34 and later) and works at layer 4 only. |
| **Docker Desktop, managed** (business) | Admin-enforced settings shown as locked in the app. | Some settings are controlled centrally; changes go through the organization's admin console, not the local app. |
| **Podman** (rootless or rootful) | `podman` CLI; no long-running daemon unless `podman system service` or the socket unit is enabled; Quadlet unit files under systemd. | Rootless is the default for normal users. The API socket, when enabled, is root-equivalent for its user (rootful: `/run/podman/podman.sock`). Containers may be managed as systemd units, so check systemd as well as `podman ps`. |
| **Podman machine / Docker alternatives on macOS or Windows** (Podman Desktop, Colima, OrbStack, Rancher Desktop) | Their own VM processes and contexts; `docker context ls` may list several. | Same VM-boundary questions as Docker Desktop, with each product's own settings. Identify which runtime actually serves each context. |
| **NAS container manager** (Synology Container Manager, QNAP Container Station, Unraid, TrueNAS apps) | Container UI inside the NAS admin interface; Docker or a compatible runtime underneath. | The NAS product skill covers its UI and storage. Bind mounts usually point at NAS shares, so a container compromise reaches stored data directly. Vendor updates to the NAS don't update container images. |
| **Swarm mode** | `docker info` shows `Swarm: active`. | Ports published by Swarm services ignore the daemon's default bind address and listen on every node. The Swarm control-plane ports and join tokens are additional assets. Kubernetes is out of scope for this skill. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **Docker API over TCP:** port 2375 (no TLS) or 2376 (TLS) are Docker's documented defaults. A plain-HTTP
  answer to `/version` on a non-loopback address is an unauthenticated root-equivalent API and is at least
  a P1 finding, P0 if reachable from the internet. Don't send any request other than a version query, and
  only within scope.
- **Swarm:** TCP 2377 (cluster management), TCP/UDP 7946 (node communication), UDP 4789 (overlay network
  traffic).
- **Container management UIs:** Portainer commonly on 9443 (HTTPS), 9000 (HTTP, older installs), and 8000
  (edge agent tunnel); the Portainer agent on 9001. A Portainer agent port reachable from untrusted
  networks is effectively a remote runtime API.
- **Hosts that run containers:** many unrelated services on one address (web apps, databases, media
  servers) on non-standard high ports; a `docker0` bridge interface and `br-<id>` and `veth` interfaces on
  the host; container subnets drawn from Docker's default address pools (private ranges starting at
  172.17 and 192.168 by default; verify `default-address-pools` in `daemon.json`).
- **Docker Desktop on a workstation:** processes such as `com.docker.backend` (macOS, Linux) or
  `com.docker.backend.exe` and `Docker Desktop.exe` (Windows); a `docker-desktop` WSL distribution on
  Windows; a QEMU or virtualization-framework VM process. Published container ports appear as listening
  sockets owned by the Desktop backend process, not by a container.
- **Podman:** `podman` and `conmon` processes; `gvproxy` for a Podman machine on macOS or Windows.
- **MAC address vendors:** none specific. Containers on macvlan or ipvlan networks appear on the LAN with
  their own addresses and locally administered or generated MACs, which can look like unknown devices.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Ask which runtime, context, and host is in scope, and run commands as the user who normally manages it.
These are *candidate* read-only commands, **not yet verified** on every version and platform unless marked.
Check that each exists and what it does on the installed version first.

> **Redaction warning.** `docker inspect`, `docker compose config`, `podman inspect`, `docker logs`, and
> `--no-trunc` output can contain passwords, tokens, and connection strings. Always use `--format` to
> pull specific fields, never dump the `Env` array, and redact anything credential-like before showing,
> storing, or uploading output (core: operating principles, untrusted data and privacy).

```sh
# Runtime, version, and daemon settings
docker version                         # client and server versions (vendor-documented)
docker info                            # security options (rootless, userns, seccomp), logging driver, Swarm
docker context ls                      # which endpoints the CLI can reach (local socket, ssh://, tcp://)
cat /etc/docker/daemon.json            # daemon settings (Linux, rootful); review before showing
systemctl cat docker.service           # listener flags such as -H tcp://... in the service unit
ls -l /var/run/docker.sock             # socket owner and group
getent group docker                    # members of the root-equivalent docker group

# Containers, ports, and security-relevant settings (field names not yet verified on every version)
docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker inspect --format '{{.Name}} priv={{.HostConfig.Privileged}} net={{.HostConfig.NetworkMode}} pid={{.HostConfig.PidMode}} user={{.Config.User}} ro={{.HostConfig.ReadonlyRootfs}} capadd={{.HostConfig.CapAdd}} secopt={{.HostConfig.SecurityOpt}} restart={{.HostConfig.RestartPolicy.Name}}' $(docker ps -aq)
docker inspect --format '{{.Name}}{{range .Mounts}} | {{.Type}} {{.Source}} -> {{.Destination}} rw={{.RW}}{{end}}' $(docker ps -aq)
docker inspect --format '{{.Name}} devices={{.HostConfig.Devices}} log={{.HostConfig.LogConfig.Type}}' $(docker ps -aq)

# Images, networks, volumes, Compose
docker image ls --digests              # repositories, tags, digests, ages
docker network ls
docker network inspect --format '{{.Name}} {{.Driver}} internal={{.Internal}}' $(docker network ls -q)
docker volume ls
docker compose ls                      # Compose projects and their config file paths
docker compose -f <file> config --no-interpolate   # structure without substituted .env values; still review

# Host-side exposure (Linux)
ss -ltnup                              # what actually listens, on which addresses (IPv4 and IPv6)
iptables -S DOCKER-USER; iptables -S FORWARD; nft list ruleset   # Docker's rules and any user filtering

# Podman equivalents
podman info; podman ps -a; podman image ls --digests
systemctl --user list-units --type=service   # Quadlet/systemd-managed containers (rootless)
```

- `docker events` and `docker logs --tail <n>` are read-only but stream data that may include secrets;
  use them deliberately, with a time limit.
- Image scanners (Docker Scout `docker scout quickview` / `cves`, Trivy `trivy image`, Grype `grype`)
  are read-only toward containers but download vulnerability databases and, for Scout, may send image
  metadata to Docker's service. Installing a scanner is a change on the host (C1); ask first, and verify
  the scanner's own provenance (pin a release and check its checksum or signature; scanners themselves
  have been targets of supply-chain attacks).
- **Never run** during Discover (all are C2 or C3): `docker system prune`, any `prune` (`image`,
  `container`, `volume`, `network`, `builder`), `docker rm`, `docker rmi`, `docker volume rm`, `docker
  compose down` (with `-v` it deletes volumes), `docker compose pull` followed by `up -d` across stacks
  ("update everything"), `docker restart`/`stop`/`kill`, Watchtower `--run-once`, Docker Desktop "Reset to
  factory defaults" / "Clean / Purge data" / Troubleshoot reset actions, `podman system reset`, `docker
  swarm leave`, and daemon restarts.
- **Don't** run `docker exec` into a container as a "read-only" check without approval: it runs code in a
  workload that may be compromised and leaves traces. Don't start probe containers that mount the host
  (`-v /:/host`, `--privileged`) to look around; that is itself the attack pattern this skill looks for.
- Don't run `docker login`, print `~/.docker/config.json`, or read files under `/run/secrets` or `.env`
  files beyond confirming they exist and who can read them.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, versions, and lifecycle

- Runtime and version: Docker Engine (and its `containerd` and `runc` versions from `docker version`),
  Docker Desktop, Podman, or a NAS-bundled runtime. Check each against current release notes and
  security announcements (core triage). Container-escape fixes often land in `runc` or the Desktop VM,
  not the CLI.
- Package source: the vendor's repository, the distribution's packages, a NAS vendor package, or a static
  binary. Distribution and NAS packages can lag upstream fixes.
- Docker Desktop: version, whether automatic update checks are on, and whether the installed version is
  still within the vendor's supported window.
- Compose version (v2 plugin vs. the retired standalone v1 `docker-compose`).
- Host OS patch level and kernel: containers share the host kernel, so a kernel vulnerability is a
  container-escape vulnerability.
- cgroup version (`docker info`): Docker's release notes deprecate cgroup v1 and advise migrating to v2;
  note hosts still on v1.

#### B. Daemon and API access

- Socket permissions and the members of the `docker` group (or whoever can reach the rootless or Podman
  socket). Every member is a host administrator; check whether that is understood and intended.
- **TCP listeners:** `-H tcp://` in the service unit or `hosts` in `daemon.json`. Docker deprecated
  unauthenticated TCP and, since Engine 27.0, refuses to start with TLS explicitly disabled on a
  non-localhost TCP address; older engines and other runtimes don't enforce this. Confirm with `ss` what
  actually listens on 2375/2376 and on which addresses.
- If TCP with TLS is used: client certificate verification on (`tlsverify`), who holds client
  certificates, where the CA key is, and expiry. TLS without client verification authenticates nobody.
- Prefer SSH contexts (`ssh://`) for remote access; check which accounts and keys can use them.
- `localhost`-only TCP listeners: still reachable by every local user and process, and historically
  exposed to cross-site request forgery from a browser on the same machine.
- Docker Desktop on Windows: the setting **Expose daemon on tcp://localhost:2375 without TLS** (off by
  default; Hyper-V backend only). Docker warns it can lead to remote code execution.
- Docker Desktop on macOS: whether **Allow the default Docker socket to be used** is on (creates
  `/var/run/docker.sock` for third-party tools).
- Remote management: Portainer, Portainer agents, Dockge, Yacht, CI runners, monitoring agents, and
  socket proxies. Each one with socket access is an administrator; check its authentication, exposure,
  and update state. A socket proxy that allows `POST` to containers is not a meaningful restriction.
- Other hosts' `docker context` entries pointing at this host, and this host's contexts pointing
  elsewhere.

#### C. Daemon defaults, rootless mode, and user namespaces

- Rootless mode or user-namespace remapping (`userns-remap`), or neither. Both are off by default in
  rootful Docker. Note the trade-offs before recommending either (see Recommend).
- `daemon.json` hardening options: `no-new-privileges` (default for all containers), `icc` (inter-
  container traffic on the default bridge), `live-restore`, `userland-proxy`, `ip` (default bind address
  for published ports), `default-network-opts`, `log-driver` and `log-opts`, `iptables`/`ip6tables`,
  `firewall-backend` (nftables support is newer and documented as experimental; verify on the installed
  version), `insecure-registries`, `registry-mirrors`, `authorization-plugins`, `seccomp-profile`,
  `experimental`.
- `insecure-registries`: plain-HTTP or unverified registries allow image tampering in transit.
- Seccomp and AppArmor/SELinux in use (`docker info` security options); containers that opt out with
  `seccomp=unconfined` or `apparmor=unconfined` (domain E).
- Podman: rootless vs. rootful per container set; `containers.conf` defaults.

#### D. Network exposure and published ports

- Every published port, the address it binds to (`0.0.0.0` / `[::]` = all interfaces), and whether it
  should be reachable from the LAN, other VLANs, or the internet. Separately check IPv6: a host with a
  global IPv6 address may expose ports with no NAT in front.
- **Firewall interaction (Linux):** ufw and plain `INPUT` rules don't filter published container ports.
  Check for filtering in the `DOCKER-USER` chain (Docker's documented place for user rules), firewalld's
  `docker` zone (Docker creates it with target `ACCEPT`), and the upstream firewall. Note that rules in
  `DOCKER-USER` see traffic after DNAT, so they must match on the container address or use conntrack's
  original-destination match.
- Engine version and published-to-localhost ports: Docker documents that before 28.0, hosts on the same
  layer-2 segment could reach ports published only to `127.0.0.1`. Check the Engine version where
  localhost binding is relied on.
- Bridge gateway modes and direct routing: `nat-unprotected` or `routed` gateway modes and
  `allow-direct-routing` change what other hosts can reach. Treat any non-default mode as needing review.
- `network_mode: host` / `--network host`: the container shares the host's network stack; every port it
  listens on is a host port, and port mappings are ignored.
- **macvlan and ipvlan networks:** containers get their own LAN addresses and bypass the host's packet
  filter entirely; the network firewall is the only control. The host usually can't reach them directly.
- **Docker Desktop:** published ports listen on all host interfaces by default and are reachable from the
  local network, through the Desktop backend process. Check whether the default bind address was changed
  to localhost in Desktop's network settings, whether the host OS firewall allows inbound connections to
  the backend process, and (macOS) the privileged-port forwarding settings. Host networking is opt-in in
  Desktop 4.34 and later and isn't available with Enhanced Container Isolation.
- Reverse proxies (Traefik, Caddy, nginx, Nginx Proxy Manager) and tunnels (for example a Cloudflare
  Tunnel container): every routed hostname is an exposure. Backends should normally bind to a proxy-only
  network or `127.0.0.1`, not to all interfaces as well. A proxy that reads the Docker socket for
  auto-discovery is an administrator (domain B).
- UPnP on the router mapping container ports, and swarm-published ports on every node.

#### E. Container privileges and isolation

For every container (running and stopped), record:

- `privileged: true`. Docker documents that a privileged container "can then do almost everything that
  the host can do": all capabilities, no default seccomp or AppArmor profile, all host devices, writable
  `/sys` and cgroups. Treat it as host root unless the user can show a contained alternative.
- **Runtime socket mounts:** `/var/run/docker.sock`, `/run/docker.sock`, `/run/containerd/containerd.sock`,
  Podman sockets, or a parent directory containing them. Read-only (`:ro`) socket mounts still allow full
  API use. Every such container is a host administrator; list why it needs it.
- Added capabilities (`cap_add`), especially `SYS_ADMIN`, `NET_ADMIN`, `SYS_PTRACE`, `SYS_MODULE`,
  `DAC_READ_SEARCH`, `ALL`; and whether unneeded default capabilities are dropped (`cap_drop: [ALL]`
  plus only what's required).
- Host namespaces: `network_mode: host`, `pid: host`, `ipc: host`, `uts: host`, `userns_mode: host`.
- Devices passed through (`devices:`, `/dev` mounts), and device cgroup rules.
- `security_opt`: `seccomp=unconfined`, `apparmor=unconfined`, `label=disable`, and whether
  `no-new-privileges:true` is set.
- Run-as user: `user:` set to a non-root UID, or the image's default (often root). Root in a container
  without user namespaces is root on the host's kernel if anything else goes wrong.
- `read_only: true` root filesystem with `tmpfs` for writable paths, where the application allows it.
- Resource limits: memory, CPU, `pids_limit`. Missing limits let one container starve the host
  (availability, and a fork bomb takes everything down).
- Sysctls set per container, and any container running its own Docker (`docker:dind`), which needs
  privileged mode.

#### F. Mounts, volumes, and data protection

- Bind mounts of `/`, `/etc`, `/root`, `/home`, `/var/lib/docker`, `/proc`, `/sys`, `/dev`, `/boot`, the
  NAS volume root, or whole data shares. Each writable one is a path to host compromise or bulk data
  loss.
- Writable vs. read-only: mounts that only need reading should be `:ro`.
- Sensitive files mounted into containers: SSH keys, cloud credentials, kubeconfig, other services'
  configuration directories.
- Named and anonymous volumes: which hold irreplaceable data (databases, application state), and
  orphaned volumes nobody can attribute (inventory only; never prune in Discover).
- **Backups:** whether volume data and bind-mounted application data are backed up off the host, whether
  databases are dumped consistently (a live file copy of a running database can be unusable), whether
  Compose files and `.env` files are backed up (and protected, since they hold secrets), and whether a
  restore has ever been tested.
- Docker's data root (`/var/lib/docker` or the configured `data-root`): on which disk, free space, and who
  can read it (it contains every container's filesystem and volume contents).

#### G. Images, provenance, and scanning

- For each running container: image repository, tag, **digest**, publisher, and image age.
- Floating tags (`latest`, `stable`, bare major versions) on important services: updates become
  unreviewed and rollback targets are unclear. Digest pinning, or at least pinned version tags, is
  expected for anything security-relevant.
- Provenance: Docker Official Images, Verified Publisher images, the upstream project's own registry, or
  an unknown individual's repository. Look for typosquatted names and images that duplicate an official
  one.
- **Abandoned images:** no updates in a long time, an archived upstream repository, or a maintainer
  notice. An abandoned image keeps its vulnerabilities forever.
- Registries configured and used (Docker Hub, GHCR, Quay, a private registry), authentication to them, and
  `insecure-registries`.
- Docker Content Trust: Docker announced its retirement in 2025, and Official Images no longer carry DCT
  signatures. Clients with `DOCKER_CONTENT_TRUST=1` will fail pulls; don't recommend DCT. Signature
  verification today means Sigstore/cosign or Notary Project signatures and attestations where the
  publisher provides them (verify the current options).
- Scan results with Docker Scout, Trivy, or Grype (with approval; see baseline). Validate high and
  critical hits per core triage: many are in packages the application never loads, and a clean scan
  doesn't prove safety. Prioritize images that are exposed (domain D) or privileged (domain E).
- Locally built images: Dockerfiles that run as root, `ADD` from URLs, `curl | sh`, secrets in `ARG` or
  `ENV`, base images pinned or not, and build cache or registries that others can push to.

#### H. Secrets

- Credentials in `environment:` blocks of Compose files, in `.env` files, in `docker run -e` history, in
  image `ENV`/`ARG` layers (`docker history`), and in labels. Report the location and type, never the
  value.
- `.env` and Compose file permissions, and whether they are in a git repository (including history) or
  synced to cloud storage.
- Use of Compose `secrets:` (mounted as files under `/run/secrets/`) or `_FILE` environment variable
  conventions where the image supports them. Docker documents that environment variables are easily
  exposed to other processes, are hard to audit, and end up in logs.
- Secrets printed in container logs (startup banners, debug output, initial admin passwords).
- Registry credentials in `~/.docker/config.json` (stored in plain base64 unless a credential helper is
  configured): which accounts, and whether a credential store is used. Check existence and helper
  configuration only.
- Docker Desktop: whether sign-in tokens and registry credentials use the OS keychain or credential
  manager.

#### I. Updates, auto-updaters, and restart behavior

- How images get updated: manually, by a Compose workflow, by Renovate/Dependabot pull requests, or by an
  auto-updater (Watchtower, its forks, What's Up Docker, Diun, or a NAS's built-in update feature).
- **Auto-updaters:** benefit: security fixes arrive without anyone remembering. Risk: they pull whatever
  the tag points to, so a compromised or broken upstream image goes live unreviewed; they need the Docker
  socket (domain B); and the original `containrrr/watchtower` project was archived in December 2025 and no
  longer receives fixes. Check which updater and version, whether it is notify-only or applies updates,
  which containers it covers (all, or a labeled opt-in list), and whether updates are logged.
- Containers whose image is far behind upstream, and stacks nobody has updated since deployment.
- Restart policies: `always` or `unless-stopped` on services that should run; also containers that
  restart in a loop (a crash loop can hide a broken or tampered service), and stopped containers with
  `always` that will come back at the next daemon start.
- Health checks, and a rollback path (previous digest recorded, data backed up before upgrades).

#### J. Networks between stacks

- Containers on the default `bridge` network: they can reach each other (unless `icc` is off) and have no
  name resolution; user-defined networks per stack are expected.
- Shared networks joining unrelated stacks (for example one big `proxy` network that every container is
  on, letting any compromised app reach every other app's database). Backends should be on per-stack
  internal networks; only the proxy-facing container joins the proxy network.
- `internal: true` networks for databases and other services that need no egress.
- Egress: which containers need internet access at all. Containers on bridge networks can usually reach
  the whole LAN and the internet by default.
- Containers that can reach the host's management services, the NAS admin UI, or the router.

#### K. Logging and monitoring

- Log driver per container and the daemon default. `json-file` is the default and does not rotate by
  default; Docker recommends the `local` driver (rotates by default) or `json-file` with `max-size` and
  `max-file`. Unrotated logs can fill the disk and take down every container.
- Whether container and daemon logs (journald for `dockerd`) are shipped off the host, so an attacker on
  the host can't erase them.
- Docker events (container create/start, exec, image pull) recorded anywhere? `docker exec` into
  containers is otherwise invisible after the fact.
- Host auditing of the socket and Docker files (for example auditd rules), where the user wants it.
- Monitoring for unexpected new containers, images, or published ports.

#### L. Docker Desktop specifics

- Version and update state (domain A); Desktop has had container-to-host and container-to-Engine-API
  issues fixed in point releases, so check the security announcements page against the installed
  version.
- **Enhanced Container Isolation (ECI):** off by default; requires sign-in and a Docker Business
  subscription. When on, containers run with user namespaces under the Sysbox runtime, socket mounts are
  blocked by default (with admin-defined exceptions), and host PID/network namespace sharing is blocked.
  It does not yet protect extension containers, and not every advisory is mitigated by ECI. If the
  subscription doesn't include it, record that rather than recommending it.
- Settings Management and Registry Access Management (business features): whether settings are locked by
  an administrator and which registries are allowed.
- File sharing: which host directories are shared into the VM (broad shares such as the whole home
  directory give containers access to SSH keys and cloud credentials when bind-mounted).
- Exposed daemon (Windows TCP 2375 setting), default-socket setting (macOS), host networking, privileged
  port forwarding to external machines (macOS), and default port bind address.
- Extensions installed: each extension runs with access to the Docker API; review publisher and need.
- Sign-in enforcement for organizations, and whether the machine is a shared workstation.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on it:

- **Clients of each published port:** users, apps, other hosts, reverse proxies, and tunnels. Rebinding a
  port to localhost breaks every direct client.
- **Tools that use the Docker socket or API:** Portainer, reverse proxies with Docker discovery,
  auto-updaters, monitoring, CI runners, backup tools, other hosts' contexts. Removing a socket mount or
  TCP listener breaks them.
- **Data location:** which volumes or bind mounts hold the container's data. Recreating a container that
  keeps state in its writable layer or an anonymous volume can lose it.
- **File ownership:** changing the run-as user, enabling user namespaces, or moving to rootless changes
  which UID owns files in volumes and bind mounts; the application may fail to read its own data.
- **Daemon-wide changes** restart every container on the host and may change networking for all of them.
- **Networks:** containers that resolve each other by name across a shared network break when split.
- **Updates:** a version-tag change can include breaking changes or database migrations that can't be
  rolled back without a backup.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Unauthenticated TCP API (2375) | Remove the TCP listener; use the local socket or SSH contexts. If TCP is required, use TLS with client verification and firewall it to admin hosts. | Remote tools using `tcp://` break until moved to SSH or given client certificates. |
| Broad `docker` group | Remove users who don't administer the host; document that membership is root. | Those users need `sudo` or lose container management. |
| Socket mounted into apps | Remove where not essential; for tools that need it, use a filtering socket proxy allowing only read endpoints they need, and keep them off untrusted networks. | Auto-discovery, dashboards, or updaters stop working or need reconfiguration. |
| Privileged containers | Replace `privileged` with the specific capabilities and devices required. | Needs testing per application; some hardware-access workloads genuinely need device passthrough. |
| Excess capabilities / host namespaces | `cap_drop: [ALL]` plus required caps; remove `pid: host`, `network_mode: host` where not needed. | Apps relying on them fail until fixed; host-network apps need port publishing instead. |
| Runs as root | Set `user:` to a non-root UID, or choose an image that supports it; add `no-new-privileges`. | File ownership in volumes must be changed; some images can't run unprivileged. |
| Writable root filesystem | `read_only: true` with `tmpfs` for scratch paths, where the app tolerates it. | Trial and error to find paths the app writes to. |
| No user isolation on host | Rootless Docker or Podman for new deployments; `userns-remap` only with its trade-offs. | `userns-remap` hides existing images and containers and is incompatible with host network/PID and `privileged`; rootless can't bind ports below 1024 by default and limits resource controls. Both are migration projects. |
| Ports on all interfaces | Bind to `127.0.0.1` (and `[::1]`) behind a reverse proxy, or to a specific interface; set the daemon `ip` default to `127.0.0.1` for new containers. | Direct LAN clients break; Swarm services ignore the default. |
| ufw/host firewall relied on | Filter published ports in `DOCKER-USER` (or the nftables equivalent) or upstream; don't set `iptables: false`. | Docker documents that disabling its iptables management is likely to break container networking. Test rules carefully: they can cut off every container. |
| macvlan exposure | Restrict at the network firewall; move to bridge networks behind a proxy if direct LAN presence isn't needed. | The container's LAN address changes; clients and DNS records need updating. |
| Broad bind mounts | Mount only the needed subdirectories, read-only where possible. | Path changes inside the container may need app configuration. |
| Floating tags / unknown publishers | Pin versions (digest for critical services); prefer official or upstream images; replace abandoned images. | Updates now need a deliberate step; replacing an image can change configuration and data layout. |
| Unmaintained auto-updater | Replace the archived Watchtower with a maintained tool, prefer notify-only or opt-in labels, and pair updates with backups. | Some updates stop happening automatically; someone must act on notifications. |
| Secrets in environment | Move to Compose `secrets` or `_FILE` variables; tighten `.env` permissions; keep secrets out of git; rotate any secret already exposed. | Images without file-based secret support need workarounds; rotation affects connected systems. |
| Shared flat network | One internal network per stack; only proxy-facing containers on the proxy network; `internal: true` where no egress is needed. | Cross-stack name resolution breaks; plan which links are real. |
| No log rotation | Use the `local` driver or `json-file` with `max-size`/`max-file`; ship logs off the host. | Applies to newly created containers only, so existing ones must be recreated. |
| No volume backups | Back up volume and bind-mount data, with consistent database dumps, to a separate system; test a restore. | Needs storage and scheduling; dumps may need brief load. |
| Docker Desktop exposure | Update Desktop; set the default bind address to localhost; disable TCP 2375 exposure; enable ECI where the subscription includes it. | ECI blocks socket mounts and host networking that some tools rely on. |

Changing published port numbers, hiding admin pages, and "security through obscurity" image names are
supplementary only. Never recommend them as the main fix.

Group the plan: immediate containment (an unauthenticated API or a privileged, socket-holding container
exposed to untrusted networks) → urgent fixes (exposed admin UIs, critical runtime updates) →
high-priority hardening (privileges, mounts, secrets) → routine maintenance (image updates, logging) →
optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Container specifics:

- **Before any change:** copy the Compose file and `.env` (store the copy as secret material), record the
  current image digest of each affected container, and back up its volume data. For daemon changes, copy
  `daemon.json` and the service unit.
- **Change the declaration, then recreate.** Edit the Compose file (or the NAS manager's project) rather
  than using `docker update` or ad hoc `docker run` commands, so the fix survives the next recreate.
  Recreate one service at a time (`docker compose up -d <service>`), check its logs and health, then move
  on.
- **Pin before recreating.** If the tag is floating, pin it to the currently running digest first, so the
  recreate changes only the setting you meant to change, not the image too.
- **Daemon changes** (`daemon.json`, service unit): C2 for the whole host. Validate the file
  (`dockerd --validate --config-file <path>` on recent engines; verify the flag exists), schedule a window,
  and have console or out-of-band access in case the daemon fails to start. Enabling `userns-remap` on an
  existing host hides existing images and containers; treat it as a migration, not a toggle.
- **Firewall rules for published ports:** add `DOCKER-USER` rules (or nftables equivalents) with a
  `RELATED,ESTABLISHED` accept first, test from an allowed and a blocked client, and make the rules
  persistent with the host's normal mechanism. Keep a session open while applying.
- **Removing a TCP listener or socket mount:** move the dependent tool first (SSH context, socket proxy),
  confirm it works, then remove the old path.
- **Image updates:** update one stack at a time, read the release notes for breaking changes and database
  migrations, back up first, and record the old digest as the rollback target.
- **Docker Desktop:** change settings in the app (or the admin console if managed); updating Desktop
  restarts the VM and every container in it.
- After each change, re-run the relevant Discover commands (ports, `inspect` fields, `ss`, packet-filter
  rules) and record before and after (core: tool-use contract).

### Hard stops (refer to a specialist; never automate)

- `docker system prune`, `docker volume prune`, `docker compose down -v`, deleting volumes, or deleting
  the Docker data root as "cleanup" or remediation.
- Docker Desktop "Reset to factory defaults" or "Clean / Purge data", or `podman system reset`: they
  delete all containers, images, and volumes.
- Setting `iptables: false` (or the nftables equivalent) on a running host to "fix" firewall bypass.
- Bulk updates: pulling and recreating every stack at once, or running an auto-updater against all
  containers as a remediation step.
- Moving the data root, changing the storage driver, or switching an existing host to `userns-remap` or
  rootless in place without a tested migration and backups.
- Editing files inside `/var/lib/docker` by hand.
- Running untrusted "security fix" containers or scripts that need the socket or `--privileged`.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the container-specific
steps in [incident-response.md](incident-response.md).

P0 indicators specific to containers include: an unauthenticated Docker or Podman API reachable from
untrusted networks with unexplained containers on the host; containers nobody created (especially
privileged ones, ones mounting `/` or the socket, or cryptocurrency miners); unexpected `docker exec`
activity; and images replaced under a pinned-looking tag.

---

## Worked example (invented)

### DKR-001: Docker API exposed on TCP 2375 without TLS

**Confidence:** Confirmed
**Priority:** P1. Anyone who can reach the port can start a privileged container that mounts the host's
root filesystem, which is full control of the host and its data. Not P0 because it is reachable only from
the LAN and no indicators of misuse were found.
**State:** Open
**Component:** Docker Engine 26.x on a Linux host (`<container-host>`, `192.0.2.20`)
**Evidence:** Observed 2026-10-12: `systemctl cat docker.service` shows `-H tcp://0.0.0.0:2375`; `ss
-ltn` shows `dockerd` listening on `0.0.0.0:2375` and `[::]:2375`. With approval, a version query from
admin workstation `192.0.2.50` returned the Engine version over plain HTTP. `docker ps -a` lists only the
user's known containers; no unexpected images.
**Expected secure state:** API reachable only through the local socket or SSH; any TCP listener uses TLS
with client certificate verification (Docker Engine documentation, remote access and socket protection).
Docker Engine 27.0 and later refuse to start with TLS disabled on a non-localhost TCP address.
**Exposure and prerequisites:** any device on the LAN, including IoT and guest devices if not segmented;
no credentials required.
**Dependencies / blast radius:** a dashboard on another host connects via `tcp://192.0.2.20:2375`.
**Recommended remediation:** move the dashboard to an SSH context or a socket proxy on the host, then
remove the `-H tcp://` flag (systemd drop-in) and restart the daemon in a maintenance window. Then update
the Engine to a supported release. Review `docker ps -a`, images, and events since the listener was added.
**Operation class:** C2 (daemon restart stops all containers; changes the dashboard's access path).
**Approval required:** Yes.
**Verification:** `ss -ltn` shows nothing on 2375; a version query from `192.0.2.50` fails; the
dashboard works over its new path; all containers are back up.
**Rollback:** restore the saved service unit and restart the daemon (not recommended; use TLS instead).

---

## Version history

- **1.0** (2026-10-30): Initial version.
