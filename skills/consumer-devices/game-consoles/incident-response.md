# Game Consoles and Handhelds: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only console-specific steps.

Most console incidents are **account takeovers**: someone signs in to a PlayStation, Microsoft, Nintendo,
or Steam account, spends the wallet or the stored card, changes the email and 2-step verification to keep
the account, and uses the friends list to scam others. The usual entry is phishing, a reused password, or
a code the victim was talked into sharing. The second category is **harm to a child** through chat:
grooming, sextortion, or pressure to hand over codes or money. Treat those as safeguarding emergencies
first and security incidents second. Malware on the console itself is rare; on a gaming PC or a Steam Deck
in desktop mode it is not.

## Triage and containment

- **Indicators:** security emails about new sign-ins, password, email, or 2-step-verification changes
  nobody made; purchases, wallet spending, or gift-card redemptions nobody recognizes; the account signed
  out on the console unexpectedly; friends reporting messages or trade offers the user didn't send;
  unknown devices in the account's device list; a child reporting someone asking for codes, money,
  pictures, or a move to another app; SSH open or a `deck` password set on a Steam Deck nobody configured.
- **Child safety first.** If a child is being threatened, groomed, or extorted: stay calm with the child,
  don't delete the messages, don't pay, block the contact after evidence is saved, report through the
  platform's reporting tools, and contact local law enforcement. In the US, the NCMEC CyberTipline handles
  reports of child sexual exploitation; other countries have equivalent hotlines. This is not an agent
  task to handle alone.
- **Secure the account, from a clean device:** use the platform's website (not a link from an email or
  message) to change the password, sign out all devices, check and restore the account email and phone,
  and re-enable 2-step verification. Steam offers "deauthorize all other devices". If the attacker already
  changed the email or second factor, go straight to the platform's official account-recovery support;
  ignore anyone else offering to recover it.
- **Stop the money:** remove or lock the stored payment method; contact the card issuer for unauthorized
  charges; contact the platform's support for fraudulent purchases (platforms may restrict an account
  after a chargeback, so ask the platform first where possible).
- **Secure the email account** that receives the platform's reset emails; if it was taken over, it comes
  first.
- **Steam Deck / gaming PC:** if a device may be compromised, disconnect it from the network and keep it
  powered for evidence.

## Evidence to preserve (console-specific)

- Screenshots or forwarded copies of the platform's security emails (new sign-in, password change, email
  change), with the times.
- Purchase history and wallet transactions from the platform's website.
- The account's device and session lists before signing them out.
- Messages, friend requests, and profile names of the scammer or contact, captured before blocking;
  for child-safety cases, don't forward explicit material; tell law enforcement it exists.
- Phishing pages, QR codes, or messages that led to the takeover (URLs, screenshots).
- Router evidence: UPnP mappings and port forwards to the console, and SSH connection logs for a Steam
  Deck.
- On a Steam Deck: `journalctl` output for `sshd` and recent `sudo` use (the user can export it; refer to
  the [linux](../../operating-systems/linux/SKILL.md) skill).

## Scope checks specific to consoles

- **Every account using the same password**, especially the account email; gaming accounts are often the
  first target of a reused-password attack.
- **The Microsoft account** behind an Xbox also signs in Windows, OneDrive, and Outlook; check those.
- **Linked accounts and services:** game publishers' accounts, Discord, streaming services, and payment
  services (for example PayPal) linked to the platform account.
- **Friends and family members** who may have received scam messages from the account; warn them.
- **Other consoles in the house** with the same account as primary console, and other children's accounts
  in the same family group (an attacker with the parent's account can change the children's settings).
- **Gaming PCs** where cheats, mods, or "free" downloads were installed: treat as a possible malware
  infection and use the [windows](../../operating-systems/windows/SKILL.md) skill.

## Eradication and recovery

- Account: new unique password, 2-step verification with an authenticator app or passkey, new backup
  codes, recovery options checked, all other sessions signed out, unknown linked apps removed.
- Family settings re-checked: the attacker may have relaxed children's limits or added themselves to the
  family group.
- Purchase protection turned on before the stored card is re-added (or keep using gift cards).
- Steam Deck: if SSH or a password was set by someone else, or unknown packages were installed, back up
  saves (Steam Cloud covers most games) and reimage with Valve's official recovery image.
- Consoles: a factory reset is rarely needed for an account takeover; sign out and back in after the
  account is secured. Reset only if the console itself behaves unexpectedly, and only after evidence is
  saved.
- Report fraud to the platform and, for significant losses, to the core references' reporting channels
  (for example the FBI's IC3 in the US).

## Quick checklist tailored for game consoles

Start with the core quick checklist, plus:

- [ ] If a child is at risk, prioritize safeguarding and reporting; save evidence; don't pay.
- [ ] From a clean device, use the platform's own website: new password, sign out everywhere, restore
      email and 2-step verification.
- [ ] Secure the email account behind the gaming account.
- [ ] Lock or remove stored payment methods; contact the card issuer and the platform about charges.
- [ ] Check family settings and children's accounts for changes.
- [ ] Warn friends about scam messages sent from the account.
- [ ] Check other accounts that shared the password.
