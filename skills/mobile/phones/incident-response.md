# Phones and Tablets: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only phone- and tablet-specific steps. "Phone" below also means an iPad or
Android tablet unless a step says otherwise.

Phone incidents usually fall into one of five patterns: **a lost or stolen phone**; **an account takeover**
(Apple Account, Google Account, Samsung account, or the email behind them); **a SIM swap or number port**;
**a malicious or monitoring app or profile** (including stalkerware); and, rarely, **targeted spyware**.
Identify which pattern fits before acting, because the right first step differs. In every pattern, the
user acts on their own phone and accounts; the agent guides, records, and never signs in for them.

## Triage and containment

- **Ask about safety first.** If the suspected person is a current or former partner, family member, or
  anyone who has had the phone in their hands, removing an app, stopping location sharing, changing
  passwords, or revoking access will likely be noticed and can escalate danger. The Coalition Against
  Stalkerware advises removing monitoring only when it is safe, warns that removal deletes evidence, and
  recommends a safety plan made with a survivor-support organization from a device the other person hasn't
  had access to. Give the user those resources (see [references.md](references.md)), let them decide the
  timing, and keep using a safer device for research and help-seeking. If anyone is in immediate danger,
  they should contact emergency services. Don't suggest the user confront the person.
- **Lost or stolen phone:** from another device, the user locates the phone and marks it lost (Find My
  Lost Mode on iPhone; Find Hub, android.com/lock Remote Lock, or Samsung Find on Android); calls the carrier
  to suspend the line and block SIM or eSIM changes; and, if the passcode may have been seen, changes the
  Apple Account or Google Account password from a trusted device. Erase the phone remotely only when
  recovery is unlikely or the data risk outweighs recovery (erasing may stop location tracking; a phone
  with Activation Lock or FRP still can't be reused by a thief). Don't remove the phone from the account
  until it has been erased, because removing it can drop Activation Lock. Report the theft to police if
  appropriate, and to the carrier for blocking.
- **Account takeover:** from a known-clean device, secure the recovery email first; then change the
  Apple or Google Account password, confirm 2FA uses a method the attacker can't receive, review and
  remove unknown trusted phone numbers, recovery options, and signed-in devices, and revoke unknown
  third-party access. Each is C2; the user does it. Expect Stolen Device Protection or Identity Check
  delays if changes are made away from familiar places; that's normal.
- **SIM swap or port-out** (sudden loss of service, carrier messages about a SIM or eSIM change, or reset
  codes the user didn't request): call the carrier from another phone immediately, using the number on
  the carrier's official site, report fraud, regain the number, and set a number lock and new account PIN.
  Then secure email and financial accounts, starting with those that use SMS codes, and call banks.
- **Suspected monitoring app, profile, or privileged permission:** don't uninstall it yet. Record it
  (below), complete the safety question, and decide with the user. If removal is safe and chosen, prefer
  revoking its device admin, accessibility, and other access first, then uninstalling, then checking the
  accounts it may have exposed. On iPhone, monitoring more often happens through the Apple Account,
  shared passwords, or an MDM profile than through an app; Safety Check helps review sharing.
- **Apple threat notification or suspected mercenary spyware:** Apple sends threat notifications to users
  it believes were targeted by state-sponsored or mercenary spyware. Treat it as real; turn on Lockdown
  Mode (and on Android, Advanced Protection) and update the phone; then refer the user to a specialist
  helpline such as Access Now's Digital Security Helpline. Don't run forensic tools as an amateur
  investigation, and don't erase the phone before the specialist advises, because that destroys evidence.
- **Malicious app or scam installation** (for example a fake banking app or a "support" app installed at
  a caller's request): disconnect from the network (airplane mode), call the bank from the number on the
  card, then record and remove the app, revoke its permissions, and change passwords for anything entered
  into it.
- **Shared or family tablet involved:** a tablet signed in to the user's account (at home, in another
  household, or with a child) can show the user's messages, photos, and location to whoever holds it.
  Before signing it out, find it in the account's device list and record it; in abuse situations the
  same safety-first rule applies. A lost or stolen tablet is handled like a lost phone (Find My or Find
  Hub), without the carrier steps for Wi-Fi-only models. If one user of a shared Android tablet is
  suspected of installing something, remember that the owner profile controls device-wide settings and
  other users' apps can't normally read the owner's data; check which profile the app is in.
- **Unknown tracker alert:** don't throw the tracker away immediately. Note the alert time and place, use
  the alert's details to find it and view its information (the alert may show part of the owner's
  identifier), and contact police if the user feels unsafe; the tracker may be evidence.

## Evidence to preserve (phone-specific)

Collect before removing anything, by screenshot (or a photo of the screen taken with a different device),
with the time shown. Redact before sharing with the agent; keep the originals for police or advocates.

- Apple Account devices list, trusted phone numbers, recovery contacts, and Sign in with Apple apps;
  Google "Your devices", recent security activity, third-party access, and recovery settings; Samsung
  account devices.
- Installed apps list, and the lists of accessibility services, device admin apps, notification access,
  "install unknown apps", VPNs, and (iPhone) VPN & Device Management profiles and certificate trust.
- Location sharing lists (Find My people, Google Maps sharing, family apps), Family Sharing or Family Group
  membership, and Safety Check's sharing review.
- Carrier messages and emails about SIM, eSIM, or port changes; the carrier's account activity; the time
  service was lost.
- Security alert emails and texts (new sign-ins, password resets, 2FA changes). Keep them; don't delete.
- Tracker alerts and their map history; the tracker itself.
- For specialist spyware cases: leave the phone as is; the helpline will advise on backups or captures.
- A short written log from the user: what they noticed, when, and what the other person seemed to know.
  The Coalition Against Stalkerware suggests keeping such a log.

## Scope checks specific to phones

- **The email accounts** behind the Apple, Google, and Samsung accounts, and every account that uses SMS
  codes to this number.
- **Everything synced from the phone's accounts:** iCloud or Google Photos, backups, messages on other
  devices (Mac Messages, Messages for web), passwords in iCloud Keychain or Google Password Manager, and
  passkeys. If the account was taken over, treat saved passwords as exposed.
- **Banking, payment, and wallet apps:** cards in Apple Pay, Google Wallet, or Samsung Wallet; bank and
  peer-to-peer payment apps. Ask the user to check transactions and call their banks.
- **Other devices on the same accounts:** shared and family tablets (including other Android users on
  the same tablet), laptops, watches, smart speakers, cars, and smart-home
  apps (door locks, alarms, cameras; see their skills).
- **The home network,** if the phone was compromised while on it: the Wi-Fi password is on the phone, and
  smart-home and router apps on it may hold admin sessions.
- **Children and family members** who share a Family Sharing or Family Link group with an affected
  account.
- **Work:** if the phone has work access, tell the employer's IT or security team; they handle the
  managed part.

## Eradication and recovery

- **Account takeovers** are fixed in the account: after containment, confirm only known devices,
  recovery methods, and third-party access remain, 2FA is passkey or authenticator based where possible,
  and alerts are on.
- **SIM swaps** are fixed at the carrier: number regained, number lock on, new account PIN, and the user
  knows how the carrier will notify them of future changes.
- **Malicious or monitoring apps:** after removal (when safe), run Play Protect, check the privileged
  lists again, change passwords for accounts used on the phone from a clean device, and watch for
  reinstallation. If the app had device admin, accessibility, or root, or if anything comes back, a full
  reset is the reliable fix: back up only photos and documents (not apps or settings), erase, update, and
  set up as new rather than restoring a full backup that could restore the problem.
- **Unknown MDM profile on a personal iPhone:** remove it when safe; if it can't be removed (supervised
  phone the user doesn't own), contact the seller or the organization that owns the phone.
- **Jailbreak or root not made by the user:** erase and restore stock software using the vendor's
  documented method (on iPhone, update or restore with Apple's tools; on Android, the maker's official
  firmware), then set up as new.
- **Lost or stolen phone not recovered:** confirm it has been erased (or will erase when it comes online),
  then remove it from the account, transfer the number to a new SIM or eSIM, and move 2FA and passkeys.
  Ask the carrier to block the device if the local process supports it.
- **Before closing:** the user can unlock and sign in normally; account device lists show only their
  devices; theft protections, updates, and carrier lock are on; the user has a plan to review sharing
  and signed-in devices regularly (and, in safety cases, ongoing support from an advocate).

## Quick checklist tailored for phones

Start with the core quick checklist, plus:

- [ ] Ask whether someone close to the user may be involved; if so, safety plan first, using a safer
      device, before removing anything.
- [ ] Identify the pattern: lost or stolen, account takeover, SIM swap, malicious app or profile, or
      targeted spyware.
- [ ] Lost or stolen: mark lost, call the carrier, change account password if the passcode was seen;
      don't remove the phone from the account before it's erased.
- [ ] SIM swap: call the carrier from another phone, regain the number, set number lock, secure email
      and banks.
- [ ] Screenshot account device lists, privileged apps and profiles, location sharing, and alerts
      before changes.
- [ ] Secure the recovery email first, then the Apple or Google Account, from a clean device.
- [ ] Threat notification: Lockdown Mode or Advanced Protection, update, and refer to a specialist
      helpline; don't erase first.
