# VMware ESXi: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only ESXi-specific steps.

A compromised ESXi host is a compromise of every VM on it: the attacker can stop VMs, copy or encrypt
their disks, open consoles, and delete snapshots. If vCenter is compromised, every host it manages is too.
ESXi ransomware usually runs quickly: VMs are powered off, then files on every datastore are encrypted or
renamed. If the host itself may be compromised, **don't rely on it, or on any VM it runs, to contain the
incident**.

## Triage and containment

- **Indicators on the host:** VMs powered off that nobody stopped; datastore files with new extensions or
  ransom notes next to `.vmdk` and `.vmx` files; a changed `/etc/motd` or Host Client landing page; SSH or
  ESXi Shell enabled unexpectedly; `SuppressShellWarning` turned on; new local accounts or role
  assignments; a new or renamed directory group trusted as administrators; `execInstalledOnly` or the
  acceptance level lowered; new `CommunitySupported` VIBs; changes to `/etc/rc.local.d/local.sh` or the root
  crontab; unexpected binaries in `/tmp`, `/scratch`, or on datastores; firewall rulesets opened; syslog
  forwarding removed; unusual outbound connections (`esxcli network ip connection list`).
- **Indicators in vCenter:** unknown SSO users or identity sources, new roles or permissions, tasks nobody
  started (snapshot deletion, VM deletion, host profile changes), and logins from unexpected addresses.
- **If encryption is in progress:** the priority is to stop it spreading. Disconnect the host's uplinks at
  the switch, or disable its switch ports, and use only the DCUI or BMC console from here. If the host can
  still reach NFS or iSCSI storage, cut that path too, because the attacker can encrypt it. If the site's
  firewall runs on this host, the internet connection goes down with it; plan that with the user.
- **Don't reboot or power off** unless destruction is ongoing and network isolation is impossible. Much of
  ESXi's state and logging is in memory and is lost at reboot.
- **If one VM is compromised and the host is trusted:** with approval, disconnect the VM's virtual NIC or
  move it to an isolated port group, and take a snapshot (with memory) before changing anything inside it.
- **If the BMC may be compromised:** the user disconnects the BMC's network port or management VLAN. The
  BMC outranks the host.
- **Protect backups first:** cut the host's and vCenter's access to backup storage and backup-server
  credentials; confirm offline or immutable copies exist.

## Evidence to preserve (ESXi-specific)

Collect from the DCUI, the BMC console, or a clean admin workstation, before changing anything:

- A support bundle (`vm-support`, or Host Client → Generate support bundle), written off the host. It
  contains logs and configuration; treat it as secret material.
- Logs, if no bundle is possible: `/var/log/` (`hostd.log`, `vpxa.log`, `shell.log`, `auth.log`,
  `vobd.log`, `vmkernel.log`, `syslog.log`), and the persistent scratch location. Also the remote syslog
  server's copy, which the attacker may not have reached. `shell.log` records commands typed in the ESXi
  Shell and SSH.
- Configuration state: `esxcli system version get`, `esxcli software vib list`, `esxcli software
  acceptance get`, `esxcli system account list`, `esxcli system permission list`, firewall rulesets and
  allowed IPs, advanced settings (Security, UserVars, Config.HostAgent), `/etc/rc.local.d/local.sh`, root
  crontab, and `authorized_keys` comments and fingerprints.
- Running state: `esxcli network ip connection list`, `esxcli vm process list`, and a process listing
  (`ps -c` or equivalent; verify on the build).
- Datastore listings with timestamps (`ls -la` per VM folder), ransom notes, and a sample of encrypted
  files. Copy them; don't open or run them.
- vCenter: events, tasks, SSO logs, and a vCenter support bundle.
- Directory: who created or changed the group ESXi trusts as administrators, and when.

## Scope checks specific to ESXi

- **Every VM on the host**, especially virtualized firewalls, NAS, DNS, domain controllers, and password
  managers: treat their secrets as exposed.
- **vCenter and every host it manages**, and any host that shares the same `root` password or SSH keys.
- **The directory:** if attackers used a trusted admin group, the directory itself is compromised; scope it
  with the directory owner.
- **Shared storage:** NFS and iSCSI targets the host mounted; other hosts using them.
- **Backup systems:** credentials stored in the backup tool for this host or vCenter; check for deleted
  backups and logins from the host's or vCenter's address.
- **Admin workstations** used to manage the host (stolen sessions and saved passwords are a common entry).
- **The BMC** and anything sharing its management network.

## Eradication and recovery

- **Reinstall the host from verified media** (checksum from the Broadcom portal) rather than cleaning it.
  Restore configuration only from a backup known to predate the compromise, and re-check it.
- **Encrypted VMs:** restore from backups taken before the earliest plausible compromise, onto an isolated
  network first. Don't run decryptors or "recovery" scripts against the only copy of a datastore; copy
  first and involve a specialist (hard stops in the skill). Check government and vendor guidance for the
  specific ransomware family before paying anyone.
- **Rotate secrets:** `root` on every host, vCenter SSO administrators, integration and backup accounts,
  SSH keys, directory accounts with host rights, iSCSI CHAP and NFS credentials, BMC credentials, and
  secrets inside affected VMs.
- **Close the entry path before reconnecting:** patched, supported build; OpenSLP off; SSH off; management
  reachable only from the management network; trusted admin group fixed; acceptance level and
  `execInstalledOnly` restored; remote syslog in place; backups separate from the host and its
  credentials.

## Quick checklist tailored for ESXi

Start with the core quick checklist, plus:

- [ ] If encryption may be running, isolate the host and its storage paths at the switch; use the DCUI or
      BMC console.
- [ ] Don't reboot; generate a support bundle and copy logs, `shell.log` especially, off the host.
- [ ] Cut the host's and vCenter's access to backups and confirm untouched copies exist.
- [ ] Check vCenter and the directory group ESXi trusts as administrators; scope every managed host.
- [ ] Reinstall from verified media, restore VMs from pre-compromise backups to an isolated network, and
      rotate every credential the host and vCenter held.
