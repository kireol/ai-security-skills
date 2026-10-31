# GPU Hosts: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only GPU-host-specific steps.

## Triage and containment

- **Cut network access, keep the machine running.** Remove port forwards, tunnels, and share links, and
  block the host at the router or switch (or detach the VM's virtual NIC on a hypervisor). Volatile
  evidence (running processes, GPU process list, network connections, loaded containers) is lost on reboot.
- **Don't kill the miner first.** Record the process, its parent, its container (if any), its command
  line, and its network connections, then stop it with the user's approval. Killing it first loses the
  trail back to how it started.
- **Stop exposed notebooks and dashboards** after recording their configuration and logs: an open notebook
  lets the attacker back in as fast as you remove them.
- **Pause automated jobs that pull new code or images** (scheduled training scripts, CI runners, image
  auto-updaters) until the entry point is known.
- **Revoke cloud and model-hub tokens from a clean device** if they were on the host; a stolen cloud key
  can rack up GPU bills far larger than the local damage.

## Evidence to preserve (GPU-host-specific)

- `nvidia-smi` and `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv` output (or
  `rocm-smi`/`amd-smi` on AMD), with the time collected.
- Process list with parents and command lines, and network connections (`ss -tnp`), for every
  GPU-using process.
- Container list, images and digests, start commands, mounts, and GPU/privilege settings
  (`docker inspect`), plus Kubernetes pod specs if applicable.
- Jupyter server logs, the list of running kernels and terminals, notebooks and files modified in the
  incident window, IPython history databases, and shell histories of notebook users.
- Logs of model servers, ML dashboards (job submissions in Ray, MLflow runs), and remote-access tools.
- `config.toml`, `daemon.json`, CDI specs, and the toolkit and driver versions (to check whether a known
  container-escape flaw applied).
- GPU utilization history from monitoring, which can date the start of abuse.
- Cron jobs, systemd units and timers, startup items, SSH authorized keys, and new users.

## Scope checks specific to a GPU host

- Every secret the host or its notebooks held: model-hub tokens, cloud keys, experiment-tracker keys, SSH
  keys, database credentials. Check provider logs for their use.
- Cloud accounts linked to those keys: new instances (especially GPU instances), new users, billing.
- The hypervisor (for passthrough or vGPU), and other containers or VMs sharing the GPU or the host.
- Shared storage the host mounts (datasets, model stores, NAS shares): files changed or added, including
  model files that execute code on load.
- Other machines reachable with the host's SSH keys or credentials.

## Eradication and recovery

- If a container-escape flaw applied or root was obtained, rebuild the host operating system rather than
  cleaning it. Reinstall the driver and Container Toolkit from the vendor's repository at a fixed version.
- Rebuild containers from verified images and pinned digests; don't reuse their secrets.
- Rotate every secret that was on the host or in notebooks, including those in saved outputs and
  checkpoints.
- Restore notebooks, code, and models from backups taken before the earliest plausible compromise, and
  re-download models from their original publisher rather than trusting copies on the host.
- Before reconnecting: notebooks and dashboards bound to localhost or authenticated, no default GPU
  runtime for all containers, no privileged GPU containers, remote access through one authenticated path,
  GPU utilization monitoring and alerting in place, and the initial access path closed.

## Quick checklist tailored for a GPU host

When the user says "my GPU is at 100% and I'm not running anything," start with the core quick
checklist, plus:

- [ ] From a clean device, remove port forwards, tunnels, and share links; block the host at the router,
      without powering it off.
- [ ] Record `nvidia-smi` process output, the process tree, network connections, and the container list
      before stopping anything.
- [ ] Revoke cloud and model-hub tokens that were on the host; check cloud billing for new GPU instances.
- [ ] Check for open notebooks, ML dashboards, and new SSH keys or remote-access tools.
