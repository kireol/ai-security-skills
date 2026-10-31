# AI Security Skills

A collection of AI security skills designed to help secure your home network, office infrastructure, and internet-facing servers.

These skills enable your AI assistant to **Discover** security weaknesses and potential threats, **Recommend** practical improvements, **Remediate** vulnerabilities with appropriate authorization, and **Respond** to suspected security incidents, malware, and active compromises.

Built to help your AI act as a security partner—not just identify problems, but help you understand, prioritize, and address them.

The skills are portable, model- and tool-agnostic Markdown instruction sets that work with Claude Code, Codex, local LLMs, MCP clients, or a human following along.

Every skill covers four modes:

| Mode | What the AI does | Authorization |
|---|---|---|
| **Discover** | Inspects the system and reports weaknesses with evidence. | Read-only access within the agreed scope. |
| **Recommend** | Proposes specific fixes and explains their consequences, dependencies, and rollback. | None beyond Discover; nothing is changed. |
| **Remediate** | Makes changes. | Explicit approval for each change, or a bounded standing authorization. |
| **Respond** (incident response) | Walks the user through containment, evidence preservation, and recovery after a suspected compromise. | Urgent manual steps are advised immediately; disruptive actions still need approval. |

## Live dashboard

Run `python3 tools/dashboard/dashboard.py serve` (or answer yes to the launcher's dashboard question) to
get a private local web page showing what your agents have found as they work: the inventory, mode,
domain status, findings, changes, and incidents. See [tools/dashboard/README.md](tools/dashboard/README.md).

![The dashboard during an example run: a list of assessments with open findings by priority, and the
run's inventory, network-wide domains, and findings](docs/images/dashboard.png)

## Quick start

Get the collection and run the launcher. It asks which AI assistant to use (Claude Code, Codex, or
Gemini CLI, or it prints the prompt for any other) and whether to start a [live dashboard](#live-dashboard)
you can watch in a browser, then starts the assessment. Pick your system:

<details>
<summary><b>macOS</b></summary>

```sh
git clone https://github.com/kireol/ai-security-skills.git
cd ai-security-skills
scripts/assess.sh
```

Needs Git and Python 3.9 or later; both come with the Xcode Command Line Tools
(`xcode-select --install`). Stop the dashboard when you're done with `scripts/assess.sh --stop`.

</details>

<details>
<summary><b>Linux</b></summary>

```sh
git clone https://github.com/kireol/ai-security-skills.git
cd ai-security-skills
scripts/assess.sh
```

Needs Git and Python 3.9 or later, for example `sudo apt install git python3` (Debian, Ubuntu),
`sudo dnf install git python3` (Fedora), or `sudo pacman -S git python` (Arch). On a computer without a
screen, choose the dashboard option for **any device on my local network** and open the link it prints
from another device. Stop the dashboard when you're done with `scripts/assess.sh --stop`.

</details>

<details>
<summary><b>Windows</b></summary>

In PowerShell:

```powershell
git clone https://github.com/kireol/ai-security-skills.git
cd ai-security-skills
powershell -ExecutionPolicy Bypass -File scripts\assess.ps1
```

Needs [Git](https://git-scm.com/download/win) and Python 3.9 or later from
[python.org](https://www.python.org/downloads/) (tick "Add python.exe to PATH") or the Microsoft Store.
Stop the dashboard when you're done with
`powershell -ExecutionPolicy Bypass -File scripts\assess.ps1 -Stop`.

</details>

Your reports are saved in `~/ai-security-reports/`. To check a single device instead of the whole
network, see [Check just one device](#check-just-one-device).

<details>
<summary><b>More:</b> options, suggested answers, the dashboard port, and running without the script</summary>

**Options.** Each one skips a question or changes a default. PowerShell uses the same names in its own
style (`-Agent`, `-Local`, `-Lan`, `-NoDashboard`, `-Port`, `-NoLookup`, `-Stop`).

| Option | What it does |
|---|---|
| `--agent claude\|codex\|gemini\|print` | Use this assistant, or print the prompt to paste into another one. |
| `--local`, `--lan`, `--no-dashboard` | Start the dashboard viewable from this computer only, or from your local network, or don't start one. |
| `--port N` | Dashboard port (default 8770). |
| `--no-lookup` | Don't ask an outside service for your public address. |
| `--stop` | Stop the dashboard, however it was started. |

**The dashboard.** You can answer the kick-off questions in the chat or in the dashboard's **Kick-off
settings** tab, which also shows every answer however it was given. As the agent works, the dashboard
fills in with the inventory, each system's checks, findings, and changes. Already in an AI session? Ask
it to "start the dashboard" during the kick-off. See the [dashboard README](tools/dashboard/README.md).

**Suggested answers.** The launcher suggests three kick-off answers, which you confirm or change:
**In-scope networks** (the /24 network around this computer's address), **Internet edge** (your
network's public address, looked up with an outside service; `--no-lookup` skips it), and **Agents** (1).
It passes them to the assistant and fills them into the dashboard's Kick-off settings form.

**If the dashboard port is in use,** the launcher reuses the dashboard only if it's this copy's, up to
date, and using the same data folder. Otherwise it tells you what's there (an older dashboard, one from
another copy, or another program) and stops without starting anything; stop the old dashboard or pick
another port with `--port N`.

**Without the script,** paste this into your AI assistant from inside the collection's folder:

```text
Use the full-assessment skill (skills/orchestration/full-assessment/SKILL.md) to run a complete security
assessment of my network. Follow its "Before anything else" rules: set up the run folder first, then ask
me the kick-off questions, and don't scan or probe my network until I've answered them. Don't change
anything without my approval.
```

</details>

### Check just one device

No kick-off, no inventory: point your AI assistant at one system and the skill for it (see the
[catalog](#catalog) below). From inside the collection's folder, ask for example:

```text
Use the synology-dsm skill (dist/synology-dsm.md) to run a Discover assessment of my Synology NAS at
<nas address>. I'll run any commands you need and paste the output. Don't change anything, and finish
with the report and totals.
```

Other examples: "Use the opnsense skill to check my firewall", "Use the phones skill to walk me through
securing my iPhone", or "Use the ip-cameras skill to check the camera at <camera address>". The agent
follows the same rules as a full run: read-only first, nothing changed without your approval, and a
report at the end.

### What happens in a full assessment

1. **Kick-off.** The agent asks what's in scope, how far it may probe your network, whether you want to
   give it **its own access** (read-only SSH, API keys, or accounts) for a deeper look or run commands
   yourself, whether to use **one agent or several** (several is faster but uses tokens faster), and whether to work
   **in phases** so you can stop and resume later without spending all your tokens at once.
2. **Inventory and plan.** It finds your systems, matches each one to a skill, and shows you the plan.
3. **Checks.** It runs each skill's read-only checks, most exposed systems first. Nothing is changed
   without your approval.
4. **Report.** At the end it writes a full report as **HTML and Markdown** and tells you the totals and
   where the files are:

   ```
   Systems found:     12
   Serious problems:  3   (open P0–P2)
   Warnings:          7   (open P3)
   Informational:     4   (open P4)
   Full report (HTML):     ~/ai-security-reports/<run-id>/report.html
   Full report (Markdown): ~/ai-security-reports/<run-id>/report.md
   ```

5. **Help the project.** If it found devices no skill covers yet, it offers to draft a public GitHub issue
   requesting one. It shows you the exact text first, describes only the product (never your network), and
   only goes ahead with your approval.

Everything about your systems stays on your machine in `~/ai-security-reports/`, readable only by you.

## Layout

```
core/                     Shared rules every skill builds on (modes, authorization, evidence, triage, IR)
templates/skill-template/ Starting point for new skills
skills/<domain>/<product>/
  SKILL.md                Product-specific Discover / Recommend / Remediate guidance
  incident-response.md    Product-specific incident-response steps
  references.md           Vendor documentation and advisories, with last-verified dates
dist/                     Generated bundles: one folder and one single file per skill, plus catalog.md
scripts/                  Tooling, including the content check
tools/dashboard/          Local live dashboard and the report generator (report.md / report.html)
```

## Using a skill

- **Claude Code (or any loader that understands `SKILL.md`):** copy `dist/<skill>/` into your skills
  directory (for Claude Code, `~/.claude/skills/<skill>/` or `.claude/skills/<skill>/` in a project). The
  folder includes its own copy of `core/`.
- **Any other AI assistant:** paste or attach the single file `dist/<skill>.md`. It contains the skill and
  all of `core/`.
- Then ask, for example: "Use the Synology DSM security skill to run a Discover assessment of my NAS."

## Catalog

| Domain | Skill | Covers |
|---|---|---|
| orchestration | [`full-assessment`](skills/orchestration/full-assessment/SKILL.md) | Full assessment: kick-off that inventories the network and runs every matching skill |
| orchestration | [`skill-request`](skills/orchestration/skill-request/SKILL.md) | Offers to open a GitHub issue requesting a skill for devices no skill covers (only with your approval) |
| network | [`opnsense`](skills/network/opnsense/SKILL.md) | OPNsense firewall |
| network | [`pfsense`](skills/network/pfsense/SKILL.md) | pfSense firewall (CE and Plus) |
| network | [`vpn-servers`](skills/network/vpn-servers/SKILL.md) | WireGuard and OpenVPN servers (including wg-easy, PiVPN, Access Server) |
| network | [`dns-filtering`](skills/network/dns-filtering/SKILL.md) | DNS filtering and DNS servers (AdGuard Home, Pi-hole, Technitium DNS) |
| network | [`wifi-and-switches`](skills/network/wifi-and-switches/SKILL.md) | Consumer Wi-Fi mesh systems and managed switches |
| network | [`home-routers`](skills/network/home-routers/SKILL.md) | Home routers, ISP gateways, modems, and bridge/passthrough mode |
| network | [`mikrotik-routeros`](skills/network/mikrotik-routeros/SKILL.md) | MikroTik RouterOS (Winbox, WebFig, API, RoMON, CHR) |
| edge | [`cloudflare`](skills/edge/cloudflare/SKILL.md) | Cloudflare (Tunnels, DNS, Zero Trust Access, proxied sites) |
| edge | [`tunnels`](skills/edge/tunnels/SKILL.md) | Other tunnels and publishing services (ngrok, Tailscale Funnel/Serve, frp, Pangolin, zrok, Dev Tunnels, SSH reverse tunnels) |
| storage | [`synology-dsm`](skills/storage/synology-dsm/SKILL.md) | Synology DSM (including DSM on non-Synology hardware) |
| storage | [`qnap-qts`](skills/storage/qnap-qts/SKILL.md) | QNAP NAS (QTS, QuTS hero, myQNAPcloud) |
| storage | [`truenas`](skills/storage/truenas/SKILL.md) | TrueNAS (Community Edition/SCALE, Enterprise, legacy CORE) |
| storage | [`unraid`](skills/storage/unraid/SKILL.md) | Unraid (array, shares, Connect, Community Applications) |
| storage | [`openmediavault`](skills/storage/openmediavault/SKILL.md) | openmediavault and omv-extras |
| storage | [`object-storage`](skills/storage/object-storage/SKILL.md) | Self-hosted S3-compatible object storage (MinIO, Garage, SeaweedFS) |
| storage | [`zfs-and-ceph`](skills/storage/zfs-and-ceph/SKILL.md) | ZFS and Ceph security: encryption, snapshots, delegation, cephx (no repair procedures) |
| storage | [`backup-tools`](skills/storage/backup-tools/SKILL.md) | Backup tools and offsite targets (Restic, Borg, Veeam, Duplicati, Backblaze B2, Wasabi) |
| virtualization | [`proxmox-ve`](skills/virtualization/proxmox-ve/SKILL.md) | Proxmox VE (including server BMCs) |
| virtualization | [`vmware-esxi`](skills/virtualization/vmware-esxi/SKILL.md) | VMware ESXi (standalone hosts and small vCenter setups) |
| virtualization | [`xcp-ng`](skills/virtualization/xcp-ng/SKILL.md) | XCP-ng and Xen Orchestra |
| operating-systems | [`macos`](skills/operating-systems/macos/SKILL.md) | macOS (including Macs used as home servers) |
| operating-systems | [`linux`](skills/operating-systems/linux/SKILL.md) | Linux (servers, desktops and laptops, VMs, LXC, Raspberry Pi) |
| operating-systems | [`windows`](skills/operating-systems/windows/SKILL.md) | Windows 10/11 and small Windows Server installs, including domain controllers |
| operating-systems | [`chromeos`](skills/operating-systems/chromeos/SKILL.md) | ChromeOS and ChromeOS Flex |
| mobile | [`phones`](skills/mobile/phones/SKILL.md) | Phones and tablets (iPhone, iPad, Android), including SIM-swap and stalkerware protection |
| containers | [`docker`](skills/containers/docker/SKILL.md) | Docker, Docker Desktop, Podman, NAS container managers |
| home-automation | [`home-assistant`](skills/home-automation/home-assistant/SKILL.md) | Home Assistant |
| home-automation | [`mqtt`](skills/home-automation/mqtt/SKILL.md) | MQTT brokers (Mosquitto) |
| home-automation | [`smart-home-devices`](skills/home-automation/smart-home-devices/SKILL.md) | Smart home devices: plugs, bulbs, light switches, locks, thermostats, hubs and bridges, ESPHome/Tasmota |
| home-automation | [`homebridge`](skills/home-automation/homebridge/SKILL.md) | Homebridge and its plugins |
| surveillance | [`frigate-nvr`](skills/surveillance/frigate-nvr/SKILL.md) | NVR software (Frigate) |
| surveillance | [`ip-cameras`](skills/surveillance/ip-cameras/SKILL.md) | IP cameras (with vendor-family notes) |
| surveillance | [`video-doorbells`](skills/surveillance/video-doorbells/SKILL.md) | Video doorbells and cloud camera systems |
| surveillance | [`nvr-software`](skills/surveillance/nvr-software/SKILL.md) | NVR software other than Frigate (Blue Iris, Synology Surveillance Station, other VMS) |
| consumer-devices | [`smart-tvs`](skills/consumer-devices/smart-tvs/SKILL.md) | Smart TVs and streaming devices |
| consumer-devices | [`game-consoles`](skills/consumer-devices/game-consoles/SKILL.md) | Game consoles and handhelds (PlayStation, Xbox, Nintendo Switch, Steam Deck/SteamOS) |
| peripherals | [`printers`](skills/peripherals/printers/SKILL.md) | Network printers, multifunction printers, and network scanners |
| maker-devices | [`3d-printers`](skills/maker-devices/3d-printers/SKILL.md) | 3D printers (Bambu Lab, Prusa, OctoPrint, Klipper/Moonraker) |
| maker-devices | [`craft-cutters`](skills/maker-devices/craft-cutters/SKILL.md) | Craft cutting machines (Cricut, Silhouette, Brother ScanNCut) |
| media | [`media-automation`](skills/media/media-automation/SKILL.md) | Media automation (*arr apps, downloaders) |
| media | [`media-servers`](skills/media/media-servers/SKILL.md) | Media servers (Plex, Jellyfin, Emby) and Tdarr |
| ai | [`local-llm`](skills/ai/local-llm/SKILL.md) | Local LLM and generative-AI servers (including LocalAI and the LiteLLM gateway) |
| ai | [`mcp-servers`](skills/ai/mcp-servers/SKILL.md) | MCP and RAG servers, vector databases |
| ai | [`gpu-hosts`](skills/ai/gpu-hosts/SKILL.md) | GPU hosts (NVIDIA drivers, Container Toolkit, DCGM, notebooks) |
| ai | [`ai-coding-agents`](skills/ai/ai-coding-agents/SKILL.md) | AI coding agents (Claude Code, OpenCode, Continue, and similar) |
| ai | [`ai-app-builders`](skills/ai/ai-app-builders/SKILL.md) | Low-code LLM app builders (Flowise, Dify, Langflow) |
| web-apps | [`self-hosted-web-apps`](skills/web-apps/self-hosted-web-apps/SKILL.md) | Small self-hosted web apps and dashboards (including ntfy, Gotify, CasaOS) |
| web-apps | [`nextcloud`](skills/web-apps/nextcloud/SKILL.md) | Nextcloud Server and Nextcloud AIO |
| web-apps | [`photo-and-document-apps`](skills/web-apps/photo-and-document-apps/SKILL.md) | Photo and document apps (Immich, Paperless-ngx) |
| web-apps | [`automation-platforms`](skills/web-apps/automation-platforms/SKILL.md) | Workflow automation (n8n, Node-RED) |
| web | [`web-servers`](skills/web/web-servers/SKILL.md) | Web servers and reverse proxies (Apache, nginx, Caddy, Traefik, HAProxy, NPM) |
| identity | [`password-managers`](skills/identity/password-managers/SKILL.md) | Password managers (Bitwarden, Vaultwarden, 1Password, KeePass/KeePassXC) |
| identity | [`mfa`](skills/identity/mfa/SKILL.md) | Multi-factor authentication (security keys, passkeys, authenticator apps, Duo) |
| identity | [`identity-providers`](skills/identity/identity-providers/SKILL.md) | Self-hosted SSO and identity providers (Authentik, Authelia, Keycloak) |
| monitoring | [`monitoring`](skills/monitoring/monitoring/SKILL.md) | Infrastructure monitoring (Prometheus, Netdata, Zabbix, Checkmk) |
| monitoring | [`logging-and-siem`](skills/monitoring/logging-and-siem/SKILL.md) | Logging and SIEM (Wazuh, Graylog, ELK, OpenSearch, CrowdSec, Fail2ban) |
| remote-access | [`remote-desktop-and-rmm`](skills/remote-access/remote-desktop-and-rmm/SKILL.md) | Remote desktop and RMM (Guacamole, RustDesk, MeshCentral, Tactical RMM) |
| hardware | [`out-of-band-management`](skills/hardware/out-of-band-management/SKILL.md) | Out-of-band management (iDRAC, iLO, Supermicro IPMI, Redfish, Intel AMT) |
| hardware | [`ups`](skills/hardware/ups/SKILL.md) | Network UPS devices and shutdown software (APC, CyberPower, Eaton, NUT) |
| cloud | [`productivity-suites`](skills/cloud/productivity-suites/SKILL.md) | Microsoft 365 and Google Workspace |
| cloud | [`cloud-storage`](skills/cloud/cloud-storage/SKILL.md) | Cloud storage and sync (Dropbox, OneDrive, Google Drive, iCloud) |
| cloud | [`cloud-providers`](skills/cloud/cloud-providers/SKILL.md) | Cloud provider accounts (AWS, Azure, Google Cloud, DigitalOcean, Linode/Akamai) |
| cloud | [`domain-registrars`](skills/cloud/domain-registrars/SKILL.md) | Domain registrars (Namecheap, GoDaddy, and others) |
| dev | [`code-hosting-and-ci`](skills/dev/code-hosting-and-ci/SKILL.md) | Code hosting and CI/CD (GitHub, GitLab, Gitea, Forgejo, Actions, Jenkins) |
| dev | [`infrastructure-as-code`](skills/dev/infrastructure-as-code/SKILL.md) | Infrastructure as code (Ansible, Terraform/OpenTofu) |

Suggestions for new skills are welcome; start from `templates/skill-template/`.

## Contributing

Read [CONTENT_RULES.md](CONTENT_RULES.md) first: skills must be fully generic, with no names, addresses,
credentials, or other details from any real environment. Run `scripts/check-content.sh` before every commit.

## License

[CC BY 4.0](LICENSE). Use, adapt, and share these skills, including commercially, with attribution.
