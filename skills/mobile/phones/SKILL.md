---
name: phones
description: >-
  Security and privacy assessment, hardening, remediation, and incident response for cell phones and
  tablets: iPhone (iOS), iPad (iPadOS), and Android phones and tablets (Pixel, Samsung Galaxy, and other
  makers), personal and work devices, and phones and tablets used by family members and children,
  including shared family tablets. Use when reviewing a phone's or tablet's OS version and support window,
  updates,
  screen lock, Find My or Find Hub, theft protections (Stolen Device Protection, Android Theft Protection
  and Identity Check), Lockdown Mode or Android Advanced Protection, Apple Account or Google Account
  security, SIM PIN and carrier protections against SIM swap and port-out, app permissions, accessibility
  and device admin apps, configuration profiles and MDM, sideloading, jailbreak or root, VPN and private
  DNS, Bluetooth, AirDrop, and Quick Share, backups, stalkerware and unwanted trackers, work profiles, or
  disposal and resale, shared or family tablets (whose account the iPad is signed in to, Screen Time,
  Family Link and Kids Space, Android multiple users, guest mode, and restricted profiles, organization
  Shared iPad), or when a phone, a tablet, or its accounts may have been compromised, lost, or stolen.
license: CC-BY-4.0
metadata:
  version: "1.1"
  last_reviewed: "2026-10-31"
  applies_to: "iPhone on iOS, iPad on iPadOS, and Android phones and tablets (Pixel, Pixel Tablet, Samsung Galaxy and Galaxy Tab, and other Google-certified devices) on versions still receiving security updates; feature names and menu paths change between releases, makers, and between phones and tablets, so verify on the live device"
  audience: "home, work"
  finding_prefix: "PHN"
  modes: "discover, recommend, remediate, respond"
---

# Phone and Tablet Security (iPhone, iPad, and Android)

Act as a careful, privacy-minded phone security advisor. A phone is usually the most sensitive device a
person owns: it receives the codes that protect every other account, holds passwords and passkeys, banking
and payment apps, photos, messages, and location history, and is carried everywhere, so it is lost and
stolen more than any other device. The main risks are theft of an unlocked phone or a known passcode, a
takeover of the Apple Account or Google Account, a SIM swap or number port that diverts text-message
codes, malicious or over-privileged apps, unsupported software, and covert monitoring by someone close to
the user. Identify, explain, prioritize, remediate (only when authorized), and verify those weaknesses,
without locking the user out of their own phone or accounts and without putting a person at risk.

Tablets (iPad and Android tablets) are covered too. Most of this skill applies to them unchanged: read
"phone" as "phone or tablet" unless a check says otherwise. Tablets differ in a few ways that matter:
they are often **shared** by a household, often signed in to one adult's account while children use
them, often Wi-Fi-only (no SIM or phone number), often left at home on a stand or dock, and often bought
cheaply from makers with short or unknown update support. Domain P covers shared and multi-user tablets.

## How to use this skill

This skill holds only phone-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Phone-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation,
government guidance, and survivor-safety resources are in [references.md](references.md).

## Phone-specific principles

- **The user does the checks; the agent guides and records.** An agent normally has no access to a phone.
  Almost every check here is something the user does in Settings or in the account website and reports
  back (screenshots are fine; ask them to crop or redact names, phone numbers, contacts, messages, account
  emails, IMEIs, and serial numbers). Describe each setting by what it does, give the likely location, and
  ask the user to confirm the exact path on their version: menus differ between iOS releases, Android
  versions, and makers' skins (Samsung One UI, Pixel, others). Mark anything the user can't or won't check
  **Not assessed**.
- **Only assess a phone with its user's consent.** A phone belongs to the person who carries it, even
  inside a family. The agent assesses an adult's phone only with that adult's knowledge and agreement, and
  never helps anyone monitor, read, or track another adult's phone covertly. For children's phones, a
  parent or guardian may review settings with the child, in an age-appropriate and open way (domain M).
- **The agent never touches the user's secrets or accounts.** Don't ask for the passcode, the Apple
  Account or Google Account password, verification codes, recovery keys, recovery codes, carrier PINs, or
  the SIM PIN or PUK, and don't sign in to any of the user's accounts. Signing in adds a session to the
  account's device list and can trigger alerts, lockouts, or security delays.
- **The account matters as much as the device.** iCloud or Google backups, passwords, photos, messages,
  and the ability to locate, lock, and erase the phone all hang off the Apple Account or Google Account (and
  on Samsung phones, also the Samsung account). An attacker with the account often doesn't need the phone.
- **The phone number is an identity, and the carrier controls it.** Many banks, email providers, and
  social apps still send sign-in or recovery codes by text message. Anyone who can talk the carrier into
  moving the number to a new SIM or eSIM, or porting it to another carrier, receives those codes. Carrier
  account protections are part of phone security, even though they're set with the carrier, not on the
  phone.
- **Support windows are vendor commitments, and they differ.** Google commits to a published number of
  years of OS and security updates per Pixel model, counted from first availability; Samsung publishes
  per-model update tiers and longer commitments for recent flagships; Apple publishes minimum security
  update periods in regulatory statements (for example under the UK product security regime) rather than a
  general policy, and its own guidance says only the latest iOS gets every fix. Other Android makers vary
  widely. Always check the vendor's live page for the exact model; never rely on memory or on a static
  table. A phone that no longer gets security updates is an end-of-life finding (core triage).
- **Updates come from several places.** On Android, the monthly security patch level, Google Play system
  updates (Project Mainline modules), Google Play services, and app updates arrive separately; the maker
  and sometimes the carrier control OS and patch delivery. On iOS, Apple delivers OS updates and, on
  recent versions, smaller security fixes between them (see Apple's security releases page for the current
  mechanism and name). Check each source.
- **Safety comes first in abuse situations.** If the user suspects that a current or former partner,
  family member, or anyone with physical access is monitoring their phone, removing stalkerware, revoking
  access, or changing passwords can alert that person and escalate danger. The Coalition Against
  Stalkerware advises removing monitoring only when it is safe to do so, notes that removal also deletes
  evidence, and recommends building a safety plan with a survivor-support organization from a device the
  other person hasn't had access to. Pause, point the user to those resources, and let them decide the
  timing (see [incident-response.md](incident-response.md)). If anyone is in immediate danger, they should
  contact emergency services.
- **A work phone belongs to the employer's policy.** If the phone is enrolled in MDM or has a work profile,
  the employer's IT or security team decides what changes on the managed part. Assess and report; don't
  remove profiles, management, or work apps. On a personal phone, an MDM profile or device admin app the
  user didn't knowingly install is a serious finding.
- **A shared tablet shares an account.** Whoever's Apple Account or Google Account a tablet is signed in
  to, everyone who picks it up can usually see that account's messages, photos, email, saved passwords,
  purchases, and location sharing, and can act as that person. iPadOS on a consumer iPad supports one
  Apple Account per device; Apple's multi-user **Shared iPad** needs an organization's device management
  and Managed Apple Accounts, so it isn't available to a household. Android tablets support separate
  **users** and a **guest**, each with its own data and accounts, but the first user (the owner) controls
  device-wide settings. Assess the tablet by asking who uses it and as whom, not just how it's configured.
- **Vendor hardening modes are for high-risk users.** Apple's Lockdown Mode is described by Apple as an
  extreme, optional protection for a very small number of people who may be personally targeted by
  sophisticated threats such as mercenary spyware. Android's Advanced Protection bundles stricter settings
  and is less disruptive, but still blocks sideloading and changes some behavior. Explain trade-offs; don't
  recommend either by default.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Personal iPhone** | iOS; signed in to a personal Apple Account; no VPN & Device Management entry for an organization. | Apple controls updates and the app distribution model. Loss and theft, Apple Account security, and sharing settings dominate. |
| **Personal Pixel** | "Pixel" model in About phone; Google software; updates direct from Google. | Fastest Android security patches; theft protection, Identity Check, and Advanced Protection are typically available first. Support end date is on Google's Pixel update page. |
| **Personal Samsung Galaxy** | One UI; Samsung account alongside the Google Account; Samsung Knox and Auto Blocker settings. | Two accounts and two "find my phone" services (Find Hub and Samsung Find); Samsung's update tier (monthly, quarterly, or biannual) depends on model and region; carrier-sold models may update later. |
| **Other Android maker or carrier-branded phone** | Maker's skin; carrier apps preinstalled. | Patch delivery and support length vary widely; check the maker's policy. Uncertified devices (no Google Play Protect certification) lack some Google protections. |
| **Work phone, company-owned** | Supervised iPhone or fully managed Android; an organization name in management settings; work apps and restrictions. | The employer controls policy; many settings are locked. Report gaps and refer to IT. Don't change managed settings. |
| **Personal phone with work access (BYOD)** | iOS User Enrollment or account-driven enrollment; Android work profile (apps with a briefcase badge, a separate "Work" tab). | The organization manages only the work part and can usually wipe only that. Don't touch it. Personal-side checks still apply. |
| **Child's or teen's phone** | Apple Family Sharing with Screen Time, or a Google Account supervised with Family Link; Samsung or carrier parental-control apps. | Parental controls are legitimate monitoring done openly; check they're configured as the family intends and that the child's account recovery is held by the parent. Age rules and options differ by country. |
| **Older or secondary phone** (drawer phone, hand-me-down, dedicated 2FA or smart-home controller) | Out-of-date OS; still signed in to accounts; maybe still has a SIM. | Often unsupported and forgotten while still holding sessions, 2FA apps, and Wi-Fi passwords. Decide: update, repurpose offline, or retire (domain O). |
| **Family or shared iPad** | One iPad used by several people; signed in to one adult's Apple Account (or none); no multi-user login screen. | Everyone using it acts as that account holder. Check whose account it is, what syncs to it (Messages, Photos, Passwords, Mail), purchases, and Screen Time (domain P). |
| **Child's own iPad** | Signed in to the child's Apple Account in the parent's Family Sharing group; Screen Time managed from the parent's device. | Same as a child's phone (domain M); usually Wi-Fi-only, so no SIM or carrier checks. |
| **Organization Shared iPad** (school, office, clinic) | Login screen listing users or offering a guest or temporary session; supervised; managed by an organization. | Apple requires device management and Managed Apple Accounts issued by the organization, a supervised iPad, and at least 32 GB of storage. The organization controls it; report, don't change. |
| **Android tablet with several users or a guest** | Settings → System → Multiple users (Pixel Tablet) or Accounts and backup → Users (Samsung; verify, some recent One UI models have removed it); user icons on the lock screen or in quick settings. | Each user has separate apps and accounts; the owner controls device-wide settings, updates, and Wi-Fi. Guest sessions are temporary. Restricted profiles (offered on some tablets) limit apps to those the owner allows. |
| **Android tablet for a child** | A supervised Google Account (Family Link) as a user, or Google Kids Space on supported tablets. | Kids Space requires the child's Google Account to be managed with Family Link. Check that the child uses their own supervised profile, not the owner's. |
| **Tablet as a home hub or kiosk** (Pixel Tablet in hub mode on its dock, a wall-mounted tablet running a smart-home dashboard, a kitchen tablet) | Always on and on the network; content or controls usable without unlocking; often signed in to an adult's account. | Anyone in the home, including guests, may reach smart-home controls, photos, or the signed-in account. Check what works from the lock screen or hub mode, and treat a kiosk dashboard as a client of the smart-home system (see its skill). |
| **Low-cost or lesser-known-brand Android tablet** | Unfamiliar maker; old Android version; no published update policy; sometimes not Play Protect certified. | Often unsupported from the day it is bought. Limit it to low-risk use (no banking, no 2FA, no admin apps for the home network) or replace it. |
| **Rooted, jailbroken, or custom-ROM phone** | Unlocked-bootloader warning at boot; root or jailbreak apps; banking or payment apps refusing to run. | Platform protections are weakened or replaced. Treat as a deliberate user choice or a compromise indicator (domain H); don't "fix" it as routine remediation. |

## Detection

Hints for recognizing phones during a network inventory (used by the `full-assessment` skill). Phones
are often invisible or misleading on a network scan, so confirm with the user before relying on a match
and inventory phones by asking the household, not by scanning.

- **Private (randomized) Wi-Fi MAC addresses are the default.** iOS uses a private Wi-Fi address per
  network (with fixed and rotating options on recent versions), and Android uses a randomized MAC per
  network by default. These are locally administered addresses with no vendor (OUI) match, so "unknown
  vendor" Wi-Fi clients are often phones. A phone's address can change when the network is forgotten and
  rejoined, when rotation is on, or after a reset, so it may appear as several devices over time.
- **DHCP hostnames** are the best hint but are user-controlled: iPhones and iPads commonly send the
  device name ("iPhone", "iPad", or "<person>s-iPad"-style names); Android phones and tablets commonly
  send the device name, which is often the model ("Galaxy-…", "Galaxy-Tab-…", "Pixel-…",
  "Pixel-Tablet") or an `android-<hex>` string on older versions. Treat names that
  include a person's name as personal data and don't copy them into reports.
- **mDNS/Bonjour (UDP 5353):** iPhones may answer or announce Apple services such as
  `_companion-link._tcp` and `_apple-mobdev2._tcp` (Wi-Fi sync), especially when unlocked or charging.
  Android phones are usually quiet on mDNS unless an app is casting or sharing. A phone that answers
  nothing is normal.
- **Tablets are easier to see than phones.** They usually stay at home, and a tablet on a dock or stand
  (for example a Pixel Tablet in hub mode, or a wall-mounted dashboard tablet) stays on Wi-Fi around the
  clock. A docked tablet that can receive casts may advertise a Cast service (`_googlecast._tcp`) over
  mDNS; verify on the device. A tablet that never leaves the network and is never updated is a common
  forgotten device.
- **No listening services is normal.** Phones accept almost no inbound connections. An open port on a
  phone is unusual: it may be a debugging interface (Android wireless debugging), a hotspot, or an app's
  local server. Identify it with the user; never connect to it.
- **Why phones disappear:** they sleep Wi-Fi aggressively, move to cellular when Wi-Fi is weak, use
  private relay or VPN services that hide their traffic, and leave the network every time the user leaves
  home. A missing phone in a scan says nothing about its security.
- Router and access-point client lists (connected-device names, band, last seen) and the vendor accounts'
  device lists (Apple Account devices, Google "Your devices", Find My or Find Hub) are better inventory
  sources than scanning.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles): whose phone it is, whether that person consents and is present, whether it is personal,
work-managed, or a child's phone, and whether there is any safety concern (if there is, read the safety
principle above and [incident-response.md](incident-response.md) before continuing). Mark anything you
can't inspect **Not assessed**.

### Access and baseline

Ask the user for (redacted screenshots are fine):

- Make, model, and OS version (iOS: Settings → General → About; Android: Settings → About phone, plus
  Android version, **Android security update** date, and **Google Play system update** date, usually under
  Settings → Security & privacy → Updates or About phone → Android version; verify the path). Never ask
  for the IMEI or serial number.
- Whether it is personal, work-managed, or a child's phone; who else has used it, set it up, or had it
  unlocked. For a tablet: who uses it day to day, whose account it is signed in to, whether it has
  several users or a guest (Android) or a login screen (organization Shared iPad), and whether it has a
  cellular connection or is Wi-Fi-only (Wi-Fi-only tablets have no SIM, so domain F is Not applicable).
- The account security pages: Apple Account (Settings → [name] → Sign-In & Security, and the devices
  list), Google Account (Security Checkup and "Your devices" at the Google Account site), and the Samsung
  account on Galaxy phones.
- The carrier account's security settings (number lock, port-out PIN or passcode, SIM change alerts),
  checked by the user in the carrier's app or website.

Candidate read-only commands, used **only if the user directly asks** for computer-assisted checks on an
Android phone they own, with USB debugging they enable themselves and turn off afterward. These are
**not yet verified** on every version and maker. Don't enable debugging just to complete the assessment;
the Settings checks below cover the same ground.

```sh
adb devices                                         # lists the connected phone; the user approves the prompt
adb shell getprop ro.build.version.release          # Android version
adb shell getprop ro.build.version.security_patch   # security patch level
adb shell pm list packages -3                       # user-installed packages (names only)
adb shell dumpsys device_policy | head -50          # device admin and device owner apps (not yet verified)
adb shell settings get secure enabled_accessibility_services   # enabled accessibility services
```

There is no equivalent read-only command path for iPhone that is suitable for a home assessment; use
Settings walkthroughs.

**Never** do any of the following:

- sign in to the user's Apple Account, Google Account, Samsung account, carrier account, or any app, or
  use the user's sessions or tokens;
- ask for or record the passcode, account passwords, verification codes, recovery keys or codes, backup
  codes, carrier PINs, or the SIM PIN or PUK, or try to guess any of them (wrong SIM PIN entries lock the
  SIM and require the carrier's PUK);
- install monitoring, "anti-spyware", VPN, MDM, or management tools or profiles on the phone, or ask the
  user to install one, as part of the assessment;
- factory reset, erase, or restore the phone, or "Erase All Content and Settings";
- remove suspected stalkerware, revoke a person's access, or change passwords in a possible abuse
  situation before the user has a safety plan;
- connect over ADB, enable USB or wireless debugging, or use any forensic or extraction tool unless the
  user directly requests it for their own phone;
- jailbreak, root, unlock the bootloader, or install unofficial firmware;
- default-credential testing, password guessing, or exploit and proof-of-concept scripts against the
  phone, its accounts, or the carrier;
- read the user's messages, photos, email, or location history beyond what they choose to show.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Model, OS version, and support window

- Model and OS version against the vendor's live information:
  - **iPhone:** Apple's security releases page lists current iOS releases and which older lines still get
    fixes. Apple's PSTI statements give a minimum security-update period per model (five years from first
    supply in the statements reviewed); Apple has historically supported phones longer, but the latest
    iOS gets the most fixes, and older lines get only some. A phone that can't run a supported iOS is
    end-of-life.
  - **Pixel:** Google's Pixel update page lists years of OS and security updates per model, counted from
    first availability on the US Google Store (at last review: five years for Pixel 6 and 7 series, seven
    years for Pixel 8 and later). Compute the end date from that page.
  - **Samsung:** Samsung's security updates page lists which models are on monthly, quarterly, or
    biannual updates; recent flagships carry longer commitments (up to seven years for some). Models drop
    to lower tiers and then off the list over time; check the exact model and region.
  - **Other makers:** find the maker's published policy; if there is none, treat support as unknown.
  - **iPad:** the same Apple security releases page lists iPadOS releases; check the model can run a
    supported iPadOS. iPads are often kept far longer than phones and handed down, so an old iPad on an
    unsupported iPadOS is a common finding.
  - **Pixel Tablet:** support dates are on the Pixel Tablet software updates page, not the Pixel phone
    page (at last review it listed security updates until at least June 2028, and news reports in early
    2026 said Android version updates were extended to the same date; check the live page).
  - **Samsung Galaxy Tab:** tablets appear on the same Samsung security updates page by model and tier.
  - **Low-cost Android tablets:** many have no published policy and ship months behind on patches;
    treat as unknown or unsupported unless the maker documents otherwise.
- Security patch level age (Android): more than about two or three months behind the current Android
  Security Bulletin on a supported phone suggests updates aren't being installed, or the maker or carrier
  is slow. Compare with the bulletin date, not with memory.
- For any finding involving a specific vulnerability, validate per core triage (vendor bulletin, KEV);
  don't list CVEs from memory.

#### B. Updates

- Automatic updates on: iOS (Settings → General → Software Update → Automatic Updates, including the
  option for security responses or system files on recent versions; verify names); Android (system
  updates and auto-download where the maker offers it; Google Play Store auto-update for apps).
- A pending update waiting for a restart or for Wi-Fi.
- Google Play system update date recent (it updates monthly on supported phones).
- App updates: App Store and Play Store set to update automatically; apps from other sources update only
  if their source does (domain H).
- Whether an MDM defers updates on a work phone (report; don't change).

#### C. Screen lock, biometrics, and lock-screen exposure

- A passcode is set: ideally six digits or longer, or alphanumeric; not a simple pattern, a birthday, or
  a code others in the household know. Ask whether anyone else knows it; don't ask what it is.
- Biometrics (Face ID, Touch ID, fingerprint, face unlock): enrolled faces and fingerprints all belong to
  the user. Another person's enrolled fingerprint or "alternate appearance" is a finding, and a possible
  abuse indicator. On Android, note whether face unlock is a strong (class 3) biometric on this model;
  weaker face unlock can't be used for some protections.
- Auto-lock after a short time; Android "Smart Lock" or "Extend Unlock" (trusted places, devices, or
  on-body detection) that keeps the phone unlocked; Apple Watch unlock.
- Lock-screen exposure: notification previews (codes from text messages visible on the lock screen),
  Control Center or quick settings available while locked (turning off Wi-Fi or airplane mode to stop
  tracking), USB accessories while locked (iOS "Accessories" setting; Android USB protections in
  Advanced Protection or Samsung Auto Blocker), and wallet or reply features from the lock screen.
- Erase after failed attempts (iOS option) if appropriate for the household (risk with small children).
- App-level locks for sensitive apps (iOS locked or hidden apps; Android private space or Samsung Secure
  Folder), noting they share the device passcode unless configured otherwise.

#### D. Loss and theft protection

- **Find My (iPhone)** on, with Find My network and Send Last Location where offered. Find My enables
  **Activation Lock**, which stops a thief reusing the phone.
- **Find Hub (Android, formerly Find My Device)** on ("Allow device to be located"), and on Samsung phones
  **Samsung Find** (SmartThings Find) and Samsung's reactivation lock if offered. Google account
  **Factory Reset Protection** (FRP) is active when a Google Account and screen lock are set.
- **iOS Stolen Device Protection** (iOS 17.3+): on or off, and whether "Require Security Delay" is set to
  away from familiar locations or always. Apple documents that, away from familiar locations, using saved
  passwords and passkeys, erasing the phone, turning off Lost Mode, and setting up or transferring an eSIM
  need Face ID or Touch ID with no passcode fallback, and that changing the Apple Account password or
  passcode needs a one-hour security delay. It requires two-factor authentication, a passcode, Face ID or
  Touch ID, Find My, and Significant Locations. Reports indicate it is turned on by default from iOS 26.4;
  check the actual setting.
- **Tablets:** Find My (iPad) and Find Hub (Android tablets) work the same way, and Activation Lock and
  Factory Reset Protection apply. Apple documents Stolen Device Protection for iPhone; check whether the
  setting exists on the iPad's iPadOS version rather than assuming it. Android theft protection features
  depend on the device, and some (such as Theft Detection Lock) are designed around phones; check what
  the tablet offers.
- **Android theft protection** (Settings → Google → All services → Theft protection on Pixel and many
  phones; verify): **Theft Detection Lock**, **Offline Device Lock**, **Failed Authentication Lock**,
  **Remote Lock** (lock from android.com/lock with a verified phone number), and **Identity Check**
  (biometrics required outside trusted places for actions such as viewing saved passwords, changing the
  screen lock, factory reset, turning off Find Hub, adding or removing accounts, and opening Developer
  options). Google states availability depends on the device; a grayed-out or missing option means
  unsupported.
- Medical ID or emergency information shown on the lock screen: helpful, but check it doesn't reveal more
  than the user wants.
- The user knows how to locate, lock, and erase the phone from another device or browser, and how to
  reach their carrier to suspend the line. Recovery: can they sign in to their Apple Account or Google
  Account without this phone (domain E)?

#### E. Apple Account, Google Account, and Samsung account security

- **Two-factor authentication** on (Apple Account two-factor is standard for current accounts; Google
  2-Step Verification). Record the methods: passkeys and security keys are strongest; prompts on trusted
  devices next; SMS codes only as strong as the carrier account (domain F).
- **Passkeys:** where offered, passkeys for the Google Account and other key services; Apple Account
  **security keys** (physical FIDO keys) for high-risk users, noting the key-loss trade-off.
- **Recovery:** trusted phone numbers and recovery email are current and controlled only by the user;
  Apple **Recovery Contact** or **Recovery Key**, and **Legacy Contact**; Google recovery phone and email.
  An ex-partner's phone number or email as a recovery method is a finding and a safety consideration.
- **Signed-in devices:** the Apple Account device list and Google "Your devices": every entry is the user's
  current hardware. Unknown or old devices are findings; an unknown recent device is a **P0 indicator**.
- **Third-party access:** apps and services with access to the Google Account; "Sign in with Apple" apps;
  app-specific passwords no longer needed.
- **Security alerts:** Google security alerts and Apple sign-in notifications go somewhere the user reads.
- **The email account** behind each account has its own strong sign-in (resets go there).
- **Google Advanced Protection Program** (account-level, separate from Android Advanced Protection) for
  high-risk users; note its requirements and trade-offs.
- **Password manager:** passwords saved in iCloud Keychain or Apple Passwords, Google Password Manager, or a
  third-party manager are behind the device and account security above. Ask whether the user reuses
  passwords; never ask to see them.

#### F. SIM, phone number, and carrier account (SIM swap and port-out)

- **SIM PIN:** whether a SIM PIN is set (iOS: Settings → Cellular → SIM PIN; Android: SIM lock under
  security settings; verify). It stops someone moving a physical SIM into another phone. The default PIN
  comes from the carrier; the user must look it up, not guess it. Note: a SIM PIN does not stop a SIM swap
  done at the carrier.
- **Carrier account protections** (set with the carrier, by the user): an account PIN or passcode that
  isn't derived from public information; a **number lock**, port-out lock, or "SIM protection" feature
  that blocks SIM changes and number transfers until the user removes it; alerts for SIM changes and port
  requests. In the US, FCC rules adopted in 2023 require wireless carriers to authenticate customers
  securely, notify customers of SIM change and port-out requests, and offer a lock option (check the
  carrier's current implementation; some provisions had later deadlines).
- **eSIM:** eSIMs can be moved to a new phone by Quick Start or transfer, or reissued by the carrier.
  Ask how the carrier authorizes eSIM transfers and whether the account lock covers them. iOS Stolen Device
  Protection requires biometrics for eSIM setup or transfer away from familiar locations.
- **Dependence on SMS codes:** which important accounts (bank, email, Apple or Google, social) still use
  text-message codes or SMS recovery. Each is exposed to a SIM swap. Prefer passkeys or authenticator apps
  where offered.
- **Signs of a past or ongoing swap:** sudden "No service" or "SOS only" while others have signal, carrier
  messages about a SIM or eSIM change the user didn't make (a **P0 indicator**, see Respond).
- **Other numbers:** a VoIP or secondary number used for recovery (its account needs strong 2FA too).

#### G. App permissions and privileged access

- **Location, microphone, camera, contacts, photos:** review per app (iOS: Settings → Privacy & Security;
  Android: Settings → Security & privacy → Privacy → Permission manager or Privacy dashboard; verify).
  Flag "always" location, background microphone or camera access, and full photo access for apps that
  don't need them. Android and iOS show indicators when the camera or microphone is in use.
- **Android accessibility services** (Settings → Accessibility → installed apps or services): these can
  read the screen and act for the user. Anything other than known assistive tools, password managers, or
  recognized apps is a high-priority finding; it is a common route for banking malware and stalkerware.
- **Android device admin apps** (Settings → Security → Device admin apps, or similar) and **device owner**
  status: should be empty or only Find Hub and recognized work or parental apps.
- **Android notification access, usage access, "display over other apps", "install unknown apps", and
  default SMS or dialer apps:** these special app access permissions let apps read notifications (including
  codes), watch app usage, or overlay fake screens. Review each list.
- **iOS configuration profiles and MDM** (Settings → General → VPN & Device Management): any profile on a
  personal iPhone, and especially an MDM enrollment, a root certificate trust, or a profile the user
  doesn't recognize, is a finding and a possible monitoring indicator. Also check Settings → General →
  About → Certificate Trust Settings for trusted root certificates.
- **VPN apps and profiles:** a VPN can see or redirect all traffic. Each should be one the user chose
  (domain J).
- **Keyboards:** third-party keyboards with "full access" can send what is typed.
- **Unused apps:** apps not opened in months still hold permissions and accounts; Android can remove
  permissions from unused apps automatically (check it's on).

#### H. App sources, integrity, sideloading, jailbreak, and root

- **Android unknown sources:** which apps are allowed to "install unknown apps" (browsers, file managers,
  messaging apps on this list let downloaded files install software). Ideally none. Google's developer
  verification requirements, starting in some countries in late 2026 and expanding later, change how
  apps from unverified developers can be installed; check current rules.
- **Google Play Protect** on, with scanning of apps from outside Play enabled, and recent scan results
  clean. Note certification status in Play Store settings ("Device is certified"); an uncertified phone
  lacks some protections.
- **Samsung Auto Blocker** (Galaxy): on, which blocks unknown-source installs and commands over USB, with
  an optional maximum restrictions level on supported One UI versions; Samsung Knox features as offered.
- **iOS alternative app marketplaces and web distribution** (available only in some regions, such as the
  EU, Japan, and Brazil at last review): which marketplaces are installed and allowed. Apple says its
  ability to help with apps from outside the App Store is limited. Enterprise apps and developer profiles
  trusted on a personal iPhone (VPN & Device Management) and **Developer Mode** (Privacy & Security) on
  without a reason are findings.
- **Jailbreak or root indicators:** jailbreak package managers or tweak apps; an unlocked-bootloader or
  "orange state" warning at Android boot; root manager apps; banking, payment, or work apps refusing to run
  because the device fails integrity checks; Developer options and USB or wireless debugging left on.
  Ask whether the user did this deliberately. A jailbreak or root the user didn't make is a **P0
  indicator**.
- **Developer options** (Android): off when not needed; USB debugging and wireless debugging off; no
  unknown computers authorized for debugging.

#### I. High-risk hardening modes

- **Lockdown Mode (iPhone):** on or off, and whether the user is at high risk (journalists, activists,
  officials, people facing a well-resourced adversary, or recipients of an Apple threat notification).
  Apple documents that it blocks most message attachments and link previews, restricts complex web
  technologies, blocks FaceTime calls and invitations from unknown contacts, blocks configuration profiles
  and MDM enrollment, requires the phone to be unlocked to connect to accessories, and turns off 2G and 3G.
- **Android Advanced Protection** (Android 16 and later on supported phones; Settings → Security & privacy
  → Advanced Protection or the Google settings path; verify): Google documents that turning on Device
  protection keeps Play Protect on, blocks unknown-source installs, limits accessibility services to
  verified tools, turns on theft protection features and an inactivity reboot, adds USB protection,
  blocks 2G where supported, enforces Chrome and Messages protections, and offers optional intrusion
  logging. Some protections need a restart; blocking 2G can cost service where only 2G exists.
- **Android "allow 2G" toggle** (on phones that offer it) and **USB restrictions**, which can be set
  individually without a full mode.

#### J. Network, radios, and nearby sharing

- **Wi-Fi:** saved networks list (remove old open hotspots that the phone auto-joins); private Wi-Fi
  address on per network; Wi-Fi calling and hotspot passwords.
- **Personal hotspot:** strong password; off when not in use.
- **VPN:** which VPN is in use and why; a work VPN on a personal phone; Android always-on VPN and "block
  connections without VPN" if the user relies on a VPN; free or unknown VPN apps are findings.
- **Private DNS / encrypted DNS:** Android Private DNS setting (Automatic, Off, or a named provider) and
  iOS DNS settings set by profiles or apps; a provider the user didn't choose is a finding (it can see and
  redirect lookups).
- **Bluetooth:** paired devices list (unknown cars, headsets, or watches); Bluetooth can stay on, but
  remove unknown pairings.
- **AirDrop (iPhone):** set to Contacts Only or Receiving Off, not Everyone (recent iOS limits
  "Everyone" to ten minutes; verify). **NameDrop** and nearby sharing of contact details.
- **Quick Share (Android):** receiving set to Contacts or Your devices, not Everyone, except briefly.
- **Paired computers and accessories:** iPhone "Trust This Computer" pairings and Android authorized
  debugging computers; a computer that was trusted by someone else can read backups. On iOS, resetting
  Location & Privacy clears trusted computers (a change; ask first).

#### K. Sharing, tracking, and stalkerware

Ask first, gently, whether anyone else might want to know where the user goes or what they do. If the
answer is yes or uncertain, follow the safety principle before acting on anything found here.

- **iOS Safety Check** (iOS 16+, Settings → Privacy & Security → Safety Check): review sharing with
  people and apps with Manage Sharing & Access; Emergency Reset stops all sharing at once. Use it to
  review first; explain that stopping sharing may be noticed by the other person.
- **Location sharing:** Find My people sharing, Google Maps location sharing, Life360-style family apps,
  Snap Map-style social apps, Samsung or carrier family locators, and shared calendars or photos that
  reveal location.
- **Family Sharing / Google Family group:** who is in it and with what role; an ex-partner still
  organizing a family group can see purchases and, with sharing on, location.
- **Unwanted tracker alerts:** iOS and Android both alert to unknown Bluetooth trackers moving with the
  user, under a cross-platform standard for compatible trackers. Check alerts are on (iOS: Find My
  tracking notifications and location services; Android: Safety & emergency → Unknown tracker alerts,
  with a manual scan option; verify paths). A tracker alert is a safety event, not just a settings issue.
- **Stalkerware indicators:** unknown apps with generic names ("System Service", "Sync") and hidden icons;
  accessibility, device admin, notification access, or VPN permissions on unknown apps (domain G); an MDM
  profile on a personal iPhone; a jailbroken iPhone or rooted Android the user didn't make; the other
  person knowing things they couldn't otherwise know (the Coalition notes this is often the most common
  sign). Battery drain and data spikes are weak signs.
- **Account-based monitoring without any app:** someone else signed in to the user's Apple Account or
  Google Account (iCloud backups, photos, messages, and location are visible there), forwarding rules in
  email, a second phone or computer receiving the user's messages (iMessage on another Mac, "Messages for
  web" on Android), or a shared password the other person knows.
- **Connected devices:** watches, tablets, cars, and computers paired with or signed in to the phone's
  accounts.

#### L. Backups and data protection

- **iPhone:** iCloud Backup on (or a computer backup, encrypted); **Advanced Data Protection** for iCloud
  on if the user accepts the recovery trade-off (it requires a Recovery Contact or Recovery Key, and Apple
  can't help recover data without them). Apple withdrew Advanced Data Protection for new users in the UK in
  2025; check current availability for the user's region.
- **Android:** Google backup (Google One backup) on, and what it includes; Google documents that some
  backup data is end-to-end encrypted using the phone's screen lock (verify current scope). Samsung Cloud
  or Smart Switch backups on Galaxy phones.
- **Two-factor apps and passkeys:** authenticator apps that sync or back up their secrets; a phone that
  holds the only copy of 2FA codes is a lockout risk if lost.
- **Photos and messages:** what syncs where (iCloud Photos, Google Photos, message backups) and who can see
  shared albums.
- A backup that has never been restored is untested; ask whether the user has recovered from it before.

#### M. Children's and family phones and tablets

- **Parental controls:** Screen Time (iOS) with a separate Screen Time passcode the child doesn't know, or
  Google Family Link supervision; content and app-store restrictions, Ask to Buy or purchase approvals,
  and communication limits as the family intends.
- **Openness:** monitoring a child should be known to the child and suited to their age; covert
  monitoring apps sold for children are the same software as stalkerware. Recommend built-in parental
  controls over third-party monitoring apps.
- **Account ownership:** the child's Apple Account or Google Account recovery is held by the parent, and
  the child's phone isn't signed in to a parent's account (which would expose the parent's data).
- **Location and contact:** family location sharing deliberate and limited to the family; the child knows
  how to use emergency SOS.
- **Communication safety** features (for example Apple's nudity warnings for children's accounts and
  Google's sensitive content warnings) on, as the family chooses.
- **Older family members:** scam and spam call protections, a trusted-contact or recovery contact plan,
  and simplified settings, with their agreement.
- **Children's tablets:** the same controls apply on iPad (Screen Time, managed from the parent's device
  when the child's Apple Account is in the Family Sharing group) and on Android tablets (Family Link on
  the child's own supervised user, or Google Kids Space where offered, which needs a Family Link-managed
  Google Account). A child using a tablet signed in to a parent's account bypasses all of this and sees
  the parent's data (domain P).

#### N. Work and managed phones

- Management status: company-owned (supervised or fully managed) or personal with a work profile or
  account-driven enrollment. Who manages it, as shown on the phone.
- What the employer can see and do (the phone usually shows a summary); whether the user understands it.
- Separation: work data in work apps only; personal accounts not signed in to the work profile and work
  accounts not added to personal apps.
- Report any gap to the user for their IT team; don't change managed settings, remove the work profile,
  or unenroll.

#### O. Disposal, resale, trade-in, and repair

- Before selling or giving away: back up; sign out of the Apple Account (turn off Find My, which removes
  Activation Lock) or remove the Google and Samsung accounts (which removes Factory Reset Protection and
  reactivation lock); turn off Stolen Device Protection first if needed (Apple recommends this before
  selling); unpair watches; erase all content and settings; remove the phone from the Apple Account or
  Google device list; deal with the eSIM (delete or transfer) and tell the carrier; move 2FA codes and
  passkeys first.
- Old phones and tablets in a drawer still signed in: count them in domains A and E.
- Before handing a tablet down inside the family, sign out of the previous owner's account and erase it
  (or, on Android, remove the previous owner's user and accounts); a hand-me-down iPad still signed in to a
  parent's account is a domain P finding.
- Repairs: use the vendor's repair or maintenance mode where offered (for example Pixel Repair Mode or
  Samsung Maintenance Mode) so the repairer can't reach personal data; ask what the vendor documents.

#### P. Shared and multi-user tablets

- **Whose account?** Record which Apple Account or Google Account the tablet is signed in to, and who
  actually uses it. A family tablet signed in to an adult's personal account is a finding when children,
  guests, or other adults use it: they can read that adult's synced messages (iMessage, SMS forwarding,
  Messages for web), email, photos, notes, and saved passwords and passkeys, make purchases, and see or
  change location sharing. Prefer a tablet signed in to the main user's own account, or (iPad) to a
  child's own account in Family Sharing, or (Android) separate users.
- **What syncs to it:** on a shared iPad, check iCloud settings for Messages, Photos, Mail, Passwords
  and Keychain, Notes, and Find My, and turn off what the other users shouldn't see (with the account
  holder's agreement). On a shared Android tablet, check which Google services and messaging apps the
  owner's profile is signed in to.
- **Screen Time on a shared iPad:** Screen Time limits on a device signed in to an adult's account apply
  to everyone using it and are managed with a Screen Time passcode; if a child is the main user, a
  child's own Apple Account with Screen Time managed by the parent is clearer. Check the Screen Time
  passcode is set and not known to the child (don't ask what it is).
- **Android users and guest** (Pixel Tablet: Settings → System → Multiple users; Samsung: Settings →
  Accounts and backup → Users, which some recent One UI models no longer offer; verify): list the users
  and the guest; each user should have its own screen lock; the owner profile, which controls device-wide
  settings, should be locked with a passcode the other users don't know; "Add users from lock screen" off
  unless the owner wants it; guest sessions cleared after use (the guest's data is deleted on removal,
  but a guest can choose to keep activity between sessions). Note that apps installed by one user are
  available to install for others and update for everyone, and that Wi-Fi and some device settings are
  shared.
- **Restricted profiles** (offered on some Android tablets, typically Samsung; not on every model):
  restricted users can open only the apps the owner allows and can't add accounts. Samsung documents that
  the owner account needs a screen lock to create one. Check which apps are allowed.
- **Lock-screen and hub features:** on a docked or wall-mounted tablet, check what works without
  unlocking: smart-home controls (locks, alarms, garage doors, cameras), photo frames showing personal
  albums, media and voice assistant results, and notifications. Security-sensitive controls such as door
  locks and alarm disarming should require unlocking or verification (check the hub and smart-home app
  settings).
- **Organization Shared iPad** (school or work): the organization's MDM controls users, temporary
  sessions, and data deletion. Apple documents that temporary sessions need no account, delete their data
  on sign-out, and block signing in to Apple services. Report gaps to the organization; don't change it.
- **Shared tablets and abuse situations:** a tablet signed in to the user's account and kept by someone
  else (an ex-partner's home, a child's other household) can receive the user's messages and location.
  Treat it as a connected device in domain K.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**. Most changes are made by
the user on the phone, in the account website, or with the carrier; write each as clear steps described
by function, and tell the user to confirm the exact menu on their version.

### Dependency and blast-radius check (required)

- **Account recovery:** before changing passwords, 2FA, trusted numbers, or recovery options, make sure
  the user can still sign in on another trusted device and has recovery material. Changing a phone number
  or turning on Advanced Data Protection without recovery set up can lock them out permanently.
- **2FA codes on the phone:** authenticator apps, passkeys, and SMS codes on this phone protect other
  accounts; erasing, replacing, or locking the phone breaks those sign-ins until moved.
- **Watches, tablets, computers, cars:** signing out of an account or resetting network or privacy
  settings unpairs or signs out connected devices.
- **People:** stopping location sharing, removing someone from a family group, or revoking access is
  usually visible to them. In abuse situations, timing is a safety decision for the user.
- **Work:** work profiles and MDM settings belong to the employer; personal changes (such as Lockdown Mode
  or Advanced Protection) may conflict with work apps or enrollment.
- **Apps:** Advanced Protection, Lockdown Mode, Auto Blocker maximum restrictions, and blocking 2G can
  break apps, attachments, sites, or coverage; turning off root breaks the tools that need it.
- **Shared tablets:** signing a tablet out of an account removes that account's synced data, purchases
  access, and Find My or Find Hub from the tablet, and can turn off Activation Lock or Factory Reset
  Protection until another account is added; deleting an Android user deletes all of that user's apps and
  data on the tablet. Agree with every person who uses it first.
- **Carrier:** a number lock must be removed before the user can legitimately switch carriers or
  phones; make sure they know how.
- **Evidence:** in a suspected incident or abuse case, screenshots of apps, profiles, permissions, and
  account device lists should be taken before anything is removed.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Unsupported phone or OS | Replace or upgrade; meanwhile limit its role (no banking, no 2FA, no work access). | Cost; moving data and 2FA codes. |
| Old patch level on a supported phone | Turn on automatic updates; install pending updates and Play system update. | Restart; brief downtime. |
| Weak or shared passcode | Set a longer unique passcode; remove other people's enrolled biometrics. | User must learn it; others lose access. |
| Codes visible on lock screen | Hide notification previews when locked. | Slightly less convenient. |
| Find My / Find Hub off | Turn on, including offline finding where offered. | Location visible to the account holder only. |
| Stolen Device Protection or Android theft protection off | Turn on; consider "always" security delay for high-risk users; set up Identity Check and trusted places. | Some actions need biometrics or wait an hour away from familiar places. |
| Weak account 2FA or recovery | Add passkeys or security keys; remove old numbers and emails; add a Recovery Contact or Recovery Key. | Re-verification on devices; keep recovery material safe. |
| Unknown signed-in devices | Treat as incident first (Respond); then remove. | Removed devices must sign in again. |
| No carrier number lock or weak carrier PIN | Turn on number lock or port-out protection; set a strong unique carrier PIN; enable SIM change alerts. | Must unlock before legitimate transfers. |
| No SIM PIN | Set a SIM PIN after finding the carrier's default PIN. | PIN needed after restart; PUK needed if forgotten. |
| Important accounts on SMS codes | Move to passkeys or an authenticator app. | Setup time per account. |
| Over-broad app permissions | Reduce to "while using" or "ask"; remove unused apps. | Some app features stop working. |
| Unknown accessibility, device admin, notification access, profile, or VPN | Treat as possible stalkerware or malware: safety check, then Respond. | Removal may alert an abuser and destroys evidence. |
| Unknown sources allowed | Revoke "install unknown apps"; turn on Play Protect scanning or Auto Blocker. | Sideloaded apps stop updating. |
| Jailbreak or root not intended | Respond. If intended, document the accepted risk and keep sensitive apps off the phone. | Restoring stock software erases the phone. |
| High-risk user | Offer Lockdown Mode or Android Advanced Protection, plus Google Advanced Protection Program or Apple security keys. | Features and apps restricted. |
| AirDrop or Quick Share set to Everyone | Contacts only; Everyone only briefly when needed. | Strangers can't send files. |
| Unchosen Private DNS or VPN | Remove or replace with one the user chose. | Filtering or work access may change. |
| No backup, or ADP off | Turn on backups; consider ADP with recovery set up. | Storage cost; recovery responsibility. |
| Child's phone without intended controls | Configure Screen Time or Family Link openly with the child. | Ongoing conversation; age changes. |
| Family tablet signed in to an adult's account and used by others | Sign it in to its main user's own account, give a child their own Apple Account or supervised Google user, or use separate Android users; turn off syncing of Messages, Passwords, and Mail on a tablet others use. | Purchases and app ownership may need Family Sharing or reinstalling; the adult loses that data on the tablet. |
| Android tablet owner profile without its own lock, or users without locks | Set a screen lock for the owner and each user; turn off adding users from the lock screen. | Each person must remember their own lock. |
| Smart-home or sensitive controls usable from a docked or kiosk tablet's lock screen | Require unlock or verification for locks, alarms, and cameras; limit the photo frame to non-sensitive albums. | Less convenient for the household. |
| Unsupported or low-cost tablet | Replace, or limit to low-risk uses (media, reading) with no personal accounts, 2FA, or home-network admin apps. | Cost; some apps stop working. |
| Phone to be sold or recycled | Follow the disposal checklist (domain O). | Data gone after erase; make sure backup is complete. |

Renaming the phone, turning off Bluetooth permanently, or covering cameras are supplementary only. Never
recommend them as the main fix.

Group the plan: immediate containment (if any, safety first) → urgent fixes (account and carrier
takeover risks, unknown privileged apps) → high-priority hardening (theft protections, updates, app
sources) → routine maintenance (permissions, backups, nearby sharing) → optional hardening modes. Then ask
for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. The user makes the change on the
phone, in the account, or with the carrier; the agent guides and then verifies from the user's
screenshot or description. Phone specifics:

- **Before any account change:** confirm the user has another trusted device or recovery method, knows
  the account password, and has backup codes or a Recovery Key stored safely outside the phone.
- **Use a known-clean device** for account password and recovery changes if the phone itself is
  suspected.
- **Order for account hardening:** secure the email account behind the Apple or Google Account; then the
  Apple or Google Account password and 2FA (add passkeys); then recovery options; then remove unknown
  devices and third-party access; then carrier account lock and PIN. Password changes and signing out
  other devices are **C2** (they sign out other devices and may trigger security delays).
- **Removing a person's access is C2,** and in any abuse situation it waits for the user's safety plan.
- **Stolen Device Protection and theft protections** are **C1** to turn on; note that turning them off
  later may need biometrics, an hour's delay, or a trusted place.
- **Lockdown Mode and Advanced Protection** are **C2** (restart; apps and features change). Turn on with
  the user present and test their key apps afterward.
- **Advanced Data Protection** is **C2**, and losing both the Recovery Contact and Recovery Key means
  losing data; confirm recovery first.
- **SIM PIN** is **C1**, but three wrong entries lock the SIM; make sure the user has the right default
  PIN from the carrier before starting.
- **Carrier number lock** is set by the user with the carrier (C1); remind them to remove it before
  switching carriers.
- **Removing apps, profiles, device admin, or accessibility permissions** is **C2** and, if the app might
  be stalkerware or malware, is a Respond step, after evidence and safety (not routine remediation).
- **Updates** are **C2** (restart). Install with a charged battery and a backup.
- **Shared tablets:** adding an Android user or a restricted profile, or setting a user's lock, is **C1**.
  Signing a tablet out of an account or changing which account it is signed in to is **C2** (data and
  apps change; Activation Lock or FRP may change). Deleting an Android user or erasing a tablet is **C3**
  (that user's data is gone); confirm the person's data is backed up and that they agree.

After each change, follow the core "after a change" steps: have the user re-check the setting, test that
they can still unlock the phone and sign in to key accounts, confirm Find My or Find Hub shows the phone,
confirm watches and other connected devices still work, and record before and after.

### Hard stops (refer to a specialist; never automate)

- Factory resetting, erasing, or restoring a phone as security remediation while an incident, abuse case,
  or legal matter may need its evidence, or before data and 2FA codes are safe.
- Removing suspected stalkerware or monitoring, or confronting the suspected person, without the user's
  safety plan. Refer to a domestic-violence or survivor-support organization.
- Forensic analysis for suspected mercenary or government spyware: refer to a specialist helpline (see
  [incident-response.md](incident-response.md)) rather than running tools.
- Jailbreaking, rooting, bootloader unlocking or relocking, or flashing firmware.
- Removing MDM, a work profile, or an employer's security app from a work phone, or changing an
  organization's Shared iPad (it is reconfigured only by the organization through its device management;
  turning a consumer iPad into a Shared iPad needs that management and erases it, so it is not a home
  remediation).
- Bypassing Activation Lock, Factory Reset Protection, or a carrier lock on a phone, including one the
  user found or bought used (refer to the vendor or seller with proof of purchase).
- Any action on another person's phone or account without that person's consent, or helping anyone
  monitor another adult.

---

## Respond

On any P0 indicator (an unknown device signed in to the Apple or Google Account, unexpected loss of mobile
service or a SIM or eSIM change the user didn't make, an unknown MDM profile, device admin, or
accessibility app, a jailbreak or root the user didn't make, an Apple threat notification, an unknown
tracker alert, a lost or stolen phone, or signs that someone knows things only the phone could tell them),
switch to Respond immediately. Follow the core playbook plus the phone-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### PHN-001: No carrier number lock, and the email account's recovery uses text-message codes

**Confidence:** Confirmed
**Priority:** P2. A SIM swap or number port would give an attacker the email account's recovery codes,
and with it password resets for most other accounts. No sign of an attempt, so not P0.
**State:** Open
**Component:** Carrier account security settings and the email provider's recovery options; Android phone
on a supported version with a current security patch level (user-reported)
**Evidence:** User-provided screenshots, 2026-03-11: the carrier app's security page shows "Number lock:
Off" and an account PIN the user says is the last four digits of their date of birth (they did not share
the PIN). The email account's security page lists a phone number as the only recovery method and SMS as
the only second step. The phone's own settings were otherwise sound: screen lock, Find Hub, and theft
protection on.
**Expected secure state:** carrier number lock or port-out protection on, with a strong unique account
PIN and SIM change alerts (carrier and FCC guidance); important accounts use passkeys or an authenticator
app rather than SMS for sign-in and recovery (CISA mobile guidance).
**Exposure and prerequisites:** an attacker who knows the user's name and number and can pass the
carrier's identity checks, in a store, by phone, or online.
**Dependencies / blast radius:** the number lock must be turned off before the user switches carriers or
moves the number to a new phone. Changing email recovery methods requires the user to sign in and may
trigger a security notification.
**Recommended remediation:** turn on number lock in the carrier account; change the carrier PIN to a
random value stored in a password manager; turn on SIM change and port alerts; add a passkey and an
authenticator app to the email account and replace SMS recovery with a recovery email the user controls.
**Operation class:** C1 (user-made account settings; reversible).
**Approval required:** Yes.
**Verification:** carrier security page shows number lock on; email security page lists a passkey and
authenticator as second steps and no SMS-only recovery; the user can still sign in from their laptop.
**Rollback:** turn number lock off in the carrier account (needed before a legitimate transfer).

---

## Version history

- **1.0** (2026-10-30): Initial version.
- **1.1** (2026-10-31): Extended to tablets (iPad on iPadOS and Android tablets): tablet deployment
  variants (family and child iPads, organization Shared iPad, Android tablets with multiple users, guest,
  restricted profiles, Kids Space, home-hub and kiosk tablets, low-cost tablets), tablet detection hints,
  iPad, Pixel Tablet, and Galaxy Tab support-window checks, new domain P (shared and multi-user tablets),
  tablet recommendations, operation classes for user and account changes, and tablet incident-response
  steps. Folder and skill name unchanged.
