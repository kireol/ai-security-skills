---
name: gpu-hosts
description: >-
  Security assessment, hardening, remediation, and incident response for hosts with NVIDIA (and, more
  generally, AMD) GPUs used for AI/ML work, notebooks, or media transcoding. Use when auditing a GPU
  workstation or server, reviewing driver and CUDA support status and NVIDIA security bulletins (driver,
  Container Toolkit, GPU Operator), which containers get the GPU and how, privileged GPU containers,
  DCGM/dcgm-exporter exposure, Jupyter and similar notebooks or ML dashboards left open on the network,
  GPU sharing between untrusted workloads (MIG, time-slicing, MPS, vGPU, passthrough), or remote access
  to the workstation, or when a GPU host may have been compromised or used for cryptomining.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "NVIDIA GPU drivers (production and long-term-support branches), CUDA, NVIDIA Container Toolkit, GPU Operator and device plugin, DCGM, Jupyter; AMD ROCm generically (verify each live version)"
  audience: "home, work, homelab"
  finding_prefix: "GPU"
  modes: "discover, recommend, remediate, respond"
---

# GPU Host Security

Act as a careful, evidence-driven security engineer for machines with GPUs. A GPU box is usually the most
expensive and most powerful machine in a homelab, set up quickly by one person to try something, and full
of things attackers want: free compute for cryptomining, cloud and model-hub API keys in notebooks and
environment files, datasets, and a privileged kernel driver that every GPU container talks to directly.
Identify, explain, prioritize, remediate (only when authorized), and verify weaknesses in the GPU
software stack, the way containers and users get GPU access, the notebooks and dashboards that run on
it, and the ways people reach it remotely.

## How to use this skill

This skill holds only GPU-host-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

GPU-host-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md).

Related skills: the model servers that run on these hosts (Ollama, vLLM, ComfyUI, Open WebUI, and others)
are covered by [local LLM servers](../local-llm/SKILL.md); GPU transcoding in Plex, Jellyfin, Emby, and
Tdarr by [media servers](../../media/media-servers/SKILL.md); the operating system by
[Linux](../../operating-systems/linux/SKILL.md) or [Windows](../../operating-systems/windows/SKILL.md);
containers generally by [Docker](../../containers/docker/SKILL.md); GPU passthrough on hypervisors by
[Proxmox VE](../../virtualization/proxmox-ve/SKILL.md) and [VMware ESXi](../../virtualization/vmware-esxi/SKILL.md);
GPU metrics collection by [monitoring](../../monitoring/monitoring/SKILL.md). A GPU server's BMC is covered
by [out-of-band management](../../hardware/out-of-band-management/SKILL.md).

## GPU-host-specific principles

- **A container with the GPU talks to the host kernel driver.** GPU access means the container opens the
  host's `/dev/nvidia*` (or `/dev/kfd` and `/dev/dri` for AMD) device nodes and sends commands straight
  to a large, privileged kernel driver. A driver vulnerability is therefore a container-escape and
  privilege-escalation surface. Patch the driver as you would the kernel.
- **The NVIDIA Container Toolkit runs as root on the host during container creation.** Its hooks prepare
  every GPU container. Flaws in it have allowed a crafted image to escape to the host, so the toolkit
  version matters as much as the runtime's. Running untrusted images with GPU access on an unpatched
  toolkit is running untrusted code as host root.
- **"All GPUs" is the default in many images.** NVIDIA's CUDA base images set `NVIDIA_VISIBLE_DEVICES=all`.
  If the NVIDIA runtime is Docker's default runtime, every container built on those images gets every GPU
  without asking for it. Know which containers really need the GPU.
- **GPU sharing is not isolation unless the hardware says so.** Time-slicing and MPS let several workloads
  share a GPU but don't give them separate, protected memory and fault domains. MIG (on supported
  data-center GPUs) and vGPU do partition the GPU. Consumer GPUs have neither. Treat workloads sharing a
  non-MIG GPU as able to affect each other.
- **Notebooks are remote shells.** Jupyter, JupyterLab, and similar tools run arbitrary code as the user
  who started them, usually with terminals enabled. An open notebook is an open shell on the GPU box.
- **Don't run GPU-intensive or GPU-resetting commands during an assessment.** Changing MIG mode, ECC
  mode, persistence mode, clocks, or power limits, or resetting a GPU, kills running jobs and can need a
  reboot. Reading state with `nvidia-smi` is fine.

## Deployment variants

Identify the variant in Discover. It changes which rules apply.

| Variant | How to recognize it | What changes |
|---|---|---|
| **Linux workstation or server, bare metal** | `nvidia-smi` works on the host; driver from the distribution, NVIDIA's repository, or the `.run` installer. | All guidance applies. How the driver was installed decides how it updates: `.run` installs don't update with the package manager. Secure Boot needs signed modules. |
| **Windows workstation** (often also a gaming PC) | NVIDIA app or GeForce Experience / Studio drivers; CUDA under Windows; maybe WSL2. | Driver updates through NVIDIA's app or manual download; GPU security bulletins list Windows separately. WSL2 shares the Windows driver; Linux containers in WSL2 use the Windows host's driver. Remote-access and game-streaming tools are common. |
| **Docker or Podman with the NVIDIA Container Toolkit** | `nvidia-ctk` present; `nvidia` runtime in `docker info`; CDI specs under `/etc/cdi` or `/var/run/cdi`. | Assess the toolkit version and configuration, the default runtime, and every container's GPU and privilege settings. |
| **Kubernetes** (GPU Operator or NVIDIA device plugin; k3s, MicroK8s, kubeadm) | `nvidia.com/gpu` resources; `gpu-operator` namespace; DCGM exporter pods. | GPU Operator and device plugin versions have their own bulletins. Time-slicing or MIG configuration is in the operator's config. Workload isolation depends on namespaces, admission policy, and pod security. |
| **Hypervisor passthrough** (Proxmox VE, ESXi, others) | GPU bound to `vfio-pci` on the host; driver inside one VM. | The VM owns the whole GPU; host and VM drivers differ. IOMMU groups matter: devices in the same group are passed together. GPU firmware state can persist across VM resets on some cards. |
| **Shared GPU into LXC or several containers** | `/dev/nvidia*` bind-mounted into LXC containers; host driver matched inside. | Every container sharing the device nodes reaches the same kernel driver with no hardware isolation. |
| **vGPU or MIG** | NVIDIA vGPU host driver and license server; `nvidia-smi mig -lgi` shows instances. | vGPU has its own driver branches and bulletins. MIG gives memory and fault isolation between instances on supported GPUs. |
| **Rented GPU or cloud instance** | Public IP; provider console; template images. | Everything bound to all interfaces is on the internet unless the provider's firewall blocks it. Templates often start Jupyter or SSH with weak defaults. |
| **AMD GPUs with ROCm** | `rocm-smi` or `amd-smi`; `/dev/kfd`; `amdgpu` driver. | The same principles apply: device access is kernel-driver access; check AMD's product security bulletins and the ROCm version's support status. AMD's tooling and container integration differ; verify commands on the installed release. |
| **NVIDIA Jetson and other embedded GPU boards** | Jetson Linux (L4T); `tegrastats`. | Separate software stack and bulletins (Jetson Linux / JetPack); check NVIDIA's Jetson security bulletins rather than desktop driver ones. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match. A GPU itself isn't visible
on the network; the services around it are.

- **Jupyter:** TCP 8888 by default (next free port above it for additional servers), page title "Jupyter
  Notebook", "JupyterLab", or "Home Page - Select or create a notebook"; `/api` returns a JSON version
  string. A login page asking for a token or password is the default; a file tree with no login is a
  finding. JupyterHub defaults to TCP 8000.
- **NVIDIA DCGM:** `dcgm-exporter` serves Prometheus metrics on TCP 9400 (`/metrics` with `DCGM_FI_`
  metric names); the standalone `nv-hostengine` uses TCP 5555. Neither has authentication.
- **ML dashboards often on GPU boxes:** TensorBoard (6006), MLflow (5000), Ray dashboard (8265), Gradio
  apps (7860), NVIDIA Triton Inference Server (8000 HTTP, 8001 gRPC, 8002 metrics), code-server (8080).
  Verify each tool's own documentation; ports are configurable.
- **Model servers** (Ollama, vLLM, ComfyUI, and similar): see the Detection section of
  [local LLM servers](../local-llm/SKILL.md).
- **Remote access:** RDP (3389), VNC (5900), SSH (22), NoMachine (4000), and game-streaming hosts such as
  Sunshine (web UI on 47990 by default; verify) are common on GPU workstations.
- **MAC address vendors:** no GPU signal. The host's NIC vendor (or a workstation maker such as Dell, HP,
  Lenovo, or Supermicro) is what shows. NVIDIA (Mellanox) OUIs appear on NVIDIA ConnectX/BlueField
  network adapters, which suggests a data-center-class GPU server.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Candidate read-only commands. Lines marked *vendor-documented* appear in NVIDIA's or the tool's
documentation; the rest are **not yet verified** on every version. Check each exists first.

```sh
nvidia-smi                                   # driver version, CUDA version, GPUs, running processes (vendor-documented)
nvidia-smi -q                                # full query: VBIOS, persistence, ECC, MIG mode (vendor-documented)
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv   # who is using the GPU
nvidia-smi mig -lgi                          # MIG GPU instances, if MIG is enabled (vendor-documented)
cat /proc/driver/nvidia/version              # kernel module version
ls -l /dev/nvidia* /dev/dri/ /dev/kfd 2>&1   # device nodes and who can open them
dpkg -l | grep -iE 'nvidia|cuda'; rpm -qa | grep -iE 'nvidia|cuda'    # how the driver was installed
nvcc --version                               # CUDA toolkit, if installed
nvidia-ctk --version                         # Container Toolkit (vendor-documented)
cat /etc/nvidia-container-runtime/config.toml   # toolkit configuration (vendor-documented path)
nvidia-ctk cdi list                          # CDI device names, if CDI is used (vendor-documented)
docker info --format '{{.DefaultRuntime}} {{json .Runtimes}}'
cat /etc/docker/daemon.json
docker ps --format '{{.Names}}' | xargs -r docker inspect --format \
  '{{.Name}} priv={{.HostConfig.Privileged}} runtime={{.HostConfig.Runtime}} gpus={{json .HostConfig.DeviceRequests}} devices={{json .HostConfig.Devices}}'
docker ps -q | xargs -r docker inspect --format '{{.Name}} {{range .Config.Env}}{{println .}}{{end}}' | grep -E 'NVIDIA_VISIBLE_DEVICES|NVIDIA_DRIVER_CAPABILITIES'
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\\.com/gpu
helm list -A | grep -iE 'gpu-operator|nvidia|dcgm'
ss -tlnp                                     # what listens, on which address
jupyter --version; jupyter server list       # running servers (output includes tokens: redact)
rocm-smi --showdriverversion; amd-smi version   # AMD equivalents, if present
```

- `jupyter server list` prints URLs that contain access tokens. Redact the token before recording.
- `docker inspect` shows environment variables, which can contain secrets; the second command filters to
  the NVIDIA variables only. Record that other secrets exist, not their values.
- On Windows, `nvidia-smi` is installed with the driver; the driver version is also in the NVIDIA app or
  Device Manager.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Driver, CUDA, and support status

- GPU models, driver version and branch, and how it was installed (distribution package, NVIDIA
  repository, `.run` installer, NVIDIA app on Windows, vendor OEM driver).
- Whether the driver branch is still supported. NVIDIA publishes production branches and long-term
  support branches with end-of-life dates for data-center drivers; consumer (Game Ready/Studio) drivers
  follow a different cadence. Check NVIDIA's driver lifecycle page on the day; record the source and date.
- Whether the GPU itself is still supported by current drivers. Older GPU architectures move to legacy
  driver branches that eventually stop receiving security fixes.
- Installed version vs. the latest NVIDIA GPU display driver security bulletin for the platform (Windows
  and Linux are listed separately; vGPU separately again). Core triage applies; match the branch, not just
  the major version.
- CUDA toolkit and libraries: version, whether it's still needed, and whether applications pin old CUDA
  that forces an old driver.
- AMD: amdgpu and ROCm versions vs. AMD's product security bulletins and the ROCm support matrix.

#### B. Container GPU access (NVIDIA Container Toolkit, CDI)

- Container Toolkit and `libnvidia-container` version vs. NVIDIA's Container Toolkit security bulletins.
  Several past flaws let a malicious image escape to the host; patching the toolkit is urgent when the
  host runs images from outside the user's control.
- Is `nvidia` the Docker or containerd **default runtime**? If so, every container whose image sets
  `NVIDIA_VISIBLE_DEVICES` (including every image built on NVIDIA's CUDA base images) gets GPUs.
- Toolkit configuration: whether unprivileged containers may request GPUs through the environment variable
  (`accept-nvidia-visible-devices-envvar-when-unprivileged`) or volume mounts
  (`accept-nvidia-visible-devices-as-volume-mounts`), and whether CDI mode is in use. NVIDIA has issued
  bulletins for non-default settings of these; compare with the current bulletin and docs.
- Each container with GPU access: does it need it? Which GPUs (`all` or specific ones)? Which driver
  capabilities (`NVIDIA_DRIVER_CAPABILITIES=all` adds display, video, and graphics libraries most
  workloads don't need)?
- **Privileged GPU containers:** `--privileged` gives every host device, not just GPUs, and disables most
  container isolation. Many guides use it for GPU access when `--gpus` or CDI would do. Flag each one.
- Device nodes mounted by hand (`--device /dev/nvidia0`) and whether `/dev/nvidiactl` and
  `/dev/nvidia-uvm` came with them.
- Image provenance for GPU images: publisher, digest, and whether they are maintained. ML images are large
  and often pulled from personal registries.
- Kubernetes: GPU Operator and device plugin versions vs. bulletins; pod security admission or policy
  that stops pods requesting privileged mode, host paths, or GPUs without a resource request.

#### C. Local users and device permissions

- `/dev/nvidia*` permissions. The NVIDIA driver creates them world-accessible by default (module options
  can change this), so every local user and every process can use the GPU and reach the driver. On a
  multi-user host, decide whether that is intended.
- Who has shell access to the GPU host, and whether shared accounts are used for convenience.
- GPU access for services: which system users run GPU workloads (model servers, transcoders, notebooks),
  and whether any run as root.

#### D. Notebooks and ML tools

- Every running Jupyter server, JupyterHub, VS Code server, or similar: which user runs it, bind address
  (`ip`), port, and authentication (token, password, or **none**). Look for `--ip=0.0.0.0`,
  `--NotebookApp.token=''` or `--ServerApp.token=''`, empty passwords, `--allow-root`,
  `allow_origin = '*'`, `disable_check_xsrf = True` in `jupyter_server_config.py` or
  `jupyter_notebook_config.py`, and in container commands.
- Whether terminals are enabled (default yes), and what the notebook user can reach: host mounts, Docker
  socket, SSH keys, cloud credentials.
- Jupyter running in a container as root with the home directory or `/` mounted: notebook access becomes
  host access.
- Secrets in notebooks: API keys (model hubs, cloud, experiment trackers) hard-coded in cells, printed in
  saved outputs, or in `.ipynb_checkpoints`. Record files and key types, not values.
- ML dashboards and job APIs (TensorBoard, MLflow, Ray, Gradio apps, Triton): bound to all interfaces?
  Authentication? Some, such as Ray's job API, run submitted code and are designed for trusted networks
  only (check the tool's security documentation for the installed version).
- Exposure through tunnels or "share" links (Gradio `share=True`, ngrok, Cloudflare Tunnel, Tailscale
  Funnel) that put a notebook on the internet.

#### E. GPU monitoring and management services

- `dcgm-exporter` and `nv-hostengine`: running? Bound to which address? Who can reach 9400 and 5555? The
  metrics reveal GPU models, utilization, and process activity; the host engine accepts management
  commands, so it should be local-only or reached only by the monitoring host.
- Other GPU exporters, vendor tools, overclocking or fan-control utilities with web or network
  interfaces.
- NVIDIA vGPU license server or Delegated License Service: exposure and accounts, if used.

#### F. GPU sharing and isolation

- How the GPU is shared: one owner, several containers, time-slicing, MPS, MIG, vGPU, or passthrough to one
  VM.
- Do workloads with different trust levels share a non-MIG GPU (for example, a public-facing model server
  and a personal notebook, or a guest's container)? Without hardware partitioning they can affect each
  other's availability, and GPU memory isolation between processes depends on the driver; research has
  shown GPU memory leaking between processes on some vendors' hardware. Prefer separate GPUs, MIG, or
  separate hosts for untrusted work.
- MIG configuration (where supported): instance layout matches intent; who can change it.
- Passthrough: IOMMU enabled, GPU in its own IOMMU group (or the whole group passed intentionally), and the
  VM that owns the GPU assessed as its own system.

#### G. Remote access to the workstation

- How the user reaches the box: SSH (keys only? exposed?), RDP, VNC, NoMachine, Parsec, Sunshine/Moonlight,
  Chrome Remote Desktop, TeamViewer, AnyDesk, or a VPN. Each listener: bind address, authentication,
  MFA, and whether it is reachable from the internet (check the router and UPnP).
- Game-streaming hosts: admin web UI credentials set, UI bound to localhost or the LAN only, pairing
  requires a PIN, UPnP port mapping off unless intended.
- Remote-support tools left installed and running after one use.
- Wake-on-LAN and BMC power control (assess the BMC with its own skill).

#### H. Resource abuse, monitoring, and logging

- Current and recent GPU utilization vs. expected use; unexpected processes in
  `nvidia-smi --query-compute-apps`; high power draw while idle. Cryptominers are the most common
  payload on exposed GPU hosts.
- Whether GPU metrics are collected somewhere the user looks, with an alert for sustained utilization
  when nothing is scheduled.
- Logs for notebooks, model servers, and remote-access tools kept and forwarded off the host.
- Cloud GPU billing alerts, if applicable.

#### I. Data, models, and secrets

- Datasets and models on the host: where they live, who can read them, whether any are sensitive.
- Model files from untrusted sources in formats that execute code on load (pickle-based checkpoints);
  prefer safer formats (see [local LLM servers](../local-llm/SKILL.md)).
- Secrets on the host: model-hub tokens, cloud keys, experiment-tracker keys, SSH keys, `.env` files.
  Existence, scope, and age only.
- Backups of notebooks, code, and trained models: present, and separate from the host.

#### J. Physical and availability

- Power and cooling for sustained GPU load; UPS coverage (see [UPS](../../hardware/ups/SKILL.md)).
- Physical access to the workstation (USB ports, boot order, BIOS password, disk encryption).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state:

- **Driver version pins:** CUDA applications, PyTorch/TensorFlow builds, containers built for a specific
  CUDA version, vGPU guests that must match the host driver branch, and media servers using NVENC/NVDEC.
  A driver update can break them, and a mismatched kernel module can stop the GPU working until reboot.
- **Running jobs:** training runs and long transcodes stop on driver updates, GPU resets, MIG changes, and
  reboots.
- **Containers that rely on the default runtime:** removing `nvidia` as the default runtime stops every
  container that silently got GPUs that way. List them first and add explicit `--gpus` or CDI requests.
- **Notebook users:** binding Jupyter to localhost breaks direct LAN access; set up the SSH tunnel, VPN,
  or JupyterHub path first.
- **Monitoring:** Prometheus scrapes of dcgm-exporter break if it is moved to localhost without a local
  collector.
- **Remote-access users:** removing a port forward or tool cuts off someone who uses it.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Unsupported driver branch | Move to a supported production or long-term branch that the GPU and applications support. | Applications pinned to old CUDA may need rebuilding; legacy GPUs may have no supported branch, so isolate or replace. |
| Driver behind a security bulletin | Update to the fixed version in the same branch. | Reboot or module reload; running jobs stop. |
| Container Toolkit / GPU Operator behind a bulletin | Update promptly, especially if untrusted images run. Until then, run only trusted images with GPU access. | Brief container restarts; check CDI spec regeneration. |
| Default runtime is `nvidia` | Remove it as default; request GPUs explicitly per container (`--gpus`, Compose `deploy.resources.reservations.devices`, or CDI). | Containers that silently used GPUs need an explicit request. |
| Unprivileged env-var/volume GPU requests | Keep these toolkit options at the vendor-recommended values for the installed version; prefer CDI. | Some older workflows depend on them; test. |
| Privileged GPU containers | Replace `--privileged` with `--gpus`/CDI and the specific capabilities really needed. | Some tools (MIG management, profiling) need extra capabilities; grant only those. |
| Open Jupyter | Bind to localhost and reach it through SSH port forwarding or a VPN; always require a token or password; disable root; for several users, JupyterHub with real authentication. | Users must change how they connect; saved URLs break. |
| Secrets in notebooks | Move keys to environment or a secret store; clear outputs; rotate any key that was ever in a shared or synced notebook. | Notebook code needs updating; rotation affects other users of the key. |
| ML dashboards and job APIs | Bind to localhost or put behind an authenticating proxy or VPN; never expose a code-running job API. | Remote viewers need the proxy or VPN path. |
| DCGM exposure | Bind `nv-hostengine` to localhost; restrict `dcgm-exporter` to the monitoring host by firewall or bind address. | Monitoring needs reconfiguring. |
| Mixed-trust GPU sharing | Separate GPUs, MIG instances (where supported), VMs with passthrough, or hosts for untrusted workloads. | Fewer workloads per GPU; MIG reduces per-instance capacity. |
| Device-node permissions on multi-user hosts | Restrict `/dev/nvidia*` to a GPU group via NVIDIA's documented module options. | Users and services outside the group lose GPU access. |
| Remote access | One authenticated path (VPN or SSH with keys); remove port forwards and unused remote-support tools; game-streaming UIs not exposed. | Users relying on a removed tool need the new path. |
| Monitoring | Collect GPU utilization and alert on unexpected sustained load. | Needs a metrics stack; tune to avoid noise during real jobs. |

Group the plan into: immediate containment (if any) → urgent security fixes → high-priority hardening →
routine maintenance → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. GPU-host specifics:

- **Driver updates (C2):** confirm the target version supports every GPU and the CUDA versions in use,
  that Secure Boot module signing will work, and that a way back exists (the previous package version, or
  a snapshot of the host or VM). Use the same install method as before; mixing a `.run` install with
  distribution packages breaks both. Plan a reboot. On hypervisors with vGPU, follow NVIDIA's vGPU
  procedure, since host and guest drivers must stay compatible.
- **Container Toolkit and GPU Operator updates (C2):** follow NVIDIA's install guide for the package
  source in use; regenerate CDI specs if CDI is used; restart GPU containers one at a time and check
  `nvidia-smi` inside each.
- **Runtime and toolkit configuration (C2):** capture `daemon.json` and `config.toml` first; change one
  setting; restart the runtime in a window, since it restarts containers; check every container that
  needs a GPU still gets one and others don't.
- **Jupyter and dashboards (C1 or C2):** change bind address and authentication in the config file or
  service unit, not by killing a user's running server mid-job; confirm with the user first.
- **MIG, ECC, persistence, clocks, power limits (C2):** these reset or reconfigure the GPU and stop jobs.
  Change only with fresh approval and only where the finding needs it.
- **Never disable Secure Boot to make a driver load** as part of security work; sign the module instead,
  following the distribution's documented process.

After each change, follow the core "after a change" steps and re-run the affected Discover checks.

### Hard stops (refer to a specialist; never automate)

- Never flash or modify GPU firmware (VBIOS), use unlocked or modified firmware, or bypass vGPU licensing.
- Never overclock, undervolt, change fan curves, or raise power limits as security work.
- Never run a GPU reset or MIG reconfiguration while the user's jobs are running.
- Never run untrusted images or notebooks to "test" a finding.

---

## Respond

On any P0 indicator (unknown processes on the GPU, cryptominer binaries or pool connections, notebooks or
containers nobody created, new SSH keys or remote-access tools, unexplained outbound traffic, or a
notebook found open to the internet with signs of use), switch to Respond immediately. Follow the core
playbook plus the GPU-host-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### GPU-001: Jupyter server open on the LAN without a token, running as root in a GPU container with the host home directory mounted

**Confidence:** Confirmed
**Priority:** P1. Anyone on the LAN can open a terminal in the notebook and act as root inside a
container that has the user's home directory (with SSH keys and model-hub tokens) mounted read-write; a
LAN-reachable unauthenticated remote shell. Raise to P0 if the access logs show unknown clients.
**State:** Open
**Component:** JupyterLab in a CUDA-based container on a Linux GPU workstation; NVIDIA Container
Toolkit installed; `nvidia` set as Docker's default runtime.
**Evidence:** Observed 2026-10-31: `docker inspect` shows the container started with
`--ServerApp.token='' --ip=0.0.0.0 --allow-root`, published on `0.0.0.0:8888`, bind mount of the user's
home directory read-write. `ss -tlnp` shows docker-proxy on `0.0.0.0:8888`. From another LAN host
(`192.0.2.25`, user-approved check), `http://192.0.2.10:8888/lab` loaded the file browser with no login.
`daemon.json` sets `"default-runtime": "nvidia"`; three other containers inherit GPU access from their
base image's `NVIDIA_VISIBLE_DEVICES=all`.
**Expected secure state:** Jupyter bound to localhost or behind authenticated access, token or password
required, not running as root, no broad host mounts (Jupyter Server security documentation); GPUs given
only to containers that request them (NVIDIA Container Toolkit documentation).
**Exposure and prerequisites:** any device on `192.0.2.0/24`. No credentials needed.
**Dependencies / blast radius:** the user opens notebooks from a laptop on the LAN; one model server
container needs the GPU; two of the three inheriting containers don't.
**Recommended remediation:** (1) publish the notebook port on `127.0.0.1` only, re-enable token
authentication, drop `--allow-root`, and mount only the project directory; reach it with
`ssh -L 8888:127.0.0.1:8888 <user>@<gpu-host>`; (2) rotate the model-hub token and review SSH keys in the
mounted home directory; (3) remove `nvidia` as the default runtime and add an explicit GPU request to the
model server container only.
**Operation class:** C2 (container recreation; Docker restart for the runtime change).
**Approval required:** Yes. Changes how the user connects and restarts containers.
**Verification:** port 8888 no longer answers from `192.0.2.25`; the notebook asks for a token through
the SSH tunnel; `nvidia-smi` works in the model server container and fails in the other two.
**Rollback:** restore the captured Compose file and `daemon.json`, then recreate the containers.

---

## Version history

- **1.0** (2026-10-31): Initial version.
