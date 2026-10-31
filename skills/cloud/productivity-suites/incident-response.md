# Microsoft 365 and Google Workspace: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only suite-specific steps for a compromised mailbox, admin account, or tenant
(business email compromise, illicit app consent, or an unknown admin).

## Triage and containment

- **Work from a clean device.** If the user's computer may be infected, sign in to the admin console from
  another device. Malware that stole a session token can steal the next one too.
- **Contain the account in this order**, so the attacker can't keep a foothold while you work:
  1. Reset the password (from the admin console, not the user's possibly compromised session).
  2. **Revoke sessions and refresh tokens.** Microsoft: "Revoke sessions" in the Entra admin center or
     `Revoke-MgUserSignInSession`. Google: reset the user's sign-in cookies in the Admin console. A
     password reset alone doesn't end existing sessions everywhere.
  3. Review and remove MFA methods the user didn't register (attackers add their own phone or
     authenticator), then require re-registration.
  4. Block sign-in temporarily if the account is actively abused and the user can live without it.
- **Stop mail leaving.** Disable malicious inbox rules and mailbox forwarding *after* exporting them (see
  evidence below). Set the tenant external forwarding policy to Off. Check for transport or routing rules
  the attacker may have added with an admin account.
- **Revoke malicious app grants.** Microsoft: remove the OAuth2 permission grant and disable the
  enterprise application (record its app ID first). Google: block the app in API controls and remove the
  user's token. App access survives a password reset unless revoked.
- **Unknown admin or tenant-wide changes:** remove the unknown admin's roles and block sign-in, then check
  every change it made in the audit log. Check partner relationships and federation or domain settings
  (an attacker may add a federated domain or change authentication settings to keep access).
- **Money at risk:** if fraudulent payment instructions were sent or received, tell the user to call
  their bank immediately (a known number, not one from the email) to try to recall or freeze the
  transfer. Speed matters more than evidence here. File a report with the authorities listed in the core
  playbook.

## Evidence to preserve (suite-specific)

Export before you remove anything; deletion destroys evidence.

- Inbox rules, mailbox forwarding, delegation, and transport rules (PowerShell output or screenshots),
  with timestamps.
- **Unified audit log** (Microsoft Purview audit search) or **Admin console audit and investigation**
  (Google): sign-ins, rule creation, `MailItemsAccessed` where the plan records it, consent grants, role
  changes, and admin actions for the affected period. Note the plan's retention period and export
  before it expires.
- Entra sign-in logs (IP, location, client app, user agent, authentication method) or Google login audit.
- The list of OAuth grants and service principals, with consent time and who consented.
- MFA methods registered on the account, with registration time.
- Sent Items and Deleted Items metadata (recipients, subjects, times) for the attacker's window; message
  content only with the mailbox owner's consent and within the incident scope.
- Any phishing message that started the incident, as an attachment (headers intact).

## Scope checks specific to the suite

- **Other mailboxes:** did the same sign-in IPs or user agents touch other accounts? Search the audit log
  for them. Check every mailbox for new rules created in the attacker's window.
- **Who received attacker mail:** customers, suppliers, family, or colleagues who may have received
  phishing or invoice fraud from the compromised mailbox. Tell them through a channel other than email.
- **Files:** OneDrive, SharePoint, or Drive files accessed, downloaded, or shared externally during the
  window (see [cloud storage](../cloud-storage/SKILL.md)).
- **Password resets triggered for other services:** the mailbox receives reset links for banks, the
  registrar, cloud providers, and social accounts. Check those accounts' recent activity and resets.
- **The domain:** whether DNS or registrar settings changed (MX, SPF, new verification records). See
  [domain registrars](../domain-registrars/SKILL.md).
- **Consumer accounts:** for a family's Microsoft or Google accounts, check recent activity pages,
  devices signed in, recovery info changes, and family group membership.

## Eradication and recovery

- Confirm all attacker artifacts are gone: rules, forwarding, delegation, app grants, MFA methods,
  admin role assignments, transport rules, federation settings, and devices registered during the
  window.
- Close the entry path: MFA for every user (security defaults, Conditional Access, or enforced 2-Step
  Verification), legacy authentication blocked, user consent restricted.
- Restore deleted mail from the recoverable items or trash within the suite's retention window if the
  attacker deleted messages.
- Watch for re-entry for at least 30 days: alerts on new rules, forwarding, app grants, and sign-ins from
  new locations.

## Quick checklist tailored for the suite

When the user says "I think my email has been hacked," start with the core quick checklist, plus:

- [ ] From a clean device: reset the password, revoke sessions, and remove unknown MFA methods.
- [ ] Export, then disable, inbox rules and forwarding that send mail outside or delete it.
- [ ] Revoke app grants nobody recognizes.
- [ ] If money moved or invoices were sent, call the bank now and warn recipients by phone.
- [ ] Export audit and sign-in logs for the period before retention expires.
- [ ] Check admin roles for unknown members and the audit log for admin changes.
