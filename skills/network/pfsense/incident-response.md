# pfSense: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only pfSense-specific steps.

A compromised firewall is a compromised network: it sees and can alter all traffic, DNS, and DHCP, and it
holds VPN keys and credentials for other systems. If the firewall itself may be compromised, **don't rely
on it to contain the incident**.

## Triage and containment

- **Indicators that point at the firewall itself:** unknown users or group privilege changes, Config
  History entries nobody made, new port forwards, WAN rules, or floating rules, new VPN peers or
  certificates, changed DNS host or domain overrides or DHCP options, unknown packages or package
  repositories, new Shellcmd, Cron, Filer, or System Patches entries, unexpected UPnP mappings, unusual
  outbound connections from the firewall, logins from unknown addresses, or an AutoConfigBackup device key
  or encryption password that changed without explanation.
- **If the firewall may be compromised:** contain *upstream* of it. Disconnect the WAN at the modem or
  upstream router, or (virtualized) disconnect the WAN virtual NIC at the hypervisor. Keep console access
  to the firewall. Don't power it off unless destruction is ongoing.
- **If the firewall is trusted and is being used to contain another device:** prefer narrow, reversible
  rules (block one host or one segment) over broad changes, with approval. Record every rule you add.
- **HA pairs and Nexus:** a compromise of one node can replicate through XMLRPC sync, and a compromised
  Nexus controller can change every registered instance. With approval, pause sync or disconnect the
  controller, and assess every node.
- **Stop trusting what the firewall serves:** if DNS, DHCP, or pfBlockerNG settings may have been
  altered, clients may be sent to attacker-controlled DNS. Note this for scoping.

## Evidence to preserve (pfSense-specific)

Collect from the console or a clean admin workstation, before changing anything:

- Config History: the list of entries (time, user, page or description) and copies of the current
  configuration and the last entries before the suspected compromise. On disk these are under
  `/cf/conf/backup/`. Treat them as secret material and copy them off the firewall.
- Users, groups, privileges, authentication servers, and SSH authorized keys from the User Manager.
- Loaded rules and NAT: `pfctl -sr`, `pfctl -sn`, `pfSsh.php playback pfanchordrill`, plus the GUI
  rules, floating rules, port forwards, and UPnP mappings (Status → UPnP IGD & PCP).
- Listening services and processes: `sockstat -4 -6 -l`, `ps auxww`.
- WireGuard peers (`wg show`; never `wg showconf`), OpenVPN users and certificates, IPsec tunnels and
  mobile clients.
- DNS Resolver/Forwarder host and domain overrides, custom options, and Python scripts; DHCP options and
  static mappings; pfBlockerNG feeds and allow lists.
- Installed packages and repositories, Shellcmd, Cron, Filer, and System Patches entries, and system
  crontabs.
- Logs: system, authentication, firewall, VPN, DNS, DHCP, and package logs. Local logs are finite and
  cycle, so export them before they rotate and before any reboot. Pull matching records from the remote
  syslog server if one exists.
- AutoConfigBackup: the list of backups held by the service (dates only) as an off-box timeline.
- For virtualized firewalls: a VM snapshot (including memory if the hypervisor supports it) before
  changes.

## Scope checks specific to pfSense

- Every device behind it: traffic may have been intercepted or redirected (DNS overrides, rogue DHCP
  options, malicious NAT). Check for credential theft on services that traffic passed through.
- Every VPN peer and remote site: their keys were on the firewall.
- Every system whose credentials are stored in the configuration: dynamic DNS accounts, remote syslog,
  LDAP/RADIUS bind accounts, SMTP and other notification accounts, package credentials (for example feed
  subscriptions or IDS rule codes), HA sync peers, and Nexus registration.
- Anywhere configuration backups were sent or downloaded to, including the AutoConfigBackup device key.
- The admin workstations used to manage the firewall.
- For virtualized firewalls: the hypervisor and its other guests.

## Eradication and recovery

- If firewall integrity is in doubt, **reinstall from verified vendor media** (Netgate installer or
  image, with its published checksum) rather than cleaning the running system. On Netgate appliances,
  follow the model's documented reinstall procedure.
- Restore configuration only from a backup taken **before** the earliest plausible compromise, and diff it
  against the compromised configuration to understand what the attacker changed. Don't restore attacker
  changes, and recheck Shellcmd, Cron, Filer, System Patches, and package entries in the restored file
  before loading it.
- Reinstall packages from the official Package Manager rather than restoring package files.
- **Rotate every secret that was in the configuration**, because the attacker could read it: admin and
  user passwords, WireGuard keys (new keys for the firewall and every peer), OpenVPN CA and certificates
  (reissue, and revoke the old ones), IPsec keys, certificate private keys, dynamic DNS, syslog,
  LDAP/RADIUS, SMTP, package, and HA sync credentials. Generate a new AutoConfigBackup device key and
  encryption password.
- Before reconnecting the WAN: current supported release with patches applied, management not reachable
  from WAN, only expected port forwards and no UPnP, privileges reviewed, VPN peers re-issued, packages
  and persistence entries reviewed, and remote logging working.

## Quick checklist tailored for pfSense

Start with the core quick checklist, plus:

- [ ] If the firewall itself may be compromised, disconnect the WAN upstream (modem or hypervisor), not at
      the firewall, and keep console access.
- [ ] Export Config History and logs before rebooting or before logs rotate.
- [ ] List users, privileges, port forwards, floating rules, VPN peers, DNS overrides, and Shellcmd/Cron/
      Filer/System Patches entries; screenshot anything unexpected.
- [ ] Pause HA sync and check any Nexus controller.
- [ ] Plan to reinstall from verified vendor media and rotate every secret in the configuration.
