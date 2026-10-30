# Docker and Containers: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only container-specific steps.

Two situations look similar but scope very differently: a **compromised container** (an application was
exploited, and the attacker has that container's privileges, mounts, network, and secrets) and a
**compromised host or runtime** (the attacker reached the Docker API, socket, or host, and controls every
container). A container that was privileged, held the runtime socket, used host namespaces, or had a
writable mount of a host system path counts as a host compromise until shown otherwise.

## Triage and containment

- **Indicators:** containers or images nobody created (often with random names, miner images, or
  `alpine`/`ubuntu` images running shell commands); containers that mount `/` or the socket or run
  `--privileged`; unexpected `docker exec` sessions; new published ports; a container using high CPU with
  no explanation; outbound connections to mining pools or unknown hosts; changed Compose files, `.env`
  files, or `daemon.json`; new users in the `docker` group; a new TCP listener on 2375/2376; an image
  digest that no longer matches the recorded one.
- **Contain without destroying evidence.** Prefer, with approval:
  - Disconnect the container from its networks (`docker network disconnect <network> <container>`) or
    remove its published-port exposure at the firewall, which keeps it running for evidence.
  - `docker pause <container>` freezes its processes in place (memory preserved) while you collect
    evidence. Note that paused containers can still be inspected but not exec'd into.
  - If the runtime API is exposed, block the port upstream (network firewall) first, then remove the
    listener.
- **Don't** `docker rm`, `docker compose down`, prune, or recreate the container before evidence is
  collected: removal deletes its writable layer, which is often the only record of what the attacker
  dropped. Don't `docker restart` it either; restart loses process and memory state.
- **Disable auto-updaters and restart automation** for affected stacks, so evidence isn't replaced by a
  fresh pull or a restart policy, and so a malicious upstream image isn't pulled again.
- **If the host may be compromised,** contain at the network (switch port, VLAN, upstream firewall, or
  hypervisor) rather than trusting the host's own tools, and work from a separate admin workstation.
- **Docker Desktop:** disconnect the workstation from the network if a container-to-host escape is
  suspected; the incident then includes the workstation and the user's accounts.

## Evidence to preserve (container-specific)

Collect before changing anything, and treat all of it as secret material (it contains environment
variables and credentials):

- `docker ps -a --no-trunc` and `docker inspect <container>` for affected and unexpected containers,
  saved to files rather than printed in chat.
- `docker diff <container>`: files added, changed, or deleted in the container's writable layer.
- `docker export <container>` (filesystem tarball) or `docker commit` to a new image name, for later
  analysis. Commit doesn't include volume contents; copy those separately.
- `docker logs --timestamps <container>` and the daemon's logs (`journalctl -u docker` on systemd hosts).
- `docker events --since <time> --until <time>` for the window of interest (create, start, exec, pull,
  attach); daemon events are only kept in memory for a limited period, so collect early.
- Image metadata: `docker image ls --digests`, `docker history --no-trunc <image>`, and
  `docker image inspect` for unknown images. Save unknown images with `docker save` before anything
  removes them.
- Compose files, `.env` files, `daemon.json`, service units and drop-ins, `docker` group membership, and
  shell history of administrative accounts.
- Network state: published ports (`docker ps`), `ss -tanp`, `iptables -S` / `nft list ruleset`, and
  `docker network inspect` for networks the container was on.
- Volume and bind-mount contents the container could write to (copy or snapshot the underlying storage).
- On a NAS or a VM host: a storage snapshot or VM snapshot of the container host before cleanup.
- Docker Desktop: Desktop's diagnostics bundle (Troubleshoot → gather diagnostics; verify the menu on the
  installed version) and the host OS's process and network logs. Don't use the reset or purge options.

## Scope checks specific to containers

- **Every secret the container could read:** its environment, `/run/secrets`, mounted configuration and
  key files, and credentials in its volumes (database passwords, API tokens, cloud keys, OAuth client
  secrets, SMTP and notification tokens). Treat them as stolen.
- **Everything the container could reach:** other containers on its networks (shared proxy networks
  especially), databases, the host's services, the LAN, and the NAS. Check those for follow-on access.
- **If the container had the socket, privileged mode, host namespaces, or a writable host mount:** treat
  the host and every container on it as compromised, plus every host the host's credentials reach.
- **Registries and build pipelines:** if images were pushed or rebuilt, check registry accounts, CI
  tokens, and whether other hosts pulled a tampered image.
- **Other hosts sharing the same images, Compose repositories, or auto-updater configuration.**
- **Data in writable mounts:** check for encryption, deletion, or tampering (core: ransomware section).
- **Docker Desktop:** the user's home directory files shared into the VM, browser sessions, SSH keys, and
  cloud CLIs on the workstation.

## Eradication and recovery

- Don't clean a compromised container; **rebuild it** from a trusted image (verified digest from the
  publisher, or rebuilt from reviewed source) and a reviewed Compose file. Don't reuse the old container's
  writable layer or any image the attacker could have modified.
- Review volumes before reattaching them: application data may contain web shells, modified
  configuration, or planted plugins. Restore from a backup taken before the earliest plausible
  compromise where integrity is in doubt.
- If the host or runtime was compromised, rebuild the host (core: eradication and trusted recovery),
  reinstall the runtime from the vendor's repository, and redeploy stacks from reviewed files. A Docker
  Desktop compromise that may have reached the host means treating the workstation as compromised.
- **Rotate every secret in scope:** application credentials, database passwords, API tokens, registry
  credentials, TLS client certificates and the CA if the API used TLS, SSH keys on the host, and
  credentials for any connected system.
- Close the entry path before reconnecting: patch the exploited application or runtime, remove the
  exposed API or port, remove unnecessary privileges and socket mounts, and pin images by digest.
- Reconnect in stages and watch `docker events`, published ports, and outbound traffic before restoring
  full network access.

## Quick checklist tailored for containers

Start with the core quick checklist, plus:

- [ ] Decide early: container compromise, or host/runtime compromise (privileged, socket, host
      namespaces, or exposed API means host).
- [ ] Disconnect or pause the container instead of removing it; block exposed API ports upstream.
- [ ] Stop auto-updaters and restart automation for affected stacks.
- [ ] Save `inspect`, `diff`, logs, events, and an export or commit of the container before cleanup.
- [ ] Treat every secret the container could read as stolen, and rotate it.
- [ ] Rebuild from trusted images and reviewed Compose files; don't reuse the old container.
