# AI Security Skills

Portable, model- and tool-agnostic instruction sets ("skills") that let an AI assistant audit, harden, and
help recover the systems people run at home, at work, in a homelab, and on the web.

Every skill covers four modes:

| Mode | What the AI does | Authorization |
|---|---|---|
| **Discover** | Inspects the system and reports weaknesses with evidence. | Read-only access within the agreed scope. |
| **Recommend** | Proposes specific fixes and explains their consequences, dependencies, and rollback. | None beyond Discover; nothing is changed. |
| **Remediate** | Makes changes. | Explicit approval for each change, or a bounded standing authorization. |
| **Incident response** | Walks the user through containment, evidence preservation, and recovery after a suspected compromise. | Urgent manual steps are advised immediately; disruptive actions still need approval. |

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
```

`core/`, `templates/`, and `dist/` are being built out; until then, the Synology skill is self-contained.

## Catalog

Status: ✅ available · 🛠 needs restructuring to the template · ⏳ planned

| Domain | Skill | Status |
|---|---|---|
| storage | Synology DSM (including DSM on non-Synology hardware) | 🛠 |
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

## Contributing

Read [CONTENT_RULES.md](CONTENT_RULES.md) first: skills must be fully generic, with no names, addresses,
credentials, or other details from any real environment. Run `scripts/check-content.sh` before every commit.

## License

[CC BY 4.0](LICENSE). Use, adapt, and share these skills, including commercially, with attribution.
