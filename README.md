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

## Quick start: assess everything

1. Optional: start the [live dashboard](tools/dashboard/README.md) to watch progress.
2. Give your AI assistant this collection (clone the repo, or install `dist/full-assessment/` plus the
   product skills you need) and paste:

```text
Use the full-assessment skill from ai-security-skills to run a complete security assessment of my
network. Start with the kick-off questions. Discovery level 0 until I approve more. Don't change
anything without my approval. Report live events to ~/.ai-security-dashboard/events/.
```

The agent asks a few scoping questions, inventories your network, matches each device to a skill, runs
each skill's checks, and gives you one prioritized plan. Devices without a dedicated skill still get
baseline checks and show up as gaps on the dashboard.

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
tools/dashboard/          Local live dashboard that agents report progress to
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
| network | [`opnsense`](skills/network/opnsense/SKILL.md) | OPNsense firewall |
| network | [`pfsense`](skills/network/pfsense/SKILL.md) | pfSense firewall (CE and Plus) |
| network | [`vpn-servers`](skills/network/vpn-servers/SKILL.md) | WireGuard and OpenVPN servers (including wg-easy, PiVPN, Access Server) |
| network | [`dns-filtering`](skills/network/dns-filtering/SKILL.md) | DNS filtering (AdGuard Home, Pi-hole) |
| network | [`wifi-and-switches`](skills/network/wifi-and-switches/SKILL.md) | Consumer Wi-Fi mesh systems and managed switches |
| network | [`home-routers`](skills/network/home-routers/SKILL.md) | Home routers, ISP gateways, modems, and bridge/passthrough mode |
| edge | [`cloudflare`](skills/edge/cloudflare/SKILL.md) | Cloudflare (Tunnels, DNS, Zero Trust Access, proxied sites) |
| storage | [`synology-dsm`](skills/storage/synology-dsm/SKILL.md) | Synology DSM (including DSM on non-Synology hardware) |
| virtualization | [`proxmox-ve`](skills/virtualization/proxmox-ve/SKILL.md) | Proxmox VE (including server BMCs) |
| operating-systems | [`macos`](skills/operating-systems/macos/SKILL.md) | macOS (including Macs used as home servers) |
| operating-systems | [`linux`](skills/operating-systems/linux/SKILL.md) | Linux (servers, VMs, LXC, Raspberry Pi) |
| operating-systems | [`windows`](skills/operating-systems/windows/SKILL.md) | Windows 10/11 and small Windows Server installs |
| containers | [`docker`](skills/containers/docker/SKILL.md) | Docker, Docker Desktop, Podman, NAS container managers |
| home-automation | [`home-assistant`](skills/home-automation/home-assistant/SKILL.md) | Home Assistant |
| home-automation | [`mqtt`](skills/home-automation/mqtt/SKILL.md) | MQTT brokers (Mosquitto) |
| home-automation | [`smart-home-devices`](skills/home-automation/smart-home-devices/SKILL.md) | Smart home devices: plugs, bulbs, light switches, locks, thermostats, hubs and bridges, ESPHome/Tasmota |
| surveillance | [`frigate-nvr`](skills/surveillance/frigate-nvr/SKILL.md) | NVR software (Frigate) |
| surveillance | [`ip-cameras`](skills/surveillance/ip-cameras/SKILL.md) | IP cameras (with vendor-family notes) |
| surveillance | [`video-doorbells`](skills/surveillance/video-doorbells/SKILL.md) | Video doorbells and cloud camera systems |
| consumer-devices | [`smart-tvs`](skills/consumer-devices/smart-tvs/SKILL.md) | Smart TVs and streaming devices |
| peripherals | [`printers`](skills/peripherals/printers/SKILL.md) | Network printers and multifunction printers |
| maker-devices | [`3d-printers`](skills/maker-devices/3d-printers/SKILL.md) | 3D printers (Bambu Lab, Prusa, OctoPrint, Klipper/Moonraker) |
| maker-devices | [`craft-cutters`](skills/maker-devices/craft-cutters/SKILL.md) | Craft cutting machines (Cricut, Silhouette, Brother ScanNCut) |
| media | [`media-automation`](skills/media/media-automation/SKILL.md) | Media automation (*arr apps, downloaders) |
| media | [`media-servers`](skills/media/media-servers/SKILL.md) | Media servers (Plex, Jellyfin, Emby) and Tdarr |
| ai | [`local-llm`](skills/ai/local-llm/SKILL.md) | Local LLM and generative-AI servers |
| ai | [`mcp-servers`](skills/ai/mcp-servers/SKILL.md) | MCP and RAG servers, vector databases |
| web-apps | [`self-hosted-web-apps`](skills/web-apps/self-hosted-web-apps/SKILL.md) | Small self-hosted web apps and dashboards |
| web | [`web-servers`](skills/web/web-servers/SKILL.md) | Web servers and reverse proxies (Apache, nginx, Caddy, Traefik, HAProxy, NPM) |

Suggestions for new skills are welcome; start from `templates/skill-template/`.

## Live dashboard

Run `python3 tools/dashboard/dashboard.py serve` to get a private local web page showing what your agents
have found as they work: mode, domain status, findings, changes, and incidents. See
[tools/dashboard/README.md](tools/dashboard/README.md).

## Contributing

Read [CONTENT_RULES.md](CONTENT_RULES.md) first: skills must be fully generic, with no names, addresses,
credentials, or other details from any real environment. Run `scripts/check-content.sh` before every commit.

## License

[CC BY 4.0](LICENSE). Use, adapt, and share these skills, including commercially, with attribution.
