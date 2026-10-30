---
name: smart-tvs
description: >-
  Security and privacy assessment, hardening, remediation, and incident response for smart TVs and
  streaming devices (Samsung Tizen, LG webOS, Google TV and Android TV, Roku, Amazon Fire TV, Apple TV, and
  generic Android TV boxes). Use when reviewing a TV's update and support status, viewing-data tracking
  (ACR) and advertising settings, microphones and cameras, developer mode, sideloading and ADB debugging,
  installed apps, signed-in accounts, network placement, or casting and remote-control exposure, or when a
  TV or streaming box may have been compromised or recruited into a botnet.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-30"
  applies_to: "Current and recent smart TV and streaming-device platforms (verify the live OS version; menus change between releases and brands)"
  audience: "home, work"
  finding_prefix: "TV"
  modes: "discover, recommend, remediate, respond"
---

# Smart TV and Streaming Device Security

Act as a careful, privacy-minded security advisor for the televisions and streaming devices in a home or
small office. These devices sit on the network for years, run third-party apps, carry signed-in accounts
with stored payment methods, often have microphones (and sometimes cameras), and report viewing habits to
their makers unless told not to. They are rarely updated on purpose and often outlive their vendor's
support. Identify, explain, prioritize, remediate (only when authorized), and verify weaknesses in the
devices, the accounts on them, and the network paths around them.

## How to use this skill

This skill holds only smart-TV- and streaming-device-specific guidance. It builds on the shared core, which
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

Smart-TV-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation,
regulator findings, and advisories are in [references.md](references.md).

## Smart-TV-specific principles

- **Most checks happen on the screen, by the user.** TVs have no admin console for the agent to read. The
  agent guides the user through the settings menus with the remote and asks for photos or screenshots of
  each screen. Describe settings by **what they do** ("the setting that lets the TV recognize what's on
  screen"), give the brand's usual name as a hint, and ask the user to confirm the exact path; menu names
  change with every OS release and differ between TV makers using the same platform.
- **The TV listens to the LAN.** Casting, remote-control apps, and discovery protocols (DIAL, SSDP, mDNS,
  vendor control APIs) mean other devices on the same network can often launch apps, send keypresses, or
  query the TV, sometimes without authentication. That is a feature; the security question is **which
  networks** can reach it.
- **The agent never controls the TV.** Sending a remote-control command, launching an app, casting,
  pairing a control app, or connecting to a debugging interface changes the device and may put a pairing
  prompt or content on someone's screen. All of those are out of bounds in Discover, and none are needed.
- **Privacy settings drift.** OS updates, new terms acceptance, and factory resets can re-enable
  viewing-data collection and ad tracking. Re-check after major updates. Turning off content recognition
  limits but doesn't stop data collection; the platform still learns which apps are used.
- **Support ends long before the hardware fails.** TV makers publish support commitments of varying
  length, and many older sets get no updates. An unsupported TV that stays online running a
  browser and third-party apps is an end-of-life finding (core triage). A common mitigation is to take
  it off the network and use a supported external streaming device.
- **Uncertified and "unlocked" Android boxes are a different risk class.** The FBI has warned that cheap,
  uncertified Android TV boxes can arrive with malware preinstalled and be used as residential proxies in
  the BADBOX 2.0 botnet (references). Factory reset doesn't fix firmware-level malware. Treat such
  devices as untrusted.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Samsung TV (Tizen)** | Samsung brand; Smart Hub home screen; Samsung account. | Viewing-information and interest-based-ad settings are separate; voice assistants (Bixby, Alexa, others) may be built in. Has a developer mode for app testing. |
| **LG TV (webOS)** | LG brand; webOS launcher; LG account. | Content recognition is tied to a "Live Plus"-style feature and the viewing-information agreements. LG publishes a multi-year webOS upgrade program for recent models. A Developer Mode app exists for app testing. |
| **Google TV / Android TV** (TVs from several makers, Google's own streamer, operator boxes) | Google TV or Android TV home screen; Google account; Google Play. | Android developer options, USB/ADB debugging, and network debugging; sideloading from unknown sources per app; Google Play Protect. The TV maker controls updates, not Google. |
| **Roku** (Roku TVs and Roku players) | Roku home screen; Roku account. | External Control Protocol (ECP) on TCP 8060 lets LAN apps control and query the device; the network-access setting controls it. Roku TVs have a content-recognition setting for TV inputs. Developer mode exists. |
| **Amazon Fire TV** (sticks, cubes, Fire TV-branded TVs) | Fire TV home screen; Amazon account. | Android-based: ADB debugging and "apps from unknown sources" under developer options (sometimes hidden). The Amazon account often has one-click purchasing; Alexa built in. |
| **Apple TV** (tvOS) | Apple TV box; Apple Account. | Fewer exposures: no sideloading outside developer pairing; AirPlay access settings control who can cast. Long OS support for many models. |
| **Uncertified Android TV box** (generic, "unlocked", "free channels") | Unknown brand; no Google TV branding; often ships with unofficial app stores; Play Protect missing or disabled. | Treat as untrusted (see principles). Replacement is usually the fix. |
| **Shared or business display** (meeting room, lobby, rental) | Several users cast to it; signage or hotel mode. | Casting from guest networks, signed-in personal accounts left on the TV, and screen content visible to visitors. |

## Detection

Hints for recognizing these devices during a network inventory (used by the `full-assessment` skill).
Ports listed are protocol or vendor defaults; firmware can change them. Confirm with the user before
relying on a match, and **never** interact with these services beyond observing that they exist.

- **SSDP/UPnP and DIAL** (UDP 1900 multicast): most smart TVs and streaming devices announce themselves,
  often naming the brand and model. DIAL is the second-screen protocol many TVs use for "cast from app."
- **Roku:** SSDP announcements for its External Control Protocol and an HTTP service on **TCP 8060**
  (Roku-documented).
- **Google Cast** (Google TV, Android TV, Chromecast, "Chromecast built-in" TVs): mDNS service
  `_googlecast._tcp` (UDP 5353), with TCP 8008 and 8009 commonly reported for the Cast service.
- **AirPlay** (Apple TV, and many Samsung, LG, Roku, and other TVs that support AirPlay): mDNS services
  such as `_airplay._tcp` and `_raop._tcp`; Apple lists TCP 7000 among AirPlay ports.
- **Android ADB over the network:** **TCP 5555** open on an Android TV, Google TV, or Fire TV device
  usually means ADB debugging or network debugging is enabled. That is a finding in itself.
- **Vendor remote-control APIs:** Samsung and LG TVs commonly expose WebSocket control services for their
  phone apps (for example TCP 8001/8002 on Samsung and 3000/3001 on LG, as commonly reported; not
  vendor-verified here).
- **MAC address vendors (OUI)** of the TV maker or streaming-device maker (Samsung, LG, Roku, Amazon,
  Google, Apple, Sony, TCL, Hisense, and others), or of a Wi-Fi module maker on budget devices. Hostnames
  often include the brand or model.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Most checks are **user-run in the TV's settings** or in the companion account on the web;
the agent guides and records. Mark anything you can't inspect **Not assessed**.

### Access and baseline

Ask the user for, per device:

- Brand, model (from the TV's "about" or support screen), platform and OS version, and when it was bought.
- Which network it uses (wired or which Wi-Fi network), and which accounts are signed in.
- Photos or screenshots of: the software-update screen, privacy and terms screens, developer options (if
  visible), the installed-apps list, and account or profile screens. Redact serial numbers, account names,
  and email addresses.

Candidate read-only network checks, **not yet verified** against every model. Run them only with the
user's authorization, from a host the user controls, and only against the user's own devices:

```sh
# Port-state check only (TCP connect; no protocol interaction). Never complete an ADB handshake.
nmap -sT -Pn -p 5555,7000,8001,8002,8008,8009,8060,3000,3001 192.0.2.60
# Passive discovery listening on the local segment:
dns-sd -B _googlecast._tcp local.        # macOS; on Linux: avahi-browse -rt _googlecast._tcp
dns-sd -B _airplay._tcp local.
# Roku only, read-only device query (vendor-documented ECP query endpoint). May be refused if network
# control is restricted. Output includes serial and device IDs: redact before sharing.
curl -s http://192.0.2.61:8060/query/device-info
```

- Router or firewall views are often better evidence than scanning: DHCP leases, which VLAN the device
  is on, UPnP port mappings it created, and its outbound connections and DNS queries.
- **Never** do any of the following:
  - connect to ADB (`adb connect`, `adb shell`, or any ADB client), even if port 5555 is open;
  - send ECP `keypress`, `launch`, or `input` commands, DIAL launches, casts, AirPlay streams, or any
    vendor remote-control API command; pair a control app with the TV;
  - enable developer mode, unknown sources, or debugging to "check" them;
  - install, uninstall, or update apps, sign in or out of accounts, or accept terms on the user's behalf;
  - factory reset the device;
  - test default or guessed credentials or PINs, or run exploit or proof-of-concept scripts.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, updates, and support lifetime

- OS or firmware version and the date of the last update, from the TV's software-update screen.
- Automatic updates: enabled? Some TVs only update when on standby and connected; a TV that is always
  unplugged or offline at night may never update.
- Support status: does the maker still ship updates for this model? Check the maker's published support
  policy (for example, Samsung announced seven years of Tizen OS updates for recent models, and LG's webOS
  upgrade program covers recent models for a set period; verify scope and model years on the vendor's
  current pages). Streaming platforms (Roku, Fire TV, Google TV devices, Apple TV) also drop old models;
  check the vendor's supported-device list.
- An end-of-support TV still connected to the network and running apps or a browser is a finding;
  mitigation is usually to disconnect it from the network and use a supported external streamer.
- Check the vendor's security advisories for the model or platform, and validate any hit per core triage.
  Don't rely on memory or old lists.

#### B. Accounts, purchases, and profiles

- Which accounts are signed in on the device: platform account (Google, Amazon, Apple, Samsung, LG, Roku),
  and each streaming app's account.
- Stored payment methods and purchase protection: a purchase PIN or password for app and content
  purchases (especially Amazon one-click and Google Play purchases on a shared living-room device).
- Platform account security: 2SV on the Google, Amazon, Apple, Roku, Samsung, or LG account; the account
  being a personal one with email, documents, and photos (a TV signed in to a primary Google account can
  expose more than viewing).
- In the platform account on the web: the list of devices signed in; old TVs and devices that were sold
  or discarded still listed.
- Streaming services: their "devices signed in" lists; sign-in codes left on shared displays.
- Child profiles and parental controls, if children use the device.
- Shared or business displays: personal accounts left signed in.

#### C. Viewing data, content recognition, and advertising

- **Automatic content recognition (ACR):** the setting that lets the TV identify what's on screen,
  including from cable boxes, consoles, and other inputs. Usual names: Samsung "Viewing Information
  Services"; LG "Live Plus" plus viewing-information agreements; Roku TVs "Smart TV Experience" or "use
  information from TV inputs"; other makers use their own names. Record whether it is on.
- Interest-based or personalized advertising: usually a separate setting from ACR. Advertising ID reset or
  delete (Google TV and Android TV document resetting or deleting the advertising ID; ads can't be turned
  off, only personalization).
- Usage and diagnostics data sharing, voice-recording retention, and marketing consents in the privacy or
  terms section, and in the platform account on the web.
- Whether the user accepted optional terms or agreements at setup that can be withdrawn later.
- Background: regulators have acted on ACR. The FTC and New Jersey settled with Vizio in 2017 over
  collecting viewing data from millions of TVs without consent, and Texas sued five TV makers over ACR in
  2025 (references). Treat ACR as on until the screen shows it off.

#### D. Microphones, cameras, and voice assistants

- Far-field microphones built into the TV (always-listening for a wake word) versus a push-to-talk
  microphone in the remote. Whether there is a physical microphone switch and its position.
- Built-in or attached cameras (some TVs support pop-up or USB cameras for video calls): present, which
  apps have camera permission, and whether a cover is used.
- Voice assistants enabled (Google Assistant/Gemini, Alexa, Bixby, Siri, or others), which account they
  use, and voice-recording history and retention in that account.
- Per-app microphone and camera permissions on Android-based platforms.
- Hands-free control linked to smart-home devices (a TV that can unlock or disarm through a voice
  assistant routine is a finding).

#### E. Developer mode, sideloading, and debugging

- **Google TV / Android TV:** whether developer options are enabled; **USB debugging**; **network or
  wireless debugging** (ADB over the network, TCP 5555 by default). ADB over the network gives a shell and
  app-install rights to anyone who can reach the port and pass any authorization prompt; botnets have
  spread across devices with exposed ADB ports. Also which apps are allowed to install unknown apps.
- **Fire TV:** developer options (may be hidden until unlocked), **ADB debugging**, and **apps from
  unknown sources**.
- **Roku:** developer mode (for installing development channels); the External Control network-access
  setting (domain H).
- **Samsung and LG:** developer mode or the Developer Mode app, and any host computer address configured
  for it.
- **Apple TV:** whether the device is paired with a computer for development (shown under remotes and
  devices in settings, per the current tvOS).
- Anything enabled that the household didn't knowingly turn on is a finding; enabled debugging the user
  doesn't recognize is a possible **P0 indicator** (Respond).

#### F. Installed apps and app sources

- The full installed-apps list. Flag unofficial app stores, "free TV" or "free movies" apps, IPTV apps with
  unknown sources, VPN or proxy apps the user didn't install, file managers and sideloading tools, and apps
  with device-admin or accessibility permissions.
- Google Play Protect status on Android-based devices (on, and no warnings). A device that requires Play
  Protect to be disabled is a red flag (FBI BADBOX 2.0 guidance).
- Whether the device is Play Protect certified (Android TV devices) or a genuine branded device.
- Unused apps that still have accounts signed in.

#### G. Network placement and egress

- Which network the device uses. Ideally an IoT or media segment that can reach the internet and, if the
  household casts from phones, can be reached by the phones' network for casting, but can't reach
  computers, NAS, or admin interfaces.
- Casting across segments needs mDNS or SSDP forwarding; note that enabling a reflector widens what
  can discover the TV. Prefer narrow rules.
- Egress options and their trade-offs: blocking all internet (only works for a TV used purely with an
  external streamer or antenna, and stops updates), blocking only tracking or advertising domains with a
  DNS filter (can break apps; some devices use hardcoded public DNS resolvers or encrypted DNS, which
  bypasses local filtering unless outbound DNS is restricted), or leaving it open on an isolated segment.
- Whether the TV is on a guest network that visitors also use (visitors can then control and cast to
  it).
- Wired versus Wi-Fi; Wi-Fi Direct or screen-mirroring hotspots the TV creates itself.

#### H. Local control and casting exposure

- **UPnP on the router:** port mappings created by TVs or streaming devices (they rarely need any). UPnP
  enabled for the TV's segment.
- **Roku External Control network access:** Roku documents settings that allow, restrict, or disable
  control by mobile apps. Its "permissive" option is meant for unusual network setups; on a home network
  the default or disabled is expected.
- **Samsung and LG phone-control APIs:** whether new control connections require on-screen approval, and
  which devices were previously allowed (some TVs list paired devices).
- **Google Cast:** whether guest mode or casting from devices not on the same network is enabled; which
  networks can see `_googlecast._tcp`.
- **AirPlay access** (Apple TV and AirPlay-capable TVs): who may cast (everyone, anyone on the same
  network, or only people sharing the home), and whether a code or password is required.
- **DIAL** and "second screen" features that let apps on the network launch apps on the TV.
- **Bluetooth** pairing of remotes, keyboards, and audio; unknown paired devices.
- **HDMI-CEC** and IP control (for home-automation systems): expected, and limited to known controllers.

#### I. Physical, shared spaces, and disposal

- Shared or business displays: casting restricted to the intended network; personal accounts not left
  signed in; screen-content exposure to visitors.
- USB ports: auto-play or auto-install from USB media.
- Retired TVs and streamers: signed out of all accounts, removed from account device lists, and factory
  reset before sale or disposal (on the user's own initiative; never by the agent).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**. Write TV changes as clear
steps described by function, and tell the user to confirm the menu path on their model.

### Dependency and blast-radius check (required)

- **Household viewing:** which apps, accounts, and features people use every day (voice search,
  recommendations, casting from phones, AirPlay from laptops).
- **Casting and control paths:** phones and laptops on other segments that cast or control the TV, and
  home-automation systems that turn it on, change inputs, or read its state.
- **Accounts:** signing out of a platform account can remove purchased apps or settings from the device.
- **Network changes:** moving a TV to another segment breaks casting and remote apps until discovery and
  firewall rules are in place.
- **Egress filtering:** blocking domains can break streaming apps or updates in ways that are hard to
  diagnose later; document every block.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| End-of-support TV online | Disconnect it from the network; use a supported external streamer. | Built-in apps and smart features stop; picture and inputs keep working. |
| Updates off or stale | Enable automatic updates; apply pending updates. | Brief restart; occasional feature or layout changes. |
| ADB, USB, or network debugging on | Turn off debugging and developer options. | Sideloading tools and developer workflows stop. |
| Unknown sources allowed | Disallow for every app that doesn't need it; remove sideloaded apps not deliberately installed. | Sideloaded apps can't be updated or reinstalled. |
| Uncertified or "unlocked" Android box | Remove it from the network and replace it with a certified device. | Loss of the box's "free content" apps. |
| ACR on | Turn off content recognition and interest-based ads; reset or delete the advertising ID. | Fewer recommendations; some "what's on" features stop. |
| Far-field mic or camera not needed | Turn off the microphone switch or wake-word setting; cover or disconnect the camera. | Hands-free voice control and video calls stop; push-to-talk remote may still work. |
| Primary personal account on a shared TV | Use a dedicated or family account; add a purchase PIN. | Personal recommendations and libraries move. |
| Stale devices in platform accounts | Remove them from the account on the web. | None for current devices. |
| TV on main LAN | Move to an IoT or media segment with narrow casting rules. | Casting may break until mDNS/SSDP rules are set. |
| TV on guest network | Move it off the guest network. | Guests can no longer cast without a deliberate path. |
| UPnP mappings from TVs | Disable UPnP or restrict it so TVs can't create mappings. | Rarely any visible effect for TVs. |
| Roku network control permissive | Return to the default, or disable if no phone app is used. | The Roku mobile app and some home-automation integrations may stop working (if disabled). |
| AirPlay or Cast open to everyone | Restrict to the same network or household, and require a code where offered. | Visitors need to be added or enter a code. |
| Tracking-domain blocking wanted | Use a DNS filter on the TV's segment; restrict outbound DNS so the TV can't bypass it. | Some apps break; maintenance burden. |

Changing the TV's name, hiding it from discovery menus, or disabling only one discovery protocol are
supplementary only. Never recommend them as the main fix.

Group the plan: immediate containment (if any) → urgent fixes (enabled debugging, untrusted boxes,
end-of-support devices online) → high-priority hardening (network placement, casting exposure, account
protections) → privacy settings → optional egress filtering. Then ask for approval (core: modes and
authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. The user makes TV-side changes with
the remote while the agent guides and verifies from photos. Smart-TV specifics:

- **Before any change:** photograph the current settings screen, so the old value can be restored.
- **Settings toggles** (ACR, ads, debugging, unknown sources, AirPlay or Cast access, Roku network
  control) are usually **C1**. Turning off a feature the household uses daily (voice, casting) is **C2**
  in practice; confirm with the household first.
- **Uninstalling apps is C2**, and C3 for any app data it removes (game saves, downloads). Note the app and
  account first.
- **Updates are C2:** the TV restarts and may change settings or re-prompt for terms. After updating,
  re-check domain C and E settings.
- **Network moves are C2:** move one device at a time; confirm streaming, casting from each needed
  device, and remote apps before moving the next. Add discovery and firewall rules on the firewall (see
  the firewall's own skill) before moving.
- **Router changes** (UPnP, DNS filtering, egress rules) belong to the router or firewall skill and its
  blast-radius checks.
- **Account changes** (signing out, removing devices from an account, adding a purchase PIN) are done by
  the user on the platform's website or the device; removing the wrong device signs out a TV in use.

After each change, follow the core "after a change" steps: have the user re-photograph the setting,
confirm the TV still streams and casts as needed, re-run the port-state check for any service that should
now be closed (for example 5555), and record before and after.

### Hard stops (refer to a specialist or do manually; never automate)

- Connecting to ADB or any debugging interface, even to "turn it off" or remove a suspicious app.
- Factory resetting a device as security remediation while an incident is open, or without the user's own
  decision at retirement.
- Rooting, jailbreaking, or flashing custom firmware or launchers.
- Installing "cleaner", antivirus, or "booster" apps from outside the official store.
- Disabling automatic updates to keep a feature.
- Sending remote-control, launch, or cast commands to any device.

---

## Respond

On any P0 indicator (debugging enabled that nobody turned on, apps nobody installed, Play Protect turned
off, purchases nobody made, unknown devices in the platform account, the device generating heavy outbound
traffic while idle, or traffic consistent with proxying), switch to Respond immediately. Follow the core
playbook plus the smart-TV-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### TV-001: Network ADB debugging enabled on a Google TV device on the main LAN

**Confidence:** Confirmed
**Priority:** P2. Anyone on the main LAN who can pass the ADB authorization (or uses a computer already
authorized) can install apps and run commands on the device; malware on any LAN computer could do the
same. The port isn't reachable from the internet, so not P1.
**State:** Open
**Component:** Google TV streaming device, developer options; OS version as shown on the user's photo
**Evidence:** User-provided photo, 2026-03-11: developer options visible, USB debugging and network
debugging on. With approval, a TCP connect port-state check from `192.0.2.50` showed TCP 5555 open on
`192.0.2.60` (observed); no ADB connection was attempted. The user says a family member enabled it last
year to sideload an app they no longer use.
**Expected secure state:** developer options and debugging off on production devices (Android developer
documentation); TVs on an isolated segment.
**Exposure and prerequisites:** reachable from every device on the main LAN; requires an authorized ADB
key or acceptance of an authorization prompt on the TV.
**Dependencies / blast radius:** the sideloaded app will no longer be updatable; no other use reported.
**Recommended remediation:** turn off network and USB debugging, then developer options; review the
installed-apps list for sideloaded apps; later, move the device to the media segment.
**Operation class:** C1 (a settings toggle with a known prior value; no outage).
**Approval required:** Yes.
**Verification:** user photo shows debugging off; the port-state check shows TCP 5555 closed.
**Rollback:** re-enable in developer options (not recommended).

---

## Version history

- **1.0** (2026-10-30): Initial version.
