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

## Layout

```
core/                     Shared rules every skill builds on (modes, authorization, evidence, triage, IR)
templates/skill-template/ Starting point for new skills
skills/<domain>/<product>/
  SKILL.md                Product-specific Discover / Recommend / Remediate guidance
  incident-response.md    Product-specific incident-response steps
  references.md           Vendor documentation and advisories, with last-verified dates
dist/                     Generated standalone single-file bundles (core + skill)
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

Status: ✅ available · ⏳ planned

| Domain | Skill | Status |
|---|---|---|
| storage | Synology DSM (including DSM on non-Synology hardware) | ✅ |
| network | OPNsense / pfSense firewall | ⏳ |
| network | WireGuard / OpenVPN | ⏳ |
| network | DNS filtering (AdGuard Home, Pi-hole) | ⏳ |
| network | Consumer Wi-Fi mesh and managed switches | ⏳ |
| edge | Cloudflare (tunnels, DNS, Zero Trust) | ⏳ |
| virtualization | Proxmox VE | ⏳ |
| operating-systems | macOS | ⏳ |
| operating-systems | Linux (servers, VMs, LXC) | ⏳ |
| operating-systems | Windows | ⏳ |
| containers | Docker / Docker Desktop / NAS container managers | ⏳ |
| home-automation | Home Assistant | ⏳ |
| home-automation | MQTT brokers (Mosquitto) | ⏳ |
| surveillance | NVR software (Frigate) | ⏳ |
| surveillance | IP cameras (per-vendor appendices) | ⏳ |
| surveillance | Video doorbells and cloud camera systems | ⏳ |
| consumer-devices | Smart TVs and streaming devices | ⏳ |
| media | Media automation (*arr stack, downloaders) | ⏳ |
| media | Media servers (Plex, Jellyfin) and transcoding (Tdarr) | ⏳ |
| ai | Local LLM and generative-AI servers | ⏳ |
| ai | MCP / RAG servers | ⏳ |
| web-apps | Small self-hosted web apps and dashboards | ⏳ |
| web | Web servers (Apache, nginx) and reverse proxies | ⏳ |

## Live dashboard

Run `python3 tools/dashboard/dashboard.py serve` to get a private local web page showing what your agents
have found as they work: mode, domain status, findings, changes, and incidents. See
[tools/dashboard/README.md](tools/dashboard/README.md).

## Contributing

Read [CONTENT_RULES.md](CONTENT_RULES.md) first: skills must be fully generic, with no names, addresses,
credentials, or other details from any real environment. Run `scripts/check-content.sh` before every commit.

## License

[CC BY 4.0](LICENSE). Use, adapt, and share these skills, including commercially, with attribution.
