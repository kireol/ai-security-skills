# Docker and Containers: References

Always prefer current vendor documentation. Docker Engine, Docker Desktop, and Podman change defaults
between releases (port binding, firewall backends, TLS enforcement), so re-verify links and contents when
updating this skill.

Last verified: 2026-10-30

## Vendor (authoritative)

- Docker security announcements (Docker Desktop and other products): https://docs.docker.com/security/security-announcements/
- Moby (Docker Engine) security advisories: https://github.com/moby/moby/security/advisories
- Docker Engine release notes: https://docs.docker.com/engine/release-notes/
- Docker Desktop release notes: https://docs.docker.com/desktop/release-notes/
- Docker Engine deprecated features (unauthenticated TCP, cgroup v1, and others): https://docs.docker.com/engine/deprecated/
- Docker Engine security overview (daemon attack surface, capabilities, user namespaces): https://docs.docker.com/engine/security/
- Protect the Docker daemon socket (TLS, SSH): https://docs.docker.com/engine/security/protect-access/
- Configure remote access for the daemon (ports 2375/2376): https://docs.docker.com/engine/daemon/remote-access/
- Linux post-install steps (`docker` group grants root-level privileges): https://docs.docker.com/engine/install/linux-postinstall/
- Rootless mode and its tips and limitations: https://docs.docker.com/engine/security/rootless/ and
  https://docs.docker.com/engine/security/rootless/tips/
- User namespace remapping (`userns-remap`): https://docs.docker.com/engine/security/userns-remap/
- Seccomp profiles: https://docs.docker.com/engine/security/seccomp/
- `docker run` reference (`--privileged`, capabilities, `--read-only`, `no-new-privileges`): https://docs.docker.com/reference/cli/docker/container/run/
- Port publishing (default all-interfaces binding, localhost binding, gateway modes, pre-28.0 L2 note): https://docs.docker.com/engine/network/port-publishing/
- Packet filtering and firewalls (ufw incompatibility, firewalld zone, nftables backend): https://docs.docker.com/engine/network/packet-filtering-firewalls/
- iptables and the `DOCKER-USER` chain: https://docs.docker.com/engine/network/firewall-iptables/
- Host network driver (including Docker Desktop 4.34+ support and limits): https://docs.docker.com/engine/network/drivers/host/
- Logging drivers and rotation: https://docs.docker.com/engine/logging/configure/
- Live restore: https://docs.docker.com/engine/daemon/live-restore/
- Restart policies: https://docs.docker.com/engine/containers/start-containers-automatically/
- Compose secrets: https://docs.docker.com/compose/how-tos/use-secrets/
- Docker Desktop settings (exposed daemon, default socket, host networking, ECI toggle): https://docs.docker.com/desktop/settings-and-maintenance/settings/
- Docker Desktop networking (published ports on all interfaces, backend process, firewall filtering): https://docs.docker.com/desktop/features/networking/
- Docker Desktop for Linux (runs a VM, `desktop-linux` context): https://docs.docker.com/desktop/setup/install/linux/
- Enhanced Container Isolation: https://docs.docker.com/enterprise/security/hardened-desktop/enhanced-container-isolation/
- Docker Scout CLI: https://docs.docker.com/reference/cli/docker/scout/
- Retirement of Docker Content Trust (2025): https://www.docker.com/blog/retiring-docker-content-trust/
- Podman API service (socket paths, warnings against TCP exposure): https://docs.podman.io/en/latest/markdown/podman-system-service.1.html
- Podman security advisories: https://github.com/containers/podman/security/advisories
- Product lifecycle: Docker doesn't publish a single fixed support period for Engine releases on the
  release-notes page; check the release notes and your distribution's or NAS vendor's support policy for
  the installed version.

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- CIS Docker Benchmark: https://www.cisecurity.org/benchmark/docker
  Consensus hardening checklist (host configuration, daemon configuration and files, images and build
  files, container runtime, security operations, Swarm). The full PDF needs a free CIS registration; check
  which Docker version the current benchmark release covers.
- Docker Bench for Security: https://github.com/docker/docker-bench-security
  Script that checks a host against an older CIS Docker Benchmark release. Check its maintenance status and
  benchmark version before relying on it; it needs broad host access, so treat running it as an approved
  action.
- Trivy (image, filesystem, and configuration scanner): https://trivy.dev/
  Useful open-source scanner. Its release artifacts were compromised in a March 2026 supply-chain attack;
  install only verified releases and check the project's current security notices.
- Grype (image vulnerability scanner): https://github.com/anchore/grype
  Open-source scanner; validate findings per core triage.
- Watchtower (original project, archived December 2025): https://github.com/containrrr/watchtower
  Listed for identification only; it no longer receives fixes. Evaluate any fork or alternative on its own
  maintenance record.
