# MQTT: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only MQTT-specific steps.

A compromised broker, or an attacker holding a client credential with broad rights, can command every
device on the bus, change what Home Assistant believes is happening, and read presence and camera data.
**Physical safety comes before evidence:** if MQTT-controlled locks, garage doors, sirens, or heating may
be under an attacker's control, secure them manually first.

## Triage and containment

- **Indicators:** unknown client IDs or usernames in `connection_messages` logs; connections from
  unexpected addresses (IoT, guest, or internet); devices changing state with no matching automation or
  user action; Zigbee2MQTT permit-join opening, new Zigbee devices, OTA updates, or device removals nobody
  started; Frigate detection or recording turned off; new Home Assistant entities from the discovery
  prefix; retained command messages that weren't there before; new bridges, listeners, users, ACL
  grants, or `allow_anonymous true` in the configuration; the dynamic-security admin role granted to a
  new client.
- **Physical safety first:** lock doors manually, check garage doors and gates, and arm the alarm from its
  own panel. Consider pausing Home Assistant automations that react to MQTT topics for locks and alarms.
- **Cut outside paths:** remove port forwards or UPnP mappings to the broker, stop bridges to cloud
  brokers (comment out the `connection` block and restart, with approval), and block the broker's ports
  from untrusted segments at the firewall. Prefer firewall-level containment, which doesn't touch the
  broker's state.
- **Disable, don't delete, suspect credentials:** with dynamic security, disable the client (this also
  disconnects it); with a password file, remove that one entry after backing up the file, then reload.
  Record exactly what you changed.
- **Don't wipe retained messages or the persistence file**: they are evidence of what was published.
- If the broker host itself may be compromised, isolate it at the switch, firewall, or hypervisor.

## Evidence to preserve (MQTT-specific)

Collect before changing anything. Treat configuration, password, and dynamic-security files as secret
material: copy them to encrypted storage and don't print or upload them.

- Broker logs (file, syslog, journal, or container logs) covering the suspected window, including
  connects, disconnects, and authentication failures. Container logs disappear when the container is
  recreated: export them first.
- Copies of the configuration directory, password file, ACL file, PSK file, dynamic-security JSON, and
  their timestamps and permissions.
- The persistence file (`mosquitto.db` or the configured location), which holds retained and queued
  messages.
- With approval, a retained-topic listing (topic names and retain flags), captured once.
- Zigbee2MQTT logs and its `data` folder state (device list, coordinator backup); Frigate logs; Home
  Assistant logbook entries for MQTT-controlled entities and its MQTT integration log.
- Firewall or router logs for connections to the broker ports.
- On a VM or container host: a snapshot before changes.

## Scope checks specific to MQTT

- **Every client credential** on the broker: an attacker with configuration or password-file access has
  the hashes and any plaintext bridge passwords; assume all of them are exposed.
- **Home Assistant:** entities created through discovery, automations triggered by MQTT topics, and the
  Home Assistant instance itself (use the [home-assistant](../home-assistant/SKILL.md) skill).
- **Zigbee network:** devices joined during the window, whether the network key or a coordinator backup
  was exposed (`bridge/request/backup` responses, the data folder), and OTA updates pushed.
- **Devices with stored MQTT settings:** Tasmota, ESPHome, Shelly, and similar devices whose broker
  address could have been changed to an attacker's broker.
- **Bridged and cloud brokers:** the remote account, what was bridged in or out, and the bridge
  credentials.
- **Data exposure:** camera snapshots, presence and location topics that could have been read.

## Eradication and recovery

- If the broker host or configuration was modified, rebuild the broker from a clean package or official
  image and restore configuration from a backup taken before the earliest plausible compromise. Diff it
  against the compromised configuration (listeners, anonymous settings, ACLs, bridges, plugins).
- **Rotate every MQTT credential:** create new passwords for every client and update each integration and
  device; reissue client certificates and revoke old ones via the CRL; new PSKs; new bridge credentials at
  the remote broker or cloud account; new dynamic-security admin credentials.
- Clear attacker-created retained messages, one topic at a time with the user, knowing what each device
  will do.
- Review Zigbee devices and remove unknown ones; if the network key was exposed, plan a re-key or
  re-pair with the user (a large project).
- Before reopening access: anonymous access off, per-client ACLs with command topics restricted, TLS for
  clients on untrusted segments, no internet exposure, bridges reviewed, and connection logging on.

## Quick checklist tailored for MQTT

Start with the core quick checklist, plus:

- [ ] Secure the home physically: locks, garage, alarm, heating.
- [ ] Block the broker from the internet and untrusted segments at the firewall; stop cloud bridges.
- [ ] Export broker logs and copy configuration, password, ACL, dynamic-security, and persistence files
      before changing anything.
- [ ] Disable suspect clients; check Zigbee2MQTT for new devices, permit-join, and OTA activity.
- [ ] Plan to rotate every MQTT credential and review every ACL and retained command topic.
