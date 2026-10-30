# OPNsense: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only OPNsense-specific steps.

A compromised firewall is a compromised network: it sees and can alter all traffic, DNS, and DHCP, and it
holds VPN keys and credentials for other systems. If the firewall itself may be compromised, **don't rely
on it to contain the incident**.

## Triage and containment

- **Indicators that point at the firewall itself:** unknown admin users or API keys, configuration
  history entries nobody made, new port forwards or WAN rules, new VPN peers or certificates, changed DNS
  host overrides or DHCP options, unknown plugins or package repositories, unexpected cron jobs, unusual
  outbound connections from the firewall, or logins from unknown addresses.
- **If the firewall may be compromised:** contain *upstream* of it. Disconnect the WAN at the modem or
  upstream router, or (virtualized) disconnect the WAN virtual NIC at the hypervisor. Keep console access
  to the firewall. Don't power it off unless destruction is ongoing.
- **If the firewall is trusted and is being used to contain another device:** prefer narrow, reversible
  rules (block one host or one segment) over broad changes, with approval. Record every rule you add.
- **Stop trusting what the firewall serves:** if DNS or DHCP settings may have been altered, clients may be
  sent to attacker-controlled DNS. Note this for scoping.

## Evidence to preserve (OPNsense-specific)

Collect from the console or a clean admin workstation, before changing anything:

- Configuration history: the list of entries (time, user, description) and copies of the current
  configuration and the last entries before the suspected compromise. Treat these as secret material.
- Users, groups, privileges, API keys (metadata only), and SSH authorized keys.
- Loaded rules and NAT: `pfctl -s rules`, `pfctl -s nat`, plus the GUI rules and port forwards.
- Listening services and processes: `sockstat -4 -6 -l`, `ps auxww`.
- WireGuard peers (`wg show`; never `wg showconf`), OpenVPN users and certificates, IPsec tunnels.
- Unbound host overrides and forwarding settings; DHCP options and static mappings.
- Installed plugins (`pkg info -x '^os-'`), configured package repositories, and cron jobs (GUI cron and
  system crontabs).
- Logs: system, audit/backend, web GUI access, firewall, VPN, and DNS logs. Export them off the firewall;
  if `/var` is a RAM disk, logs are lost on reboot, so export before any restart.
- For virtualized firewalls: a VM snapshot (including memory if the hypervisor supports it) before
  changes.

## Scope checks specific to a firewall

- Every device behind it: traffic may have been intercepted or redirected (DNS overrides, rogue DHCP
  options, malicious NAT). Check for credential theft on services that traffic passed through.
- Every VPN peer and remote site: their keys were on the firewall.
- Every system whose credentials are stored in the configuration: dynamic DNS accounts, remote syslog,
  LDAP/RADIUS bind accounts, backup destinations, SMTP accounts, HA peers.
- The admin workstations used to manage the firewall.
- For virtualized firewalls: the hypervisor and its other guests.

## Eradication and recovery

- If firewall integrity is in doubt, **reinstall from a verified image** (check the checksum and signature
  published with the release) rather than cleaning the running system.
- Restore configuration only from a backup taken **before** the earliest plausible compromise, and diff it
  against the compromised configuration to understand what the attacker changed. Don't restore attacker
  changes.
- **Rotate every secret that was in the configuration**, because the attacker could read it: admin and
  user passwords, API keys, WireGuard keys (new keys for the server and every peer), OpenVPN CA and
  certificates (reissue, and revoke the old ones), IPsec keys, certificate private keys, dynamic DNS,
  syslog, LDAP/RADIUS, SMTP, backup-destination, and HA sync credentials.
- Before reconnecting the WAN: 2FA on all admin accounts, management not reachable from WAN, only expected
  port forwards, VPN peers re-issued, plugins and repositories reviewed, and remote logging working.

## Quick checklist tailored for a firewall

Start with the core quick checklist, plus:

- [ ] If the firewall itself may be compromised, disconnect the WAN upstream (modem or hypervisor), not at
      the firewall, and keep console access.
- [ ] Export configuration history and logs before rebooting (logs may live in RAM).
- [ ] List admin users, API keys, port forwards, VPN peers, and DNS overrides; screenshot anything
      unexpected.
- [ ] Plan to reinstall from a verified image and to rotate every secret in the configuration.
