# Smart Home Devices: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only smart-home-device-specific steps.

A smart home incident can be an account takeover (someone else controls the devices through the vendor
cloud), unwanted access by a known person (a former partner, roommate, or previous owner still holding
access), a compromised device used as a foothold on the network, or a device misbehaving because of a bug
or a broken automation. **Physical safety comes first**: if someone may be able to unlock a door, open a
garage, or disable an alarm, secure the physical space before anything else.

If the incident involves a person the user knows, such as a current or former partner, it may be a
safety situation rather than only a technical one. Changes such as removing someone's access can alert
them. Let the user decide the order, and point them to local domestic-abuse or tech-safety support
services if they want help planning.

## Triage and containment

- **Indicators:** devices turning on or off, locks unlocking, or garages opening with no matching
  automation or household action; unknown entries in lock or garage history; new shared users, guests,
  lock codes, linked services, or Matter fabrics; sign-in or new-device alerts from a vendor account;
  changed account email, phone, or MFA settings; devices showing up on the network that nobody added; a
  device contacting unexpected destinations or showing heavy outbound traffic; UPnP mappings nobody
  created; voice-assistant purchases or history entries nobody made.
- **Rule out the ordinary first, without operating devices:** review automations, schedules, scenes, and
  linked services (Home Assistant, voice routines, energy-company programs) that could explain the event.
  Many "the lights turned on by themselves" reports are automations or power cuts (power-on state).
- **Secure the physical space (user-run, in person):** for locks, lock with the physical key or thumb
  turn and, if the smart lock may be controlled by someone else, use a mechanical deadbolt or temporarily
  disable the smart function as the vendor documents. For garage openers, use the opener's lock-out or
  vacation mode if it has one, or the user can unplug the opener and secure the door manually (manual
  release and a manual lock if fitted). For alarms, contact the monitoring company if the system is
  monitored. Never have the agent send commands to these devices.
- **Contain the account:** from a trusted device, change the vendor account password, enable MFA, sign out
  all other sessions, check the recovery email and phone, and remove unknown shared users, guests, lock
  codes, e-keys, and linked services. If the account email was changed, use the vendor's account recovery
  and contact vendor support.
- **Contain a compromised device on the network:** block it at the firewall or move it off the network
  (the user can unplug a non-critical device). Prefer a firewall block over unplugging when the device
  powers something important (heating, a freezer, a pump), and keep the device powered if evidence matters.
- **Don't factory reset or re-pair yet:** that destroys device-side evidence and history and may leave a
  lock in an unknown state. Collect evidence first unless physical safety requires immediate action.

## Evidence to preserve (smart-home-specific)

Collect from a trusted device, before changing anything where safety allows:

- Screenshots or exports of lock and garage event history, alarm event logs, and device activity history
  from each vendor app (with timestamps and which user or code triggered each event).
- The list of shared users, guests, lock codes (names and dates, not the codes), linked services, Matter
  fabrics and connected controllers, and signed-in devices for each account.
- Vendor account security pages: recent sign-ins, new-device alerts, and email notifications about
  account changes.
- Router and firewall evidence: DHCP leases and client lists (IP, MAC, first seen), UPnP mapping tables,
  firewall and DNS logs for the affected devices.
- Hub and controller logs: Home Assistant logbook and history (see the
  [home-assistant](../home-assistant/incident-response.md) skill), Zigbee2MQTT or Z-Wave JS logs, Hue or
  other hub activity, MQTT broker logs (see the [mqtt](../mqtt/incident-response.md) skill).
- For DIY devices: the current firmware version and configuration structure (not secret values), and any
  device log the user can view in its web UI without changing anything.
- Voice-assistant history entries and purchase history relevant to the event.
- Note the times of any physical events the household noticed (a door found unlocked, a garage found
  open) for the timeline.

## Scope checks specific to smart home devices

- Every device on the same vendor account or ecosystem account: an account takeover reaches all of them,
  plus any linked services and stored payment methods.
- Every account that used the same password, and the email account used for recovery.
- Other devices on the same network segment: unauthenticated local APIs (Shelly, Tasmota, some ESPHome
  builds) on the segment may also have been controlled.
- The MQTT broker and Home Assistant instance if devices report to them; a compromised device holding MQTT
  credentials can publish to topics that drive automations.
- Radio networks: if a hub or coordinator was compromised, or its backup was exposed, treat the Zigbee,
  Z-Wave, or Thread keys it holds as exposed.
- Wi-Fi credentials stored on compromised DIY devices (they are compiled into ESPHome images and stored
  in Tasmota and Shelly configurations): treat the Wi-Fi password as exposed.
- Physical-security implications: if a lock or garage was opened, the incident may include a physical
  intrusion; the user may want to involve the police and their insurer.

## Eradication and recovery

- **Accounts:** after containment, confirm MFA is on, only expected users, codes, linked services, and
  fabrics remain, and recovery details are the user's own. Rotate passwords for every account that shared
  the password.
- **Lock codes and keys:** delete and re-issue all keypad codes, e-keys, and guest codes for locks that
  were affected, and re-key or replace mechanical cylinders if physical keys may have been copied.
- **Devices:** for a device suspected of being compromised, the user factory resets it, updates firmware
  from the vendor's official source, and re-adds it to the account and controllers. For DIY firmware, the
  user rebuilds from a known-good configuration with **new** API encryption keys, OTA settings, web
  passwords, and MQTT credentials, flashing over USB if the device's integrity is in doubt.
- **Radio networks:** if keys were exposed, the user plans a rebuild with new keys (new Zigbee network
  key, re-inclusion of Z-Wave devices, new Thread network), re-pairing every device. This is a planned
  project, not an emergency step, unless high-impact devices are affected.
- **Network:** rotate the Wi-Fi password if any device that stored it was compromised (every device on
  that SSID must be updated); move devices to an IoT segment with egress limits; disable UPnP or remove
  unknown mappings.
- **End-of-support devices** that were compromised should be replaced, not restored.
- Before trusting a high-impact device again, the user confirms in person that it locks, unlocks, opens,
  closes, arms, and disarms only when expected, and that the manual fallback works.

## Quick checklist tailored for smart home devices

Start with the core quick checklist, plus:

- [ ] Secure the physical space first: physical key or deadbolt, garage opener lock-out or unplug and
      lock manually, alarm monitoring company informed.
- [ ] Screenshot lock, garage, alarm, and account activity histories, shared users, linked services, and
      Matter fabrics before changing anything.
- [ ] From a trusted device: change the vendor account password, enable MFA, sign out all sessions,
      check recovery details, remove unknown users, codes, linked services, and fabrics.
- [ ] Block a suspected compromised device at the firewall instead of resetting it; keep evidence.
- [ ] Check the MQTT broker, Home Assistant, and other devices on the same segment.
- [ ] Rotate the Wi-Fi password if a DIY device holding it was compromised.
- [ ] Consider safety support, police, and insurer involvement if a person may have entered the home.
