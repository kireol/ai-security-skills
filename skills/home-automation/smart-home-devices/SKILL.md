---
name: smart-home-devices
description: >-
  Security assessment, hardening, remediation, and incident response for consumer smart home devices and
  their hubs: smart plugs, bulbs, switches and dimmers, locks, thermostats, sensors, garage-door openers,
  robot vacuums, voice assistants and smart speakers, hubs and bridges (Philips Hue, SmartThings, Aqara,
  Zigbee/Z-Wave coordinators, Matter controllers, Thread border routers), and DIY or open firmware
  (ESPHome, Tasmota, Shelly local APIs). Use when inventorying smart home devices, reviewing vendor cloud
  accounts, shared users, locks and garage doors, local APIs, Zigbee/Z-Wave/Thread/Matter security,
  firmware support, IoT network placement, voice assistants, privacy, or resale and disposal, or when a
  smart home device or account may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Consumer smart home devices, hubs, and bridges from any vendor, plus ESPHome, Tasmota, and Shelly Gen1/Gen2+ firmware (verify each device's current firmware, app, and support status)"
  audience: "home, homelab"
  finding_prefix: "SHD"
  modes: "discover, recommend, remediate, respond"
---

# Smart Home Device Security

Act as a careful, evidence-driven security engineer for the devices that make a home "smart". These are
many small, cheap, rarely updated computers, often invisible on the network except as a MAC address, most
of them controlled through a vendor cloud account, and some of them able to unlock a door, open a garage,
disarm an alarm, or turn off the heating. Weaknesses here leak presence and household routines, give an
attacker a foothold on the network, or move things in the physical world. Identify, explain, prioritize,
remediate (only when authorized, and with the user physically in control of anything that moves), and
verify weaknesses in the devices, their hubs and radio networks, their accounts, and what they can reach.

## How to use this skill

This skill holds only smart-home-device-specific guidance. It builds on the shared core, which always
applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Smart-home-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and advisories are in [references.md](references.md).

Related skills, assessed alongside this one rather than repeated here:

- [home-assistant](../home-assistant/SKILL.md): the Home Assistant instance itself, its automations, and
  the Zigbee/Z-Wave/Matter integrations and keys it stores.
- [mqtt](../mqtt/SKILL.md): the MQTT broker that Tasmota, Shelly, ESPHome, and Zigbee2MQTT often report to.
- [wifi-and-switches](../../network/wifi-and-switches/SKILL.md): IoT SSIDs, VLANs, and the router's UPnP.
- [ip-cameras](../../surveillance/ip-cameras/SKILL.md) and
  [video-doorbells](../../surveillance/video-doorbells/SKILL.md): cameras and doorbells.
- [smart-tvs](../../consumer-devices/smart-tvs/SKILL.md): TVs and streaming devices.
- The network firewall skill in use (for example [opnsense](../../network/opnsense/SKILL.md)) for egress
  rules and multicast/mDNS relaying between segments.

## Smart-home-specific principles

- **Physical effect raises the stakes.** Locks, garage-door and gate openers, alarm panels and sensors,
  smoke/CO and leak detectors, water shut-off valves, heating and cooling, and anything switching a heater,
  pump, or medical device are **high-impact devices**. In every mode: never send them a command, never
  "test" them, and treat every change to them, their accounts, their automations, or their hub as at least
  **C2**, carried out only by the user, in person, with a manual fallback (a physical key, the opener's
  wall button and manual release, the alarm keypad) confirmed working first.
- **Never touch a device to learn about it.** Toggling a plug or switch can turn off a freezer, a router,
  a medical device, or a space heater someone relies on. Discover reads app screens, router tables, and
  passive announcements; it does not toggle, dim, open, unlock, arm, disarm, or reboot anything.
- **Never test passwords or keys.** Don't try default credentials, guess PINs or passwords, or run exploit
  or proof-of-concept scripts against any device, hub, or local API. Ask the user how each device and
  account was set up.
- **The account is usually the real control.** Most devices are controlled through a vendor cloud
  account, and whoever holds that account (or a shared-user invitation, or a linked voice assistant) holds
  the devices. Account security, shared users, and linked services matter as much as the device.
- **Setup codes, keys, and stickers are secrets.** Matter setup QR codes and 11-digit manual codes, Z-Wave
  S2 DSK labels, Zigbee install codes, HomeKit setup codes, and Wi-Fi credentials stored on DIY devices
  can let someone join or take over a device. Never ask the user to paste them, and redact them from photos
  and screenshots.
- **Never read radio network keys.** Zigbee network keys, Z-Wave S0/S2 keys, Thread network credentials
  (operational dataset), and Matter fabric credentials are equivalent to control of every device on that
  network. Record only whether they are default or unique, how they are backed up, and who can read them,
  never their values.
- **Local APIs often have no authentication by default.** Shelly devices document HTTP authentication as
  optional (Gen1: "disabled by default"), Tasmota's web UI has no password unless one is set, and ESPHome
  devices are protected only by the API encryption key and OTA settings in their YAML. Anyone on the same
  network segment may be able to control them. Network placement is therefore the main control.
- **Vendors leave.** Cloud services shut down (for example, Belkin ended Wemo cloud and app support for
  most Wemo products on 2026-01-31), and devices that depended on them lose features or stop working.
  Check support status and local-control options before the user relies on a device for safety.
- **Firmware flashing, factory resets, and re-pairing are the user's job.** They can brick a device,
  remove it from every automation, or (for locks) leave a door in an unknown state. The agent never
  performs them.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Cloud-only Wi-Fi device** (many plugs, bulbs, sensors, and Tuya-platform white-label devices) | Set up only in a vendor or white-label phone app; no local UI; talks to a vendor cloud. | Security is mostly the vendor account (password, MFA, shared users) and vendor-pushed firmware. Blocking internet access usually breaks it. White-label devices from one platform share that platform's cloud and app, whatever the brand on the box. |
| **Hub or bridge with a radio mesh** (Philips Hue Bridge, SmartThings, Aqara, IKEA, and similar) | A small wired box; end devices are Zigbee, Z-Wave, Thread, or Bluetooth and never appear on the IP network. | The hub is the network-facing attack surface and holds the radio keys. Inventory end devices from the hub's app, not the router. |
| **Self-run coordinator** (Zigbee or Z-Wave USB stick or network coordinator with Zigbee2MQTT, ZHA, Z-Wave JS) | A USB radio on a server or Home Assistant host, or a small Ethernet/Wi-Fi coordinator. | The user owns the keys and backups. Zigbee2MQTT's documented defaults include a fixed network key unless `GENERATE` was used (domain F). Assess the host with its own skill. |
| **Matter devices** (over Wi-Fi, Ethernet, or Thread) | Matter logo and setup QR/manual code on the device or box; added through a Matter controller (Apple Home, Google Home, Amazon Alexa, SmartThings, Home Assistant). | Local control by standard; can be shared with several controllers ("multi-admin"), each a separate fabric. Thread devices need a border router (often a smart speaker, display, Apple TV, or hub). |
| **Apple HomeKit accessory** (non-Matter) | HomeKit setup code; added in the Apple Home app. | Local control through a home hub; access is through Apple Home sharing. |
| **DIY or open firmware** (ESPHome, Tasmota, Shelly with local API, OpenBeken-style firmware) | Local web UI or API; often reported to Home Assistant or an MQTT broker; the user built or flashed it. | The user is the vendor: they set the passwords, keys, and update cadence. Defaults are often open (domain E). |
| **Voice assistant / smart speaker or display** | Echo, Nest/Google, HomePod, and similar; may also be a Thread border router or Matter controller. | Microphones, purchasing, linked services, and the ability to control locks by voice (domain I). |
| **Robot vacuum or mower** | App-controlled; some models have cameras, microphones, and build maps of the home. | Camera and map privacy, cloud account, and resale (domain J, K). Some owners run open firmware. |
| **Professionally installed system** (alarm panel, access control, installer-managed thermostat) | Installer or monitoring company account; dealer app. | The installer may have its own account or remote access. Changes may need the installer and can trigger alarm-monitoring responses. |

## Detection

Hints for recognizing these devices during a network inventory (used by the `full-assessment` skill).
Ports listed are protocol or vendor defaults; firmware can change them. Confirm with the user before
relying on a match, and **never** interact with these services beyond observing that they exist.

- **Many devices are only a MAC address.** Cheap Wi-Fi devices often have no hostname or a generic one
  (for example `ESP_xxxxxx` or a module name). The MAC vendor (OUI) is frequently the **Wi-Fi module
  maker**, not the brand: Espressif (ESP8266/ESP32, used by Shelly, Sonoff, many Tuya-platform devices,
  and almost all ESPHome/Tasmota builds), Tuya-platform OEM module makers, Beken, Realtek, and similar.
  Phones and some devices use randomized MACs, so an unknown OUI is not proof of anything.
- **mDNS/DNS-SD** (UDP 5353):
  - `_hap._tcp`: Apple HomeKit accessories and bridges (also Home Assistant's HomeKit Bridge).
  - `_matter._tcp`: commissioned Matter nodes (operational discovery); `_matterc._udp`: Matter devices
    currently in commissioning mode (a device advertising this is waiting to be paired). Per the Matter
    handbook, Thread devices are advertised by their border router, not by themselves.
  - `_meshcop._udp`: Thread border routers (commonly reported; TXT records include network identifiers).
  - `_hue._tcp`: Philips Hue Bridge (as used by Hue discovery clients; Hue also offers a cloud
    discovery broker).
  - `_esphomelib._tcp`: ESPHome devices with the native API enabled; `_http._tcp` if the ESPHome web
    server is enabled.
  - `_shelly._tcp` and `_http._tcp`: Shelly Gen2+ devices (commonly reported; not vendor-verified here).
- **SSDP** (UDP 1900): Hue bridges, many Wi-Fi plugs (older Wemo-style devices), media and speaker
  devices, and anything doing UPnP. A device creating UPnP port mappings on the router is a finding.
- **Typical local ports** (TCP connect state only):
  - ESPHome native API **6053**; ESPHome OTA **3232** (ESP32) or **8266** (ESP8266) (vendor-documented).
  - Shelly and Tasmota web UI and API on **80**; Shelly Gen2+ RPC over HTTP/WebSocket on 80.
  - Hue Bridge local API over HTTPS on **443** (vendor-documented; plain HTTP on 80 may also answer).
  - Tuya-platform local protocol on **6668** (commonly reported; not vendor-verified here).
  - HomeKit accessories on a dynamic port announced in their `_hap._tcp` record.
- **Hubs with no visible end devices:** a hub's single IP address may stand for dozens of Zigbee, Z-Wave,
  Thread, or Bluetooth devices. Ask the user for the hub app's device list.
- **Open setup access points:** an unconfigured or factory-reset device often broadcasts its own Wi-Fi
  network (for example a `shelly...`, `tasmota-...`, or vendor-named SSID). Tasmota documents a fallback
  access point when Wi-Fi fails. An unexpected open SSID nearby may be a device waiting to be claimed.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Most checks are **user-run in vendor apps and account pages**; the agent guides and records.
Mark anything you can't inspect **Not assessed**.

### Access and baseline

Ask the user for:

- The list of apps and hubs in use (vendor apps, Apple Home, Google Home, Alexa, SmartThings, Home
  Assistant), and for each, the device list (screenshots are fine; redact serial numbers, account names,
  email addresses, setup codes, and room names if the user prefers).
- The router or firewall's DHCP lease table and connected-client list, which VLAN or SSID each client is
  on, and any UPnP mappings. These are the best evidence for devices the user has forgotten.
- Which devices are high-impact (locks, garage/gate openers, alarms, smoke/CO/leak sensors, valves,
  heating, anything powering a heater, pump, or medical device), and what the manual fallback is for each.
- Who in the household, and outside it, has access to each app or account.

Candidate read-only network checks, **not yet verified** against every device. Run them only with the
user's authorization, from a host the user controls, against the user's own devices, one device at a time:

```sh
# Passive discovery listening on the local segment (macOS dns-sd; on Linux: avahi-browse -rt <type>)
dns-sd -B _hap._tcp local.
dns-sd -B _matter._tcp local.
dns-sd -B _matterc._udp local.          # devices currently open for commissioning
dns-sd -B _meshcop._udp local.          # Thread border routers
dns-sd -B _hue._tcp local.
dns-sd -B _esphomelib._tcp local.
# Port-state check only (TCP connect; no protocol interaction). Never send requests to these services.
nmap -sT -Pn -p 80,443,3232,6053,6668,8266 192.0.2.80
```

- Light TCP connect checks only. Embedded devices can hang or reboot under aggressive scanning, UDP
  sweeps, OS detection, or vulnerability-scanner plugins, and a rebooting plug or switch turns its load off.
- For DIY firmware, prefer reading the user's own configuration source (ESPHome YAML, Tasmota template
  notes) for *structure*, with secrets redacted, over querying the device. ESPHome YAML usually points at a
  `secrets.yaml`; never open that file.
- **Never** do any of the following:
  - toggle, dim, open, close, lock, unlock, arm, disarm, start, stop, or reboot any device, including
    "just to identify which one it is";
  - send any request to a local API (Shelly RPC or HTTP API, Tasmota web or `cm?cmnd=` commands, ESPHome
    API, Hue API, Tuya local protocol), even a read-style one, unless the user has explicitly approved that
    specific documented read endpoint. Several "status" commands also print configuration and secrets
    (for example, Tasmota's `WebPassword` with no argument shows the current password);
  - press a hub's link or pairing button, open a Matter commissioning window, pair or re-pair, remove or
    add a device, or create API keys or app registrations on a hub;
  - factory reset, flash, or update firmware, or enable debug, telnet, or developer modes;
  - read, export, or print Zigbee network keys, Z-Wave keys, Thread operational datasets, Matter fabric
    credentials, ESPHome API encryption keys or OTA passwords, Tasmota or Shelly configuration backups
    (they can contain Wi-Fi and MQTT passwords), or a vendor app's tokens;
  - scan or sniff Zigbee, Z-Wave, Thread, or Bluetooth radio traffic;
  - test default or guessed credentials or PINs, or run exploit or proof-of-concept scripts;
  - sign in to the user's vendor accounts, accept terms, or change any account setting on their behalf.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory and identification

- Reconcile three lists: router/firewall clients (IP, MAC, OUI, SSID/VLAN), hub and app device lists, and
  what the user remembers. Every network client should map to a known device and owner; every hub should
  map to its end devices.
- Unknown clients with module-maker OUIs (Espressif, Tuya-platform OEMs, Beken, Realtek): ask the user to
  identify them from the app lists or by the time they were set up. Do not toggle devices to find them.
- For each device: type, brand, real platform (white-label devices often run a common OEM platform; check
  the app's "about" or device-info screen), connection (Wi-Fi, Ethernet, Zigbee, Z-Wave, Thread, Bluetooth,
  Matter), controlling apps/hubs, and whether it is high-impact.
- Devices that are no longer used but are still powered and connected, or still listed in an account.
- Devices whose setup access point is still broadcasting, or that show up in `_matterc._udp` (open for
  commissioning) when nobody is pairing anything.

#### B. Vendor cloud accounts, MFA, and app sign-ins

- For each vendor account (device vendor, white-label platform app, hub vendor, voice assistant,
  ecosystem such as Apple/Google/Amazon/SmartThings): unique password, MFA available and enabled, recovery
  email and phone current and controlled by the user, and sign-in alerts if offered.
- Accounts using the household's main email and password reused from elsewhere.
- Signed-in phones, tablets, and browsers listed by the account; old phones and former household members'
  devices.
- Accounts that also hold payment methods (voice assistants, ecosystem accounts): a compromise allows
  purchases as well as device control.
- Whether high-impact devices (locks, garage openers, alarms) are on accounts with MFA. A lock or garage
  opener on an account without MFA is a high-priority finding where MFA is available.

#### C. Household members, shared users, and linked services

- Shared users and household members in every app and ecosystem: who they are, their role (owner,
  admin, member, guest), and whether each is still appropriate (former partners, roommates, house-sitters,
  contractors, previous owners of the home).
- Lock-specific access: keypad codes, e-keys, temporary or scheduled guest codes, fingerprints, NFC cards,
  and phone keys. Codes for people who no longer need them, and codes that never expire.
- Garage openers and gates: shared access, guest access, and delivery integrations (in-garage or in-home
  delivery services).
- Linked services: voice assistants, IFTTT-style automation services, other ecosystems, insurer or
  energy-company programs, installer or dealer accounts. Each linked service can control the devices it
  was granted. List which ones can control high-impact devices.
- Matter multi-admin: each controller the device is shared with (Settings → connected services or fabrics,
  depending on the controller app). Unknown fabrics are a finding.
- Home Assistant or other local controllers holding tokens for these accounts: assess them with the
  [home-assistant](../home-assistant/SKILL.md) skill.

#### D. High-impact devices: locks, garage doors, alarms, and safety-relevant control

- Inventory every lock, garage-door or gate opener, alarm panel and sensor, smoke/CO/leak detector,
  water valve, thermostat, and smart plug that powers a heater, pump, aquarium, freezer, or medical
  device.
- For each: how it can be operated (app, cloud, voice, automation, keypad, NFC, auto-unlock on approach,
  linked service, local API), and which of those paths can be reached by people outside the household.
- Remote unlock and remote open: enabled? Is it needed? Is there a notification for every unlock or open,
  and does someone actually receive it?
- Auto-unlock and geofencing features: what triggers them (phone location, Bluetooth proximity), and
  whether a shared or lost phone could trigger them.
- Voice control of locks and garage doors (domain I): unlock or open by voice disabled, or protected by a
  spoken PIN. A spoken PIN can be overheard; treat it as weak.
- Smart plugs or DIY relays switching a garage opener, gate, or door strike: often have no authentication
  (domain E), which makes the door as weak as the plug.
- Failure behavior: what happens when Wi-Fi, the hub, the cloud, or power fails. Locks should keep a
  mechanical key or keypad path; garage openers keep their wall button and manual release; batteries in
  locks and sensors are monitored.
- Activity logs: lock and garage event history exists, how long it is kept, and whether it shows anything
  the user doesn't recognize.

#### E. Local APIs and DIY or open firmware

- **Shelly:** Gen1 devices document HTTP authentication (Basic) as disabled by default, enabled through
  `/settings/login`; the `/shelly` endpoint is always unauthenticated. Gen2+ devices use digest
  authentication (SHA-256) enabled with `Shelly.SetAuth`; the vendor documents that MQTT, UART, outbound
  WebSocket, `Shelly.GetDeviceInfo`, and `/shelly` are not protected by it. Check in the Shelly app or web
  UI (user-run) whether authentication is enabled, and whether cloud, MQTT, Bluetooth, and the setup AP are
  enabled and needed.
- **Tasmota:** web UI password set (`WebPassword`; the default username is `admin`)? The vendor recommends
  keeping the web server off except for administration, notes the web server cannot be encrypted, and
  warns that HTTP REST relay control is insecure. Check MQTT: per-device credentials, broker ACLs, and TLS
  (see the [mqtt](../mqtt/SKILL.md) skill). Check `WifiConfig` (the vendor calls the fallback access point a
  risk; option 2 is the riskiest). Configuration backups can expose Wi-Fi and MQTT passwords.
- **ESPHome:** native API `encryption: key` configured (API password authentication was removed in
  ESPHome 2026.1.0; Home Assistant flags devices still using it). OTA: the vendor now recommends OTA
  `encryption` over the older `password`, and documents that without encryption the firmware image,
  which contains Wi-Fi credentials and the API key, travels in plaintext, and that with no password anyone
  who can reach the device can upload firmware. `web_server` enabled? If so, `auth` set, and is the web
  server OTA platform also enabled (it accepts the image over plaintext HTTP)? Secrets kept in
  `secrets.yaml` and out of shared repositories. Read the YAML structure only; never the secret values.
- **Other open firmware** (OpenBeken-style, Valetudo for vacuums, custom builds): which project, how it is
  updated, and what it exposes by default. Check the project's own docs.
- **Hue Bridge and similar hubs:** apps authorized on the bridge's local API (an app gets a key only after
  someone presses the bridge's link button). Ask the user to review the list of connected apps in the
  vendor app or account, where offered, and remove unknown ones.
- **Tuya-platform devices with local control:** a per-device local key retrieved from the cloud lets
  anything on the network control the device; treat stored local keys as secrets.
- Any of these devices controlling a high-impact load (domain D) without authentication is a higher
  priority finding.

#### F. Radio networks: Zigbee, Z-Wave, Thread, Matter, and Bluetooth

- **Zigbee:** network key unique, not a documented default. Zigbee2MQTT documents a fixed default network
  key, PAN ID, and extended PAN ID unless `GENERATE` is set; ask the user (without reading the key) whether
  they used `GENERATE` or a random key. Install-code joining used where the coordinator supports it
  (install codes are mandatory for Zigbee 3.0 devices; joining without them uses a well-known link key).
  Permit-join off except while pairing. Coordinator backups exist and are protected (they contain the key).
- **Z-Wave:** devices included with S2 security, and locks and garage openers with **S2 Access Control**
  (the class intended for locks and garage doors). Devices that fell back to S0 or no security, especially
  locks. Check the controller's device list (Z-Wave JS UI, hub app) for each device's security class. DSK
  labels and QR codes are secret; check whether they are stuck on visible, reachable parts of devices.
- **Thread:** which devices act as border routers (often several, from different ecosystems), and whether
  the user knows which ecosystem holds the Thread credentials. Unexpected border routers.
- **Matter:** which controllers (fabrics) each device belongs to (domain C). Setup QR codes and manual
  codes: where are they stored? A photo in a shared album, a code on the outside of a device, or a box in
  a shared space lets someone add the device to their own controller if they can trigger commissioning
  (basic commissioning reuses the original code). Devices left in commissioning mode (`_matterc._udp`).
- **Bluetooth:** locks and other devices with Bluetooth control: app-based key sharing, and whether old
  phones still hold keys.
- Hub and coordinator placement: physical access to a USB coordinator or hub allows reset or key theft.

#### G. Firmware, updates, and end of support

- Firmware version for each device and hub, automatic updates on or off, and the date of the last update
  the vendor shipped for that model.
- Support status: check the vendor's support or end-of-life pages and announcements. Cloud shutdowns are
  common (for example, the Wemo cloud and app shutdown on 2026-01-31); a device with no vendor cloud and no
  local or standard (Matter, HomeKit, Zigbee, Z-Wave) control path is effectively end-of-life.
- Published support periods and labels. UK PSTI rules (in force since 2024-04-29) require consumer
  connectable products sold in the UK to have unique or user-set passwords, a vulnerability-reporting
  route, and a published minimum security-update period with an end date. The US Cyber Trust Mark is a
  voluntary FCC label; at the time of writing the FCC reports its rollout is still under way, so absence
  of the mark says little about older products. Check current status before relying on either.
- Vendor security advisories for each device family, validated per core triage. No static CVE list here.
- DIY firmware: version of ESPHome, Tasmota, or Shelly firmware, and whether the user has a routine for
  updating it. Some security fixes (for example an ESPHome web server authentication fix in 2025.8.1) only
  arrive by rebuilding or updating.

#### H. Network placement, egress, UPnP, and discovery

- Which SSID/VLAN each device is on. Smart home devices on the main LAN alongside computers and NAS
  devices is a finding where the network can segment (see
  [wifi-and-switches](../../network/wifi-and-switches/SKILL.md)).
- What the IoT segment can reach: admin interfaces, NAS, Home Assistant (only what is needed, for
  example its API and MQTT port), the router's management UI.
- What can reach the IoT segment: ideally only the controllers (Home Assistant, hubs) and admin hosts.
- Egress: devices with local control (ESPHome, Tasmota, local Shelly, Zigbee/Z-Wave hubs used locally)
  often need no internet access, or only NTP. Check the firewall for per-device or per-segment egress
  rules, and DNS logs for devices calling clouds the user didn't expect.
- Multicast and mDNS relaying between segments (needed for HomeKit, Matter, Cast, AirPlay): relayed only
  between the segments that need it.
- **UPnP:** enabled on the router? Smart home devices and hubs creating port mappings; any mapping is a
  finding to explain.
- Port forwards to any device or hub; remote access through a local API exposed to the internet is a
  P1-class finding.
- Thread and Matter over IPv6: IoT segments may have IPv6 and link-local traffic that IPv4-only rules
  don't cover.

#### I. Voice assistants and smart speakers

- Voice purchasing: enabled? Protected by a voice code? Limited to recognized voices?
- Which entities are exposed to the assistant, and whether unlock, open garage, and disarm are allowed by
  voice. Lock vendors commonly require a spoken PIN for voice unlock and disable it after a few wrong
  attempts; anyone nearby can hear the PIN, and a voice heard through a window or a TV can issue commands.
- Voice recordings and history: retention setting, whether recordings are saved, and who in the household
  can review them. Amazon removed the Echo "Do Not Send Voice Recordings" option on 2025-03-28 (users were
  moved to "Don't save recordings"); check the current options for each assistant.
- Microphone mute habits for rooms where privacy matters; drop-in, intercom, and calling features, and who
  can drop in.
- Skills, actions, and third-party integrations linked to the assistant (domain C), and household members
  or guests who can use them.
- Speakers and displays that are also Thread border routers or Matter controllers (domain F).

#### J. Robot vacuums, cameras, microphones, and home maps

- Which robots have cameras, microphones, or remote video features, and whether those are enabled.
- Maps of the home stored in the vendor cloud (they reveal layout and sometimes room names and objects).
- Video or remote-view PIN: on some models researchers found the PIN was checked only in the app; do not
  treat it as strong protection. Published research on one vendor's robots (DEF CON 2024) also showed
  takeover over Bluetooth at short range and continued access after resale; check the user's vendor for
  advisories and firmware updates.
- Account sharing for the robot and its maps; who can view the camera.
- Other camera- or microphone-bearing smart home devices (displays, some thermostats and sensors, pet
  cameras) and their privacy settings. Cameras and doorbells proper go to their own skills.

#### K. Resale, disposal, and devices from previous owners

- Devices that came with the home (locks, thermostats, garage openers, alarm panels, hubs): are they
  removed from the previous owner's account and re-enrolled in the user's, with all old codes and users
  deleted? A previous owner still able to unlock a door or open a garage is a high-priority finding.
- Second-hand devices: factory reset and re-paired by the user, firmware updated.
- Devices the user plans to sell, return, or discard: a removal procedure that both removes the device
  from every account and fabric and factory resets it. Removing only from the account, or only resetting,
  may leave either access or data (Wi-Fi credentials, maps, codes) behind.
- DIY devices with Wi-Fi credentials compiled into their firmware: wiped or physically destroyed before
  disposal.

#### L. Physical, power, and availability

- Physical access to hubs, coordinators, and bridges (reset buttons, USB ports).
- Outdoor-mounted devices (keypads, garage controllers, sensors) that can be opened, reset, or rewired.
- Power: what turns off when a smart plug or relay reboots or loses power, and its power-on state setting
  (on, off, or last state). Heaters and pumps on smart plugs: whether the plug is rated for the load.
- Dependence on internet and cloud: what stops working during an outage, especially heating and locks.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

Before recommending a change, list what depends on the current state:

- **Household routines:** automations, schedules, and scenes in every app and in Home Assistant that use
  the device; voice routines; people who open the door or garage with their phone every day.
- **High-impact devices:** who relies on each lock, opener, alarm, and thermostat, and what the manual
  fallback is. Never plan a change to them that could leave a door unlocked or locked with no way in.
- **Integrations and linked services:** Home Assistant, voice assistants, other ecosystems, and MQTT
  topics. Changing a device's password, enabling authentication, or moving it to another VLAN breaks any
  integration that hasn't been updated.
- **Radio networks:** changing a Zigbee network key or channel requires re-pairing every device;
  changing ESPHome encryption keys can leave devices unreachable until re-flashed; removing a Thread
  border router can strand Thread devices.
- **Cloud dependence:** blocking internet access stops cloud features, remote access, firmware updates,
  and sometimes the device entirely.
- **Multicast and discovery:** moving devices to another segment can break HomeKit, Matter, Cast, and
  local discovery unless mDNS is relayed.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Vendor account without MFA | Enable MFA; unique password; current recovery details; sign out unknown sessions. | Shared logins stop working; other household members need their own accounts or invitations. |
| Shared or former users | Remove former users, guests, and old phones; give people their own accounts with the lowest role. | Removed people lose access immediately; confirm before removing anyone who still lives there. |
| Stale lock codes or e-keys | Delete unused codes; give guests time-limited codes. | Someone may be locked out; tell them first. |
| Remote unlock/open not needed | Disable remote unlock or remote open; keep notifications on. | The user can't let people in remotely. |
| Voice unlock or garage open by voice | Disable, or require a spoken PIN and accept it is weak. | Less convenient. |
| Voice purchasing on | Disable, or require a voice code. | Voice shopping stops or needs the code. |
| Local API without authentication | Enable authentication (Shelly `SetAuth` / login, Tasmota `WebPassword`); turn off unused web servers, cloud, MQTT, or setup AP. | Integrations using the API must be given the credentials; test each one. |
| ESPHome without API encryption or OTA protection | Add an API `encryption` key and OTA `encryption`, then re-flash; remove legacy API passwords. | One-time re-flash, possibly over USB; update the key in Home Assistant; lost keys need a serial re-flash. |
| Zigbee network on a default key | Plan a new network with a random key (`GENERATE`) at a convenient time. | Every Zigbee device must be re-paired; a large job. |
| Z-Wave lock without S2 | Exclude and re-include with S2 Access Control. | The lock is briefly unavailable; the user must be present at the door. |
| Unknown Matter fabric or linked service | Remove it in the device's controller app. | Anything using it stops controlling the device. |
| Smart home devices on the main LAN | Move them to an IoT SSID/VLAN with rules allowing only what they need. | C2 project; plan per device group; mDNS relaying for HomeKit/Matter. |
| No egress control | Block internet for local-only devices (allow NTP if needed). | Cloud features and vendor updates stop; plan manual update checks. |
| UPnP on, devices creating mappings | Disable UPnP, or restrict it to specific hosts. | Some apps lose remote access; consoles may need manual forwards. |
| End-of-support device or dead cloud | Replace, or move to a supported local/standard control path; never rely on it for safety. | Cost; re-creating automations. |
| Robot camera or remote view on | Disable camera features not used; review maps and sharing. | Object avoidance or remote view may stop. |
| Previous owner's devices | Remove from the old account (vendor support may be needed), reset, re-enroll, delete all codes. | The device is unusable until re-enrolled; for locks, re-key or rely on mechanical keys meanwhile. |
| No disposal procedure | Adopt a remove-from-account-then-factory-reset routine. | None. |

Hiding SSIDs, changing ports, and MAC filtering are supplementary only. Never recommend them as the main
fix.

Group the plan: immediate containment (unknown users or fabrics, previous-owner access, exposed local
APIs) → urgent fixes (MFA on accounts controlling locks and garage doors, voice unlock) → high-priority
hardening (local API authentication, segmentation, egress) → routine maintenance (updates, end-of-support
replacement) → optional defense in depth. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Smart-home specifics:

- **The user makes the changes.** Most changes are made in vendor apps and accounts the agent should not
  sign in to. The agent explains each step, the user performs it and shares the result, and the agent
  records before and after.
- **High-impact devices need the user's direct control and presence.** Any change to a lock, garage-door
  or gate opener, alarm, smoke/CO/leak sensor, valve, heating, or anything with a physical effect (its
  account, codes, firmware, pairing, network, or automations) is **C2** at minimum and is carried out only
  by the user, physically at the device, after confirming the manual fallback works (physical key, keypad,
  wall button and manual release, alarm keypad, manual thermostat control). Never schedule such changes
  for when nobody is home, and never chain them in a standing authorization.
- **Account changes first, then devices.** MFA, password, recovery, and removing unknown users or sessions
  are usually the fastest, safest wins.
- **Before enabling authentication on a local API**, list every integration that calls it (Home Assistant,
  scripts, other apps) and have the new credentials ready for each. Change one device, confirm every
  integration still works, then continue.
- **ESPHome key changes** require re-flashing; confirm the user has USB/serial access or a working OTA path
  first, because a lost or mismatched key can leave the device unreachable over the network.
- **Network moves** (new VLAN or SSID): move one device group at a time, test control from every app and
  controller, and keep the old network until everything works. Devices on old Wi-Fi standards may not join
  a stricter network.
- **Firmware updates** are run by the user from the vendor app or project tooling. Don't update a lock or
  garage opener while away or at night; low batteries can brick a lock mid-update.
- **Re-pairing and network rebuilds** (new Zigbee key, Z-Wave S2 re-inclusion, Matter re-commissioning) are
  planned projects the user performs, with a written list of every device and automation to restore.

After each change, follow the core "after a change" steps: confirm the setting in the app, confirm that
every controller and integration still works, confirm high-impact devices still operate by both smart and
manual means (the user does this in person), and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Sending any command to a device or local API, including to "verify" a fix: the user operates devices.
- Unlocking, opening, disarming, or changing the state of any lock, garage door, gate, alarm, or safety
  device.
- Factory resets, firmware flashing (including serial/USB flashing of DIY devices), and re-pairing.
- Reading, exporting, or rotating Zigbee, Z-Wave, Thread, or Matter keys or credentials by script.
- Changes to professionally installed or monitored alarm and access-control systems without the installer
  or monitoring company (changes can trigger dispatch or void monitoring).
- Rewiring mains-powered devices (switches, relays, thermostats, garage openers): electrician territory.

---

## Respond

On any P0 indicator (an unknown person able to unlock a door or open a garage, unexplained unlocks or
opens, unknown users or fabrics on high-impact devices), switch to Respond immediately. Follow the core
playbook plus the smart-home-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### SHD-001: Garage door relay on the main LAN with an unauthenticated local API

**Confidence:** Confirmed
**Priority:** P1. Anyone or anything on the main LAN, including a compromised laptop or a guest's device,
can open the garage, which gives access to the house.
**State:** Open
**Component:** Wi-Fi relay module (Shelly Gen2-family) wired to a garage-door opener's wall-button input;
local HTTP RPC on TCP 80; firmware current at assessment time.
**Evidence:** Observed 2026-10-20 (user-run): the device's web UI at `192.0.2.45` opened without a login
prompt, and its settings page showed authentication disabled. The router's client list places it on the
main LAN SSID with computers and a NAS. The user confirmed the relay triggers the opener. No command was
sent to the device during the assessment.
**Expected secure state:** local authentication enabled (Shelly Gen2+ digest authentication via
`Shelly.SetAuth`, vendor API documentation); the device on an IoT segment reachable only from the home
automation controller.
**Exposure and prerequisites:** any client on the main LAN; no credentials needed. Not reachable from the
internet (no port forwards or UPnP mappings found). The vendor documents that some endpoints and MQTT stay
unauthenticated even with authentication enabled, so segmentation is still needed.
**Dependencies / blast radius:** Home Assistant at `192.0.2.20` controls the relay and runs a "close at
night" automation; two household members open the garage from the Home Assistant app.
**Recommended remediation:** (1) with the user at the garage and the wall button and manual release
confirmed working, enable authentication in the device's web UI and update the Home Assistant integration
with the new credentials; the user confirms open and close from the app. (2) Later, move the relay to the
IoT VLAN and allow only Home Assistant to reach it.
**Operation class:** C2 (could interrupt the user's ability to open or close the garage; physical effect).
**Approval required:** Yes, and the user performs the change in person.
**Verification:** the web UI now prompts for credentials; Home Assistant still operates the door (user
confirms in person); the "close at night" automation runs that evening.
**Rollback:** disable authentication in the device's web UI and restore the previous integration
settings; the wall button works throughout.

---

## Version history

- **1.0** (2026-10-30): Initial version.
