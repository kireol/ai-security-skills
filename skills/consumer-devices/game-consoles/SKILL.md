---
name: game-consoles
description: >-
  Security, privacy, and family-safety assessment, hardening, remediation, and incident response for game
  consoles and gaming handhelds: PlayStation, Xbox, Nintendo Switch and Switch 2, and Steam Deck or other
  SteamOS devices. Use when reviewing console and platform-account security (2-step verification,
  passkeys, stored payment methods, purchase PINs), family and parental controls, voice and text chat
  privacy, UPnP and NAT-type requests on the router, remote play, update status, SteamOS desktop mode
  and SSH, or when a gaming account may have been taken over or a household member was targeted by a
  gaming scam.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Current console and handheld platforms: PlayStation 4/5, Xbox One and Series X|S, Nintendo Switch and Switch 2, Steam Deck and other SteamOS devices (verify the live system software; menus and account features change often)"
  audience: "home, work"
  finding_prefix: "GAME"
  modes: "discover, recommend, remediate, respond"
---

# Game Console and Handheld Security

Act as a careful, family-minded security advisor for the game consoles and gaming handhelds in a home.
The console itself is rarely the weak point: console makers lock their systems down hard, and updates
arrive automatically. The risks live in the **platform account** (a store account with a stored card,
years of purchases, and a friends list, which makes it a prized target for takeover and resale), in
**children's access** to purchases, chat, and strangers, in the **router changes** consoles ask for
(UPnP, open NAT, port forwards, DMZ), and in **scams** aimed at players. A Steam Deck or other SteamOS
device is also a Linux computer with a desktop mode. Identify, explain, prioritize, remediate (only when
authorized), and verify weaknesses in the devices, the accounts, the family settings, and the network
around them.

## How to use this skill

This skill holds only game-console-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Console-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
is in [references.md](references.md). Related skills: [home-routers](../../network/home-routers/SKILL.md)
for UPnP, port forwards, and DMZ; [smart-tvs](../smart-tvs/SKILL.md) for the TV the console is plugged
into and for media apps; [phones](../../mobile/phones/SKILL.md) for the companion apps and the
authenticator; [mfa](../../identity/mfa/SKILL.md) for 2-step verification and passkeys in depth;
[linux](../../operating-systems/linux/SKILL.md) for a Steam Deck's desktop mode.

## Console-specific principles

- **The account is the asset.** A PlayStation, Microsoft (Xbox), Nintendo, or Steam account holds a
  stored payment method, a digital library that can be worth a lot of money, wallet funds, and a friends
  list that attackers use to scam others. Stolen gaming accounts are resold, so takeover is common and
  often targets children's accounts. Account security comes before console settings.
- **Platforms differ in which protections they offer, and they change.** At the time of writing,
  PlayStation, Microsoft, and Nintendo accounts support passkey sign-in in addition to 2-step
  verification, while Steam relies on Steam Guard (mobile authenticator or email codes) and reporting in
  October 2026 found no Steam passkey rollout. Verify each platform's current options on its own
  support pages before recommending one.
- **Children's accounts are a separate system per platform.** PlayStation Family Management, Microsoft
  Family Safety (Xbox Family Settings), Nintendo Switch Parental Controls, and Steam Families each have
  their own rules, and none of them carry over to the others. A child often has accounts on several
  platforms plus third-party game accounts (for example Epic, Roblox, or Minecraft through a Microsoft
  account) with their own chat and purchase settings.
- **Consoles ask the router for open doors.** Online games and voice chat prefer an "open" NAT type and
  use UPnP to create port mappings automatically. That is normal, but it means **UPnP** on the router
  lets any device on the network, including a compromised one, open ports to the internet. The trade-off
  between NAT type and UPnP exposure is a router decision; consoles never need a DMZ.
- **Scams target the person, not the console.** Free-currency offers, fake giveaways, "I accidentally
  reported you" messages, fake trade or tournament sites, fake support agents, and requests to "verify"
  an account with a code are the usual routes into an account. Education is part of the remediation.
- **The agent never signs in or buys.** Don't sign in to the user's platform accounts, approve
  purchases, change parental controls, or send messages on the user's behalf. Guide the user and record
  from screenshots.
- **SteamOS desktop mode is a Linux computer.** Steam Deck and other SteamOS devices boot into a console-
  like Gaming Mode but have a full KDE desktop. By default the `deck` user has no password, so `sudo`
  can't be used until one is set; the SSH server is installed but not running. Once a user sets a
  password and starts SSH, the device is a Linux host on the network.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **PlayStation 5 / PS4** | Sony console; PlayStation Network (PSN) account. | 2-step verification (SMS or authenticator app) and passkey sign-in in PSN account management; Family Management sets per-child limits on chat, purchases, age ratings, and play time; Remote Play from phones and PCs; automatic system software updates. |
| **Xbox Series X\|S / Xbox One / Xbox on PC** | Microsoft console; Microsoft account. | The Microsoft account (also used for Windows, Outlook, and Minecraft) protects everything; console sign-in and purchase protection are set in the console's sign-in, security, and passkey settings; Microsoft Family Safety and the Xbox Family Settings app control children; remote play and "remote features" let a phone app control the console. |
| **Nintendo Switch / Switch 2** | Nintendo console; Nintendo Account. | 2-step verification and passkeys on the Nintendo Account website; Nintendo Switch Parental Controls app sets play limits and communication restrictions; eShop purchase password setting; Switch 2 adds GameChat (voice, screen share, and camera), which Nintendo gates for children through parental controls (verify current rules). |
| **Steam Deck / SteamOS handheld or PC** | Valve's Steam Deck or another device sold or installed with SteamOS; Steam account. | Steam Guard mobile authenticator; Steam Families for child accounts and purchase approval; desktop mode, `sudo` password, SSH, Flatpak apps from Discover, and the device's own Linux updates; Steam Remote Play and Steam Link. |
| **Gaming PC** (Steam, Epic, Xbox app, and others on Windows) | A Windows computer with launchers. | The [windows](../../operating-systems/windows/SKILL.md) skill covers the PC; this skill covers the launcher accounts, family settings, and scam patterns. Mods, cheats, and "free game" downloads are a common malware route. |
| **Retired, modded, or jailbroken console** | Old console no longer updated, custom firmware, homebrew launcher. | Custom firmware removes the platform's protections and may get the account banned; an old console no longer updated is an end-of-support device if it stays online with a signed-in account. |

## Detection

Hints for recognizing consoles during a network inventory (used by the `full-assessment` skill). Ports
listed are vendor-documented or commonly reported; confirm with the user before relying on a match, and
never interact with these services beyond observing that they exist.

- **MAC address vendors (OUI)** registered to Sony Interactive Entertainment, Microsoft, Nintendo, or
  Valve are the strongest hint; handhelds from other makers show their Wi-Fi module's vendor. DHCP
  hostnames often name the console (for example a PS5 or Xbox default name).
- **UPnP port mappings** on the router that name the console or a game, and SSDP (UDP 1900) M-SEARCH
  requests from the console looking for the router's UPnP service.
- **Outbound traffic patterns:** Xbox network uses UDP 88, 500, 3074, 3544, and 4500 and TCP 3074
  (Microsoft-documented port list; verify on the live page). PlayStation Network commonly uses TCP and
  UDP around 3478–3480 (commonly reported; Sony's current list may differ). Nintendo recommends wide UDP
  ranges for some games (verify on Nintendo's network-troubleshooting pages).
- **Remote play and local discovery:** Steam Remote Play uses UDP 27031–27036 and TCP 27036 on the
  local network, with UDP 27036 for discovery (Valve-documented); PlayStation Remote Play and Xbox
  remote features use their own discovery and streaming ports (commonly reported; not vendor-verified
  here).
- **Steam Deck in desktop mode** with SSH started shows **TCP 22** open; in Gaming Mode it normally
  listens on nothing beyond Steam's local discovery and streaming.
- Consoles sometimes appear as DLNA/UPnP media renderers or Cast targets when media apps are installed.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Most checks are **user-run** on the console, in the platform's website or phone app, and in
the router's admin page; the agent guides and records. Mark anything you can't inspect **Not assessed**.

### Access and baseline

Ask the user for, per console or handheld:

- Platform and model, who uses it, and which accounts are signed in (adult, child, shared, guest).
- Screenshots of: the system software version and update settings; the account's security page on the
  platform's website (2-step verification, passkeys, devices, recent sign-in activity); the family or
  parental-control settings for each child; the payment-method and purchase-protection settings.
  Redact email addresses, gamertags, real names, and payment details.
- From the router (or the [home-routers](../../network/home-routers/SKILL.md) skill): UPnP on or off,
  current UPnP mappings, port forwards and DMZ entries pointing at consoles, and which network segment the
  consoles are on.

Candidate read-only checks, **not yet verified** on every model. Run them only with the user's
authorization, from a host the user controls, against the user's own devices:

```sh
nmap -sT -Pn -p 22,27036 192.0.2.70   # TCP connect only; a Steam Deck with SSH started shows 22 open
```

On a Steam Deck in desktop mode, with the user at the keyboard (read-only; no `sudo` needed):

```sh
systemctl is-active sshd            # "inactive" is the default (not yet verified on every SteamOS build)
systemctl is-enabled sshd           # whether SSH starts at boot
cat /etc/os-release                 # SteamOS version
flatpak list --app                  # desktop apps installed from Discover
```

- Ask the user whether they have ever set a `deck` password (with `passwd`); don't test it.
- **Never:** sign in to the user's accounts; make or approve purchases; add or remove payment methods;
  send messages or friend requests; enable SSH or set a password on the user's behalf; jailbreak or
  install homebrew; test credentials; or join the user's account to "check" anything.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Platform, updates, and support

- System software version and automatic updates on (consoles usually update in rest or standby mode;
  a console that is always unplugged may lag).
- Whether the console or handheld still receives updates. Old generations eventually stop getting
  system updates and lose online services; a console kept online with a signed-in account and stored
  payment method after support ends is an end-of-life finding (core triage).
- Steam Deck / SteamOS: SteamOS update channel (Stable is expected for a child's device), the date of
  the last update, and desktop apps (Flatpak) updated through Discover.
- Custom firmware, homebrew, or a jailbroken console: present or not, and who installed it.

#### B. Platform account security

Per account (PlayStation, Microsoft, Nintendo, Steam, plus third-party game accounts used on the
console). Coordinate with the [mfa](../../identity/mfa/SKILL.md) skill.

- A unique, strong password, stored in a password manager; the account email's own account protected
  (an attacker who controls the email can reset every gaming account).
- **2-step verification** on, with an authenticator app or passkey rather than SMS where offered;
  **passkeys** registered where the platform supports them; Steam Guard **mobile authenticator** rather
  than email codes on Steam.
- Backup or recovery codes saved somewhere safe; recovery phone and email current. Several platforms
  require contacting support (with proof of ownership) if both the second factor and the backup codes
  are lost.
- Devices and sessions signed in to the account (the platform's website lists them): unknown or old
  consoles, PCs, and phones; Steam's authorized devices and "deauthorize all other devices" option.
- Linked third-party accounts and apps (streaming, Discord, game publishers' accounts): which are still
  needed.
- Recent sign-in activity and security emails: unfamiliar locations or devices.
- The **primary console** setting (PlayStation's console-sharing / primary PS, Xbox's "home Xbox",
  Nintendo's primary console): it lets every account on that console use the owner's purchases. A
  primary console the household no longer owns is a finding.

#### C. Payments and purchase protection

- Stored payment methods on each account; whether wallet top-ups or auto-renewing subscriptions exist.
- Purchase protection: a password, PIN, or passkey required at checkout (PlayStation's sign-in and
  purchase settings, Xbox's sign-in, security, and passkey preferences, Nintendo eShop's purchase
  password setting; verify current names on the live console). A stored card with no purchase
  protection on a shared console is a finding.
- For children: spending limits or "ask to buy" approval (Family Management, Microsoft Family Safety,
  Nintendo Parental Controls, Steam Families purchase requests); wallet top-ups by gift card instead of a
  stored card.
- Purchase history and receipts: unexpected purchases, subscriptions, or gift-card redemptions.

#### D. Family and parental controls

Per child, per platform:

- The child has their own child account under the family, not an adult's account or a shared profile.
- Age-rating limits for games, apps, and web browsing; play-time limits.
- Communication: who the child can message, voice chat with, and accept friend requests from (no one,
  friends only, or anyone); whether user-generated content and screen sharing are allowed. On Switch 2,
  GameChat camera and voice settings for children (Nintendo documents parental controls for it; verify).
- Purchases: spending limits and approval (domain C).
- Whether the child can bypass controls: an unsupervised adult account on the same console without a
  passcode, a parental-control PIN that is too easy or known to the child, guest sign-ins, or a second
  console or PC without controls.
- Third-party game accounts the child uses (with their own chat and purchase settings) and companion apps
  on the child's phone.
- Parents' own accounts are protected with 2-step verification (they control the child's settings).

#### E. Voice, text chat, and privacy

- Online status and activity visibility (who can see what the user is playing and when they are
  online), real name sharing, and friend-list visibility.
- Party and game chat settings; whether chat is recorded or reported clips are shared with the platform
  (some platforms record voice for moderation; check the platform's privacy pages).
- Cameras and microphones attached to the console or handheld; Switch 2 camera; Steam Deck microphone in
  desktop apps.
- Screenshots and video captures automatically uploaded or shared; broadcasting to streaming services
  linked to the account.
- Data-sharing and personalized-advertising settings in the platform account.

#### F. Network: UPnP, NAT type, and exposure

- **UPnP** on the router: enabled for the console's segment or not, and which mappings consoles created.
  Explain the trade-off (domain principle). Some routers offer UPnP limited to specific devices or with
  short lease times; the router skill covers the options.
- **NAT type** shown on the console (Open / Moderate / Strict, or Type 1–3): what the household actually
  needs. Many households play fine with Moderate.
- **Port forwards and DMZ** entries pointing at consoles. A console in the router's DMZ (exposed host) is
  a finding: it puts every port on the console on the internet and is never needed; a few static
  forwards for the platform's documented ports are the narrower alternative to UPnP.
- **Network segment:** consoles on the main LAN, a gaming or IoT segment, or the guest network. Isolation
  from computers and NAS is good; it needs care because remote play and casting rely on local discovery.
- **Remote play and remote features:** PlayStation Remote Play, Xbox remote play and remote features,
  Steam Remote Play and Steam Link, Nintendo's app features. Which devices are linked, and whether
  remote play from outside the home is enabled.
- Steam Deck: SSH running or enabled at boot, and whether password authentication is allowed; other
  services started in desktop mode (file sharing, game-streaming servers, remote desktop).

#### G. SteamOS desktop mode (Steam Deck and other SteamOS devices)

- Whether a `deck` password has been set, how strong it is, and who knows it. Without a password, nobody
  can `sudo`; with a weak one, anyone with the device or SSH access can become root.
- SSH: inactive (default), active, or enabled at boot; key-only or password; reachable from which
  networks. The [linux](../../operating-systems/linux/SKILL.md) skill's SSH checks apply.
- Whether the read-only root filesystem was disabled (`steamos-readonly`), and packages installed with
  `pacman` (these are lost on SteamOS updates and bypass the image's integrity).
- Desktop apps (Flatpak) and their sources; non-Steam games and launchers added; browser and saved
  passwords in desktop mode.
- Decky Loader or other plugin frameworks, and plugins installed from unofficial sources (they run with
  elevated rights on the device).
- A child using the device: Steam Families restrictions apply in Gaming Mode, but desktop mode can bypass
  some of them. Check whether the child can reach desktop mode and a browser.

#### H. Scams and account-takeover exposure

Ask the household, especially children, about:

- Offers of free in-game currency, skins, or items; "generators"; giveaways that ask for sign-in.
- Messages saying the account was "reported" or "will be banned" and pointing to a support contact,
  Discord server, or website; anyone asking for a code that was just sent to them (that code signs in or
  approves a login).
- Off-platform trades, account sharing, or account buying/selling (against platform rules and a common
  way to lose an account).
- Fake login pages for votes, tournaments, or trades (Steam-themed phishing is common); QR codes shown on
  websites that ask to be scanned with the platform's mobile app (scanning approves a sign-in).
- Downloads of mods, cheats, or "free game" installers on gaming PCs.
- Gift-card requests from "friends" or fake support.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**. Describe console
settings by function and give the usual menu name as a hint; tell the user to confirm the path on their
system software version.

### Dependency and blast-radius check (required)

- **Online play and voice chat:** changing UPnP, removing port forwards, or moving a console to another
  segment can change the NAT type and break party chat or matchmaking for some games.
- **Remote play and companion apps:** segmenting the network or turning off remote features breaks
  phone apps and remote play until discovery rules exist.
- **Accounts shared across devices:** a Microsoft account also signs in Windows, Outlook, and Minecraft;
  changing its password or 2-step verification affects all of them.
- **Primary-console and game-sharing settings:** changing them removes access to purchased games for
  other accounts on that console.
- **Children:** tighter controls work better when explained; a child locked out of chat with friends may
  move to an unsupervised device or account.
- **Steam Deck:** turning off SSH breaks file-transfer or development workflows; check who relies on it.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No 2-step verification | Turn on 2-step verification with an authenticator app or passkey; Steam Guard mobile authenticator on Steam. | Save backup codes; losing both the phone and codes means a support recovery. |
| Passkeys supported but unused | Register a passkey on the platform account (in a password manager or phone). | Keep a second sign-in method. |
| Stored card, no purchase protection | Require a password, PIN, or passkey for purchases; or remove the stored card and use gift cards. | One more step at checkout. |
| Child on an adult account | Create a child account under the family and move the child to it. | Saves and purchases may need moving; check platform rules. |
| Chat open to anyone for a child | Limit to friends, or off, per age. | Less contact with strangers; some games' features limited. |
| Unknown devices or sessions | Sign them out; change the password; deauthorize other devices (Steam). | Every device must sign in again. |
| Old primary console | Remove it as primary (often from the account's website). | Some platforms limit how often this can be done. |
| Console in the router's DMZ | Remove it; use UPnP or a few documented port forwards. | NAT type may change; test online play. |
| UPnP on for the whole LAN | Restrict UPnP to the consoles (if the router supports it) or replace with static forwards; or accept, with monitoring. | Some games may show a stricter NAT type. |
| Consoles on the main LAN | Move to a gaming or IoT segment with rules for remote play. | Remote play and casting need discovery and firewall rules. |
| Steam Deck SSH running | Stop and disable SSH when not in use; use keys if kept. | File-transfer workflows change. |
| Weak or shared `deck` password | Set a strong password known only to the device's adult owner. | Children can't use `sudo` in desktop mode. |
| Custom firmware or jailbreak | Keep it offline with no signed-in accounts, or restore official firmware (vendor procedure). | Homebrew stops working; risk of bans. |
| Scam exposure | Household talk: never share codes, never sign in from links, use the platform's own app for trades and support. | None, beyond time. |

Group the plan: immediate containment (if any) → urgent fixes (accounts without 2-step verification,
stored cards without purchase protection, consoles in a DMZ) → family controls → network hardening →
privacy and optional settings. Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. The user (an adult account holder)
makes the changes on the console, website, or phone app; the agent guides and verifies from
screenshots. Console specifics:

- **Account changes** (password, 2-step verification, passkeys, signing out devices, removing payment
  methods) are **C2**: they can lock people out and affect every device on the account. Do them from a
  trusted device, save backup codes first, and keep one session signed in until the new method is
  tested.
- **Parental-control and privacy toggles** are **C1**: screenshot the old settings first.
- **Moving a child to a new child account** is **C2**, and C3 for any saves or purchases that can't be
  transferred; check the platform's rules first.
- **Router changes** (UPnP, port forwards, DMZ, segments) belong to the router or firewall skill and its
  blast-radius checks; they are **C2**. Test online play and remote play after each change.
- **Steam Deck:** stopping and disabling SSH is **C1**; setting or changing the `deck` password is **C2**
  (forgetting it means a reset from a TTY or a reimage); re-enabling the read-only filesystem may remove
  packages installed with `pacman`.
- **System updates** are normally automatic; installing a pending one is **C2** (restart, occasional
  re-prompts for terms).

After each change, follow the core "after a change" steps: re-screenshot the setting, test the household's
everyday use (online play, party chat, remote play, purchases with the new protection), and record before
and after.

### Hard stops (refer to a specialist or the platform; never automate)

- Jailbreaking, installing custom firmware, or restoring official firmware outside the vendor's own
  documented procedure.
- Buying, selling, or "recovering" accounts through third parties, or paying anyone who claims they can
  restore an account.
- Making purchases, chargebacks, or refunds on the user's behalf; the account holder contacts the
  platform.
- Disabling the SteamOS read-only filesystem or installing system packages as a security fix.
- Monitoring a child's private messages beyond what the platform's parental controls provide; that is a
  household decision, not an agent action.

---

## Respond

On any P0 indicator (security emails about sign-ins or password changes nobody made, purchases or wallet
spending nobody recognizes, a changed account email or 2-step verification setting, friends reporting
scam messages sent from the account, a child reporting a stranger pressuring them for codes or
pictures, or SSH open on a Steam Deck nobody configured), switch to Respond immediately. Follow the core
playbook plus the console-specific steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### GAME-001: Shared console with a stored card and no purchase protection; child uses a parent's account

**Confidence:** Confirmed
**Priority:** P3. Anyone using the living-room console, including children and visitors, can buy games,
add-ons, and wallet funds on the parent's card without a prompt; no sign of misuse so far, and the
account itself has 2-step verification.
**State:** Open
**Component:** Living-room console; parent's platform account; system software current.
**Evidence:** User screenshots, 2026-05-20: payment method saved on the parent's account; purchase
setting shows no password required at checkout; the child signs in to the parent's account to play
because no child account exists. Purchase history shows only expected purchases. Router page shows
UPnP enabled with two mappings from the console at `192.0.2.80` (observed).
**Expected secure state:** password, PIN, or passkey required for purchases; each child on their own
child account under the family group with spending limits (platform family-settings documentation).
**Exposure and prerequisites:** physical access to the console while the parent's account is signed in.
**Dependencies / blast radius:** the child's game saves are on the parent's account; moving to a child
account may mean starting some games again; the parent plays online and uses party chat.
**Recommended remediation:** turn on the purchase password/PIN setting now; create a child account in
the family group with chat limited to friends and spending by approval; then decide with the child how to
move saves. UPnP left on (accepted for the household's online play), reviewed again in the router
assessment.
**Operation class:** C1 (purchase setting); C2 (new child account and moving the child).
**Approval required:** Yes.
**Verification:** a test checkout on the console asks for the password/PIN; the child's account
appears in the family settings with the chosen limits.
**Rollback:** the purchase setting can be turned off again from the screenshot of the previous state.

---

## Version history

- **1.0** (2026-10-31): Initial version.
