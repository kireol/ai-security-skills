# Content Rules

Every document in this repository is published for anyone to use. Skills are written by looking at real
deployments, but **nothing from any real deployment may appear in them**. These rules apply to every file:
skills, core documents, templates, examples, scripts, commit messages, and pull requests.

## Never include

- **Names:** people, households, sites, organizations, hostnames, device names, Wi-Fi SSIDs, domain names,
  share/volume names, VM/container names, service account names, or usernames from a real environment.
- **Network identifiers:** IP addresses (including private ranges), subnets, MAC addresses, ports *as
  configured in a specific environment*, VLAN IDs, DHCP reservations, WireGuard/VPN keys or peer lists.
- **Secrets:** passwords, password hashes, API keys, tokens, private keys, certificates, recovery codes,
  tunnel tokens, connection strings, or anything that looks like one, even if it is fake or expired.
- **Hardware/asset identifiers:** serial numbers, service tags, IMEIs, license keys, account IDs.
- **Environment specifics:** real file paths that reveal a user or layout (e.g. `/Users/<name>/…`,
  `/volume1/<share>`), schedules, camera locations, room names, inventories, or findings from a real audit.
- **References to private sources:** internal knowledge bases, runbooks, tickets, or chat logs.

## How to write instead

- Describe the **class** of thing: "the NAS's NFS export", "a camera on the IoT VLAN", "a reverse-proxied
  admin UI".
- Product **default** ports and paths are fine when they are vendor-documented (e.g. a product's default
  web UI port), because they describe the product, not a deployment.
- Use reserved documentation values when an example needs concrete values:
  - IPv4: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737)
  - IPv6: `2001:db8::/32` (RFC 3849)
  - Domains: `example.com`, `example.net`, `example.org`, `*.example` (RFC 2606)
  - MAC: `00:00:5e:00:53:xx` (RFC 7042)
  - Placeholders: `<nas-host>`, `<admin-user>`, `<share-name>`, `<api-token>`
- Worked examples must be invented and visibly generic ("Example finding NAS-001: NFS export writable by the
  whole LAN"), never a lightly edited copy of a real finding.
- A real deployment may inspire *which* checks to add (e.g. "this setup had no hypervisor backups, so the
  skill should check for that"). Write the check generically; do not describe the deployment.

## Enforcement

- Run `scripts/check-content.sh` before committing. It flags private/non-documentation IP addresses, MAC
  addresses, email addresses, key/token patterns, and any term listed in your local `.private-denylist`.
- `.private-denylist` is git-ignored. Put your own names, hostnames, domains, and other identifiers in it
  (one per line, case-insensitive) so the check catches them. Never commit it. See
  `.private-denylist.example`.
- A hit is not automatically a violation (for example, a vendor-documented default), but every hit must be
  reviewed and either removed or justified.
