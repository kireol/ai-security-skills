# Domain Registrars: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only registrar-specific steps for a hijacked registrar account, an unauthorized
transfer, changed DNS, an expired domain, or a subdomain takeover.

## Triage and containment

- **Act fast and use the phone.** Domain hijacks are usually reversible only in the first hours or days,
  before the attacker transfers the domain onward. Contact the registrar's security or abuse team by phone
  or their documented urgent channel (see [references.md](references.md)), from a clean device, and keep
  a case number.
- **Registrar account compromised (changed email, MFA, nameservers, or contacts):**
  1. Try to sign in from a clean device; if possible, reset the password, re-register MFA, and remove
     unknown delegated users and API keys.
  2. Restore the nameservers to the known-good values (from the user's records or a captured zone
     export) and re-enable locks.
  3. If you can't sign in, the registrar's account recovery and security team are the only path. Have
     proof of ownership ready (invoices, payment records, prior correspondence).
- **Domain transferred away:** contact the losing registrar (the original one) immediately; it can open
  a transfer dispute with the gaining registrar. ICANN's Transfer Dispute Resolution Policy and the
  registry's procedures apply for gTLDs; ccTLDs have their own. Don't contact the attacker.
- **DNS records changed at the DNS host:** restore records from the export, secure the DNS host account,
  and lower nothing else until the account is secured. See [Cloudflare](../../edge/cloudflare/SKILL.md)
  if the zone is at Cloudflare.
- **Domain expired:** renew immediately if still in the registrar's grace period. If in redemption, the
  registrar can usually restore it for a fee. If it has been deleted and re-registered by someone else,
  recovery is a legal matter.
- **Subdomain takeover:** delete the dangling record at the DNS host (this ends the takeover for new
  lookups once caches expire), then report the hostile content to the hosting provider.
- **Protect what depends on the domain while it's out of your control:** tell users not to trust email
  from the domain; switch account recovery addresses for important accounts (bank, cloud, registrar) away
  from the domain; warn customers or family through another channel.

## Evidence to preserve (registrar-specific)

- RDAP output for the domain over time (status codes, registrar, nameservers, dates), saved with
  timestamps; DNS answers (`dig` output) for NS, MX, A, and DS records.
- Registrar notification emails: login alerts, nameserver change notices, transfer requests, and
  authorization code requests, with full headers.
- Registrar account activity or audit log, and the DNS host's audit log.
- Certificate transparency entries (for example from `crt.sh`) for certificates issued during the
  incident; an attacker controlling DNS can obtain valid certificates.
- The prior zone export and the user's records of correct nameservers and DS values.
- Screenshots of hostile content served on a taken-over subdomain.

## Scope checks specific to domains

- **Email:** was MX changed? If so, the attacker may have received password resets and messages; check
  every account whose recovery address is on the domain (see
  [productivity suites](../productivity-suites/SKILL.md)).
- **Certificates:** revoke certificates issued to the attacker (contact the issuing CA with evidence).
- **Domain verification at services:** cloud and SaaS services verified by DNS TXT records; an attacker
  with DNS could have verified the domain in their own tenant. Check the suite and cloud providers.
- **Other domains in the same registrar account,** and other registrar accounts using the same email or
  password.
- **The account email's mailbox:** how the attacker got into the registrar account often starts there.

## Eradication and recovery

- Once control is regained: new password, phishing-resistant MFA, account email on an independent
  provider, unknown users and API keys removed, registrar lock on, registry lock considered.
- Restore DNS from the known-good export; verify NS, MX, DS, and CAA at the authoritative servers and a
  public resolver.
- DNSSEC: if the attacker changed DS or DNSKEY records, restore the correct DS at the registrar (or
  remove it until the zone is re-signed) and validate with `delv`.
- Rotate credentials for anything that used the domain for login or recovery during the incident.
- Monitor RDAP status, DNS answers, and certificate transparency for the domain for several weeks.

## Quick checklist tailored for domains

When the user says "my website and email stopped working" or "my domain was stolen," start with the core
quick checklist, plus:

- [ ] Save RDAP and `dig` output now (registrar, status, nameservers, MX, DS).
- [ ] Call the registrar's security or abuse line from a clean device; get a case number.
- [ ] If signed in: restore nameservers, re-enable locks, remove unknown users and keys, fix MFA and email.
- [ ] Move account recovery for important services off the affected domain.
- [ ] Check certificate transparency for certificates issued to the attacker.
- [ ] Warn people who rely on email from the domain, by another channel.
