---
name: video-doorbells
description: >-
  Security and privacy assessment, hardening, remediation, and incident response for cloud-first consumer
  video doorbells, cameras, and alarm-and-camera kits (Ring, Google Nest, Arlo, Eufy, Wyze, SimpliSafe and
  similar). Use when reviewing who can see a household's cameras, the vendor account's sign-in security,
  shared users and logged-in devices, end-to-end encryption and local-storage options, police and
  neighborhood sharing settings, third-party integrations and local stream bridges, network placement, or
  physical tamper and theft, or when a doorbell or camera account may have been taken over.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Cloud-managed consumer doorbells, cameras, and alarm kits and their vendor apps (verify the live app version; menus and features change often)"
  audience: "home, work"
  finding_prefix: "DBL"
  modes: "discover, recommend, remediate, respond"
---

# Video Doorbell and Cloud Camera Security

Act as a careful, privacy-minded security advisor for a household's or small office's cloud cameras.
These systems record the front door, the driveway, and often the inside of the home, and the recordings
live in the vendor's cloud behind an ordinary consumer account. The main risks are someone else getting
into that account, people who should no longer have access keeping it, footage leaving the account through
sharing features and integrations, and the device itself being stolen or tampered with. Identify, explain,
prioritize, remediate (only when authorized), and verify those weaknesses, and treat what the cameras see
as sensitive personal data throughout.

## How to use this skill

This skill holds only doorbell- and cloud-camera-specific guidance. It builds on the shared core, which
always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Doorbell- and camera-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation, regulator findings, and advisories are in [references.md](references.md).

## Doorbell- and cloud-camera-specific principles

- **The account is the system.** For cloud-first products there is usually no local admin interface to
  audit. Live view, recordings, settings, sharing, and firmware are all controlled through the vendor
  account and app. Almost every check in this skill is something the **user** does in the app or on the
  vendor's website and reports back (screenshots are fine; redact names, addresses, and faces). Say so
  plainly at the start, and mark anything the user can't or won't check **Not assessed**.
- **The agent never signs in to the user's account.** Don't ask for the password, a verification code, a
  passkey, or the end-to-end encryption passphrase, and don't use account tokens taken from an integration.
  Signing in as the user would also add the agent's session to the account's device list and may alert or
  lock the owner out.
- **The email account behind the camera account is part of the attack surface.** Password resets go to
  it. A camera account with strong two-step verification can still be taken over through a weak email
  account or a ported phone number.
- **Firmware is vendor-controlled.** Updates are pushed by the vendor's cloud, usually automatically, and
  most products give the user no way to choose, delay, or roll back a version. The user's job is to keep
  devices online and supported and to replace models the vendor no longer updates. Never recommend
  unofficial or custom firmware as security remediation.
- **Marketing claims about "local" or "encrypted" are not evidence.** Regulators and researchers have
  found that some camera vendors' security and encryption claims were inaccurate (see the history in
  [references.md](references.md)). Record what the vendor currently documents, label it
  **vendor-documented**, and don't present it as observed.
- **Cameras record other people.** Neighbors, passers-by, visitors, and household members have privacy
  interests and, in some places, legal rights (audio recording and camera-placement laws vary). Raise this
  where it matters; don't give legal advice.
- **Household safety comes first.** Shared access and camera history can be used to track or control a
  partner or family member. If the user indicates that someone in or formerly in the household may be
  abusive, removing that person's access can alert them. Pause, point the user to a domestic-violence
  advocate or hotline for safety planning, and let them decide the timing (see
  [incident-response.md](incident-response.md)).

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Cloud-only doorbell or camera** (typical Ring, Nest, Wyze cloud recording) | Recordings appear only in the app or vendor website; no storage card or hub. | All history is in the vendor cloud. Recording usually needs a paid plan; without one the device may offer only live view and alerts. |
| **Hub or base station with local storage** (Arlo SmartHub or base station with USB or card storage, Eufy HomeBase, some Wyze and Eufy cards in the camera) | A hub on the network, or a storage card slot; the app shows a local storage option. | Recordings may stay on the hub or card, but the app, notifications, and remote viewing still go through the vendor's cloud. Theft of the hub or card is theft of the footage. Check what is still uploaded (thumbnails, previews, event clips). |
| **Alarm kit with cameras** (SimpliSafe-style base station, keypad, sensors, cameras, optional professional monitoring) | Base station and keypad; arm/disarm modes; a monitoring plan. | Adds PINs, alarm modes, and monitoring staff who may view camera footage during an alarm. Camera behavior is often tied to the alarm mode, and some cameras record briefly on disarm by design. |
| **Ecosystem-integrated** (cameras shown on smart displays, TVs, or in a voice assistant's app) | Cameras appear in a voice-assistant or smart-display app; account-linking entries in the camera app. | Every linked platform and every person signed in to it can view the cameras. Count those accounts as camera users. |
| **Bridged to a local system** (community integrations or bridges that pull streams into Home Assistant, Scrypted, an NVR, or an MQTT broker) | An integration in a home-automation system; a container or add-on whose name includes the camera brand. | The bridge stores a long-lived account token or refresh token. Anyone who controls that host controls the camera account. Assess the host too. |
| **Business or shared premises** (office door, rental property, shared building entrance) | Several admins; staff or tenants as shared users. | More shared users, staff turnover, and workplace or tenant privacy rules. Access reviews need an owner and a schedule. |

## Detection

Hints for recognizing this product class during a network inventory (used by the `full-assessment` skill).
These devices mostly make outbound connections to their vendor and expose little or nothing locally, so
network evidence is often thin. Confirm with the user before relying on a match.

- A MAC address vendor (OUI) registered to the camera brand (for example Ring, Google, Arlo, Wyze, or
  Anker/Eufy), or to the Wi-Fi module maker inside the device (commonly Espressif, Realtek, or similar),
  in which case the OUI alone doesn't identify the product.
- A DHCP hostname or client identifier that includes the brand or product family.
- Steady outbound TLS connections and DNS queries to the vendor's cloud domains, with **no** listening
  services on the device. A scan that finds no open ports on a doorbell is normal, not a pass or a failure.
- Hubs and base stations (Arlo, Eufy HomeBase, alarm base stations) are usually wired or on 2.4 GHz Wi-Fi
  and may answer local discovery (mDNS or SSDP) or keep a few local ports open for the app's local
  streaming. Port numbers vary by vendor and firmware; treat any open port as something to identify, not
  something to connect to.
- Local stream bridges on another host (a container or add-on named after the camera brand) and RTSP
  (TCP 554, the protocol default) on a camera where the vendor offers optional RTSP firmware or a setting.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Most checks are **user-run in the vendor app or website**; the agent guides the user through
them, describing each setting by what it does, and asks the user to confirm the exact menu on their app
version. Mark anything you can't inspect **Not assessed**.

### Access and baseline

Ask the user for:

- The brand(s), every device in the account (doorbells, cameras, hubs, chimes, alarm parts), and whether
  there is more than one account or "location" in the app.
- The app version and phone OS, and whether they're the account **owner** or a shared user. Many checks
  are visible only to the owner.
- Screenshots of the account's security page, the shared-users list, the logged-in or authorized devices
  list, and the linked-services or integrations list, with personal details redacted.

Candidate read-only network checks, **not yet verified** against every product and firmware. Run them only
with the user's authorization, from a host the user controls, and only against the user's own devices:

```sh
# Port-state check of one camera or hub address (TCP connect scan, no service interaction):
nmap -sT -Pn --top-ports 100 192.0.2.40
# Local discovery announcements (read-only listening on the local segment):
dns-sd -B _services._dns-sd._udp local.     # macOS; on Linux: avahi-browse -art
```

- Router or firewall views are often better evidence than scanning: the DHCP lease (hostname, MAC vendor),
  which network or VLAN the device is on, and its outbound connections or DNS queries.
- **Never** do any of the following:
  - sign in to the user's camera account, or use a token taken from a bridge or integration to call the
    vendor's API;
  - test default or guessed credentials, or try to log in to RTSP streams, hubs, or local ports;
  - run exploit or proof-of-concept scripts against a camera, hub, or the vendor's cloud;
  - press the doorbell, trigger the siren or alarm, change the alarm mode, or talk through two-way audio;
  - factory reset, unpair, or re-register any device, or remove its storage card;
  - download, copy, or view recordings beyond what the user shows you for the assessment.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, support status, and firmware

- Every device in the account, with model and generation. Look for models the vendor has declared
  end-of-life or no longer updates; a camera that no longer gets security fixes but still connects to the
  cloud is an end-of-life finding (core triage). Vendors have stopped updating older models that later had
  known, unfixed flaws (for example, Wyze said its first-generation camera could not support a needed
  security update; see [references.md](references.md)).
- Firmware version per device as the app shows it, and whether the app reports updates as current.
  Remember the user can't normally choose a version, so the question is whether the device is online,
  supported, and receiving updates.
- Devices that have been offline for a long time (they miss updates and still hold the Wi-Fi password).
- Old devices still registered to the account that are no longer installed, or devices that were given
  away or sold without being removed.
- Check the vendor's security or advisory page for current issues affecting the models in use, and
  validate any hit per core triage. Don't rely on memory or old lists.

#### B. Account sign-in security

- Two-step verification (2SV/MFA): enabled for the owner and, where the vendor allows, required for shared
  users. Some vendors now make it mandatory (Ring's documentation describes it as mandatory; Wyze announced
  it as required). Record the method: authenticator app or passkey is stronger than SMS; email codes are
  only as strong as the email account.
- Passkeys or federated sign-in (signing in with a Google, Apple, or Amazon account): if used, the
  security of that identity account is the security of the cameras. Check its 2SV and recovery options too.
- Password: unique to this account (never reused; credential stuffing against reused passwords is the
  documented route by which tens of thousands of Ring accounts were accessed, per the FTC). Ask whether the
  user's email address appears in known breaches, without asking for the password.
- Account recovery: the recovery email and phone number on file are current and controlled by the owner;
  the recovery email account itself has strong 2SV; the mobile carrier account has a port-out PIN or
  similar protection if SMS codes are used.
- Login or new-device alerts: enabled, and sent somewhere the owner reads.
- Account owner continuity: is the owner a single person whose departure would orphan the system? Is
  there a documented way to transfer ownership (some vendors require the vendor's support to do it)?

#### C. Shared users, household members, and signed-in devices

- The full list of **shared users** or household members and what each can do (live view, history,
  settings, arming, sharing). Flag former partners, former household members, house-sitters, contractors,
  previous owners or tenants, and anyone the owner doesn't recognize.
- Shared users with admin-level rights who don't need them.
- The **authorized or logged-in devices** list (Ring calls it authorized client devices; other vendors
  list active sessions or "where you're signed in"): unknown phones, tablets, browsers, or devices not seen
  in months. Ask the user to compare against devices they actually own.
- Smart displays, TVs, and voice-assistant accounts that can show the cameras (domain F), and who is
  signed in to them.
- For business or rental use: whether there is a joiner/leaver process for shared users.
- Any unexplained entry (an unknown signed-in device, an unknown shared user, settings changed nobody
  made) is a **P0 indicator**: switch to Respond.

#### D. Encryption, storage location, and retention

- **End-to-end encryption (E2EE):** whether the vendor offers it for these models, whether it is enabled,
  and what the user gives up. Ring's support documentation lists many features that are unavailable with
  its video E2EE enabled, including shared-user access to videos, sharing links, viewing on the website,
  viewing on smart displays, TVs, and third-party devices, and several detection and AI features, and it
  limits the number of enrolled phones. (At last review that page described its original E2EE as retired
  in favor of a newer version, so the list may change.) Other vendors' options differ; verify on the
  vendor's current page.
- E2EE recovery material: whether the passphrase or account key is stored somewhere safe outside the
  phone. Ring states that without the passphrase, encrypted videos can't be accessed. Losing it means
  losing the footage.
- What the vendor says about encryption when E2EE is off (typically encryption in transit and at rest,
  with the vendor holding the keys). Label it vendor-documented; note that Eufy's distributors settled
  with the New York Attorney General after an investigation found streams were not always encrypted and
  could be reached via a link without authentication (2025; see references).
- **Local storage claims:** for hubs and card storage, what is still uploaded to the cloud (thumbnails,
  event previews, notifications with images, AI processing). "Local" in marketing often means "also
  local." Ask the user to read the vendor's current description.
- Cloud retention period (set by the plan or by the user) and whether it is longer than needed.
- Downloaded clips and shared links: old public or "anyone with the link" shares still active; clips
  downloaded to shared computers or synced photo libraries.
- Notifications with image previews on lock screens (anyone holding the phone sees the snapshot).

#### E. Privacy, neighborhood, and law-enforcement sharing

- **Law-enforcement request features:** for example, Ring's Community Requests in its Neighbors feed,
  through which verified local public-safety agencies can ask users for footage. Whether the user has
  opted out, and whether they understand that responding is voluntary under those programs but that a
  vendor may still disclose data in response to legal process or, under its own policy, in emergencies.
  Check the vendor's current law-enforcement guidelines and transparency report; these programs and
  partnerships have changed several times (references).
- **Neighborhood and community features:** posts the user has shared publicly, location precision shown
  on those posts, and features that use the camera network to search for things on others' behalf (for
  example Ring's Search Party for lost pets, reported as on by default for eligible outdoor cameras when
  launched). Note the default and the user's choice.
- **Face recognition and AI features** (for example "familiar faces" style features, AI video
  descriptions): enabled or not, where processing happens per the vendor, and whether it is allowed where
  the user lives. Some jurisdictions restrict biometric collection; the vendor may disable features by
  region. Faces of visitors and passers-by are other people's biometric data.
- **Privacy zones and motion zones:** neighbors' windows, gardens, and the public street masked where
  possible; indoor cameras not pointed at bathrooms or bedrooms.
- **Audio recording:** on or off per camera; whether it is needed. Audio recording laws can be stricter
  than video laws.
- **Indoor camera privacy modes:** physical shutters or "privacy mode" schedules, and whether the camera
  follows the alarm or home/away mode. On some alarm-kit cameras, the vendor documents that the shutter
  opens and the camera records briefly when the system is disarmed; make sure the household knows.
- Vendor data-sharing and marketing settings in the account's privacy section; requests for a copy of the
  data the vendor holds, where the law provides one.

#### F. Integrations, account linking, and local bridges

- **Linked services** listed in the camera account: voice assistants, smart-display platforms, automation
  services (IFTTT-style), alarm monitoring partners, insurance or "verified alarm" partners. Each one can
  see events or video. Unused links are findings.
- **Local bridges and integrations** that extract streams or events (community Home Assistant
  integrations, Scrypted plugins, MQTT bridges, NVR bridges, "docker bridge" projects): they hold the
  account's refresh token or credentials, often in a plain file or the home-automation configuration.
  Check: which account they use (ideally a dedicated shared user with the least rights, not the owner);
  where the token is stored and who can read it; whether the bridge's own web UI or re-streamed RTSP or
  WebRTC output is reachable from untrusted networks; whether the project is maintained; and whether its
  backups contain the token. Apply core: tool-use contract, third-party integrations.
- **Vendor RTSP or local streaming options** (some brands offer optional RTSP firmware or settings):
  enabled or not, password set, and which networks can reach port 554.
- Third-party apps on the phone that ask for the camera account's credentials (unofficial viewers): these
  receive the password and are a finding unless the user deliberately accepts them.

#### G. Network placement and Wi-Fi

- Which network the devices are on: ideally an IoT segment or VLAN that can reach the internet but not
  the household's computers, NAS, or admin interfaces. Check the firewall rules that apply (core and the
  firewall skill for the user's router).
- Inbound exposure: cloud cameras shouldn't need any port forwards. Check the router for port forwards
  and UPnP mappings created by camera devices or hubs, and that UPnP isn't letting them open inbound
  paths.
- Egress: the devices need the vendor cloud. Blocking all internet breaks them; blocking only specific
  services (for example, direct outbound DNS to bypass local filtering) may be fine. Note the trade-off.
- Wi-Fi security on the segment they use (WPA2-AES or WPA3; doorbells often support only 2.4 GHz and
  sometimes only WPA2). A shared IoT Wi-Fi password is stored on every device on it (domain H).
- Hubs and base stations: wired where possible; not on a guest network that visitors also use.
- Bridge hosts (domain F): if a bridge re-streams cameras, it is a camera system in its own right; check
  what segments can reach it.

#### H. Physical security, tamper, and theft

- Mounting: doorbells and outdoor cameras within reach are commonly stolen or knocked off. Check for the
  vendor's security screws or theft-resistant mounts, and whether the vendor offers theft replacement.
- Storage cards in cameras and USB drives on hubs: removable footage. Could a thief take the recording
  of their own visit?
- Tamper and offline alerts: enabled, so the owner learns when a camera goes offline or is moved.
- Setup buttons and pairing modes reachable from outside: on some devices pressing a button starts setup
  or Wi-Fi pairing. Ask what the vendor documents about re-pairing a device that is already registered
  (usually it requires the owner's account to remove it first).
- A stolen device holds the Wi-Fi password of the network it was on. Plan to rotate it (Remediate).
- Battery doorbells: theft or a dead battery stops recording silently unless alerts are on.
- Alarm kits: keypad and base-station placement, a duress PIN if the vendor supports one, and backup
  power and connectivity (cellular backup) for the base station.

#### I. Subscription, service dependency, and vendor lifecycle

- Which features depend on a paid plan: recording, history length, person detection, E2EE eligibility,
  professional monitoring, theft protection. What happens if the plan lapses (recordings stop, history
  is deleted after a period, cameras drop to live view only); ask the user to read the vendor's current
  terms.
- Whether recordings the user may need (for an insurance claim or a police report) would be lost at
  lapse or at the end of the retention period.
- Vendor service dependency: if the vendor's cloud or the user's internet is down, what still works
  (local recording, alarm sirens, cellular backup). Vendor outages and cloud bugs have exposed or
  disabled camera feeds before; Wyze, for example, disclosed in 2024 that about 13,000 users were shown
  thumbnails from other customers' cameras after an outage (references).
- Vendor end-of-life announcements for models or for the whole service, and whether the household has a
  replacement plan.

#### J. Alarm-kit specifics (if applicable)

- Master and user PINs: unique, not shared with former household members or contractors, not the
  default or an obvious sequence. (Ask whether they were changed from setup; never test them.)
- Who the monitoring service may contact and dispatch; whether monitoring staff can view indoor cameras
  during an alarm, and the user understands that.
- Arming schedules and geofencing (location-based arming): which phones' locations control arming.
- Entry/exit delay and alarm-mode-to-camera behavior (domain E).
- Sensor and keypad battery and tamper alerts.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**. Most changes are
made by the user in the vendor app; write each as clear steps described by function, and tell the user to
confirm the exact menu on their app version.

### Dependency and blast-radius check (required)

- **People:** every shared user and household member who relies on alerts, live view, or arming. Removing
  or downgrading someone stops their access immediately, and some vendors notify them.
- **Devices:** every phone, tablet, smart display, TV, and voice assistant that shows the cameras.
  Enabling E2EE or signing out all devices affects all of them.
- **Integrations:** automations, bridges, NVRs, and dashboards that use the account; revoking tokens or
  changing the password may break them until re-linked.
- **Monitoring:** professional monitoring and verified-alarm services that depend on camera access.
- **Evidence:** any recordings needed for an insurance claim, police report, or dispute; export them
  before changing retention, plans, or encryption.
- **Network:** moving devices to another Wi-Fi network or VLAN requires re-joining each device, sometimes
  physically, and may break local streaming and casting.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No or weak 2SV | Enable 2SV with an authenticator app or passkey; avoid SMS-only where alternatives exist. | Every shared user may need to re-verify; keep backup codes offline. |
| Weak recovery path | Secure the recovery email with 2SV; update recovery phone; add a carrier port-out PIN. | None for normal use. |
| Reused password | Set a unique password from a password manager, then sign out all other sessions. | All devices and some integrations must sign in again. |
| Stale or unknown shared users | Remove them; downgrade others to the least role they need. | They lose access at once; consider safety first if the person may be abusive. |
| Unknown or stale signed-in devices | Remove them; if any is unrecognized, treat as an incident first (Respond). | Removed devices must sign in again with 2SV. |
| E2EE available but off | Explain the trade-off; enable only if the user accepts the lost features, after saving the passphrase. | Listed features (sharing, web viewing, smart displays, some AI and detection) stop working; lost passphrase means lost footage. |
| Long cloud retention | Shorten to what the household needs. | Older recordings are deleted (export anything needed first). |
| Law-enforcement and neighborhood features | Opt out, or keep with informed consent. | User no longer sees agency requests in the feed. |
| Face recognition or AI features | Disable unless deliberately wanted and lawful where the user lives. | Fewer smart alerts. |
| Cameras capture neighbors or indoor private spaces | Add privacy zones; re-aim; turn off audio where not needed. | Less coverage. |
| Unused linked services | Unlink them in the camera account and in the other platform. | Those displays or automations stop showing cameras. |
| Bridge uses the owner account | Create a dedicated least-privilege shared user for the bridge; protect the host and its backups. | Re-link the bridge; some features may need owner rights. |
| Bridge or RTSP reachable from untrusted networks | Restrict with firewall rules; disable RTSP if unused. | Remote viewers using that path stop working. |
| Cameras on the main LAN | Move to an IoT segment with internet access and no access to internal systems. | Re-join each device; local streaming between segments may need extra rules. |
| Port forwards or UPnP mappings for cameras | Remove; disable UPnP or restrict it. | None for cloud viewing. |
| End-of-life model | Replace; meanwhile isolate it and limit what it can see. | Cost; possible plan changes. |
| Theft and tamper exposure | Security screws or anti-theft mount; tamper/offline alerts; protect hubs and cards. | Minor install work. |
| Plan lapse would lose needed recordings | Export important clips; set a renewal reminder; document what stops on lapse. | Ongoing cost if the plan is kept. |
| Alarm PINs shared or unchanged | Change master and user PINs; give each person their own; add a duress PIN if offered. | Everyone must learn new PINs. |

Hiding the camera, renaming devices, and changing Wi-Fi network names are supplementary only. Never
recommend them as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (account sign-in and unknown access) →
high-priority hardening (sharing, integrations, network placement) → routine maintenance (retention,
alerts, support status) → optional privacy improvements. Then ask for approval (core: modes and
authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. The user usually makes the change in
the app while the agent guides and then verifies from the user's screenshot or description. Doorbell and
cloud-camera specifics:

- **Before any account change:** confirm the user can still sign in to the recovery email, has the
  current 2SV method and backup codes, and (if E2EE is on) has the passphrase. Export any recordings that
  may be needed before changing plans, retention, or encryption.
- **Use a known-clean phone or computer** for password, 2SV, and recovery changes.
- **Order for account hardening:** secure the recovery email first; then set a unique camera-account
  password; then enable or strengthen 2SV; then remove unknown devices and shared users; then sign out all
  other sessions. Classify sign-out-everywhere and password changes as **C2** (they log out every viewer
  and may break integrations).
- **Removing a person's access is C2.** Do it one person at a time, after the safety question in the
  principles, and confirm the remaining users still work.
- **Enabling E2EE is C2**, and losing the passphrase makes footage unrecoverable. Confirm the passphrase
  is saved outside the phone before enabling, and that the user accepts the listed lost features.
- **Shortening retention is C3** for the recordings it deletes. Export first and get explicit approval.
- **Integration changes:** re-link bridges with a dedicated least-privilege user, then revoke the old
  token or session, then check the bridge host's configuration and backups no longer hold the old token.
- **Network moves:** move one device at a time to the new segment and confirm it reconnects, records,
  and alerts before moving the next. Battery doorbells may need to be taken down to re-pair.
- **Firmware:** there is usually nothing to approve; if the app offers a pending update, applying it is C2
  (the device restarts and stops recording briefly).

After each change, follow the core "after a change" steps: have the user re-check the setting, test a live
view and a motion event, confirm alerts arrive on the intended phones, confirm integrations still work
(or are intentionally removed), and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Factory resetting, unpairing, or removing a device from the account as security remediation (it can
  destroy evidence and local recordings and may need physical access to re-add).
- Deleting recordings, event history, or the account, or shortening retention, while an incident or
  dispute may need the footage.
- Flashing unofficial or custom firmware, or rooting a camera or hub.
- Transferring account ownership, or removing the last admin, without the vendor's documented process.
- Disabling professional alarm monitoring or changing dispatch contacts on the user's behalf.
- Any action against another person's camera or account (for example a neighbor's), or helping access
  footage the user isn't entitled to.

---

## Respond

On any P0 indicator (an unknown signed-in device, unknown shared user, settings changes nobody made,
voices or siren activations through a camera, deleted recordings, or a login alert the user didn't cause),
switch to Respond immediately. Follow the core playbook plus the doorbell-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### DBL-001: Former house-sitter still has shared-user access with live view and history

**Confidence:** Confirmed
**Priority:** P2. A person outside the household can watch the front door and indoor cameras live and
review history, revealing when the home is empty. No sign of misuse, so not P0.
**State:** Open
**Component:** Vendor camera account, shared-users list; app version as shown in the user's screenshot
**Evidence:** User-provided screenshot, 2026-02-03: the shared-users list shows three people; the user
identifies one as a house-sitter from a trip months earlier. Their role includes live view and event
history for all cameras, including two indoor cameras. The authorized-devices list shows no devices the
user doesn't recognize (user-reported).
**Expected secure state:** only current household members and deliberately chosen guests have access,
with the least role they need (vendor shared-user documentation).
**Exposure and prerequisites:** the house-sitter's own account and phone; if their account is compromised,
so is this household's camera view.
**Dependencies / blast radius:** none; the house-sitter no longer needs access. The user confirms there is
no safety concern with removing them.
**Recommended remediation:** remove the house-sitter as a shared user. Review the remaining shared users'
roles, and set a reminder to review shared users after each trip.
**Operation class:** C2 (removes a person's access immediately; the vendor may notify them).
**Approval required:** Yes.
**Verification:** the shared-users list no longer shows the house-sitter; the remaining users' live view
still works.
**Rollback:** re-invite the person (not recommended).

---

## Version history

- **1.0** (2026-10-30): Initial version.
