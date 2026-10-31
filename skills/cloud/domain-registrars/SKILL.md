---
name: domain-registrars
description: >-
  Security assessment, hardening, remediation, and incident response for domain registrar accounts and
  the domains they hold: Namecheap, GoDaddy, and other registrars (Cloudflare DNS has its own skill).
  Covers registrar account MFA and contact email security, registrar and transfer locks, registry lock,
  auto-renew and expiry, WHOIS/RDAP privacy, nameserver and DNS record review (dangling records and
  subdomain takeover), DNSSEC, CAA, API keys, and delegated access. Use when auditing a household's or
  small office's domains, before a domain expires or moves, or when a domain may have been hijacked,
  transferred away, or had its DNS changed.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "ICANN-accredited registrars for gTLDs (for example Namecheap, GoDaddy, Porkbun, Squarespace Domains, Cloudflare Registrar) and ccTLD registrars; registrar-hosted DNS (verify the live registrar dashboard and current ICANN and registry policies; menus and policies change)"
  audience: "home, work, homelab, web"
  finding_prefix: "REG"
  modes: "discover, recommend, remediate, respond"
---

# Domain Registrar Security

Act as a careful, evidence-driven DNS and domain security engineer. A domain is the root of trust for a
household or small office's email, websites, certificates, and account recovery. Whoever controls the
registrar account can change the nameservers and so redirect mail, obtain TLS certificates, pass domain
verification at cloud services, and reset passwords for every account tied to an address on the domain.
A domain that silently expires can be re-registered by someone else, who then receives that mail.
Identify, explain, prioritize, remediate (only when authorized), and verify weaknesses in the registrar
account, the domain's locks and lifecycle, and the DNS records it publishes.

## How to use this skill

This skill holds only registrar and domain guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Registrar-specific Respond steps are in [incident-response.md](incident-response.md). Vendor and policy
documentation is in [references.md](references.md). Related skills: [Cloudflare](../../edge/cloudflare/SKILL.md)
when the domain's DNS (or registration) is at Cloudflare, [productivity suites](../productivity-suites/SKILL.md)
for the mail records (MX, SPF, DKIM, DMARC), [cloud providers](../cloud-providers/SKILL.md) for the cloud
resources DNS records point to, [web servers](../../web/web-servers/SKILL.md) for the sites behind
them, and [MFA](../../identity/mfa/SKILL.md).

## Registrar-specific principles

- **The registrar account is above everything else.** Changing nameservers at the registrar overrides
  whatever the DNS host says. Assess registrar login and recovery first.
- **Watch for circular recovery.** If the registrar account's email address is on the same domain
  (`admin@` the domain), then an expired or hijacked domain also takes away the email needed to recover
  the registrar account. The account email belongs on an independent provider with strong MFA.
- **The agent never signs in and never handles secrets.** The user signs in to the registrar dashboard
  and shares screenshots (cropped or redacted: account numbers, contact details, and authorization codes
  must not appear). Never ask for the password, MFA codes, transfer authorization (EPP/auth) codes, or API
  keys. If the user uses a registrar API, they configure the key in their own environment, scoped and
  IP-restricted where the registrar allows.
- **Public DNS and registration data are fair to read.** DNS lookups and RDAP (the successor to WHOIS
  for gTLDs) are passive and need no access. Querying the user's own domains is reading. Testing whether
  a dangling record can actually be claimed (registering the bucket or app name) is a **change** with
  legal and ethical implications; never do it except as an approved remediation on the user's own
  provider account.
- **Policies come from ICANN and the registries, not only the registrar.** Transfer locks, grace and
  redemption periods, and contact-change rules depend on ICANN policy (for gTLDs), the registry (for
  example the operator of a given TLD), and ccTLD rules. These change; ICANN has approved revisions to
  the Transfer Policy whose implementation dates should be checked live. Verify the current rule for the
  specific TLD before stating timelines.
- **DNS changes are slow to undo.** TTLs and caches mean a wrong NS, DS, or MX record can break mail or
  the website for hours or days. Treat DNS and delegation changes as **C2**, and DNSSEC changes with
  extra care.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Registrar and DNS at the same company** (for example Namecheap BasicDNS, GoDaddy DNS) | NS records point to the registrar's own nameservers. | One account controls registration and every record; its security is everything. Registrar DNS features (URL forwarding, email forwarding, parking) are in scope. |
| **Registrar separate from DNS host** (for example registrar plus Cloudflare, Route 53, or another DNS host) | NS records point to a different provider. | Two accounts to secure. The registrar holds NS delegation and DS records; record review happens at the DNS host (see [Cloudflare](../../edge/cloudflare/SKILL.md) or the provider's skill). |
| **Cloudflare Registrar** | Domain registered through Cloudflare. | Registration and DNS share the Cloudflare account; use the [Cloudflare](../../edge/cloudflare/SKILL.md) skill for the account and this skill for lifecycle, locks, and record hygiene. |
| **Registrar after a migration or acquisition** | Domains moved between registrars by a business deal (for example the 2023 move of Google Domains registrations to Squarespace). | Security settings, MFA, and login methods may not carry over. Re-check account security after any registrar migration; hijackings of migrated accounts, attributed to weak account defaults after the migration, were publicly reported in 2024. |
| **Reseller or web-host-managed domain** | Domain bought through a web host or IT provider; registrar shown in RDAP differs from who the user pays. | The user may not hold the registrar account at all. Confirm who can change nameservers and how the user would get control if the provider disappears. |
| **ccTLD domain** | Country-code TLD (for example `.uk`, `.de`, `.ca`). | Registry rules for locks, privacy, transfers, and DNSSEC differ; some ccTLDs don't use RDAP or EPP auth codes. Check the registry's rules. |
| **Several domains, including parked or defensive ones** | Typo or brand domains that don't host anything. | Each needs renewal, locks, and anti-spoofing mail records; parked domains are often forgotten until they expire. |

## Detection

Hints for recognizing a registrar or DNS host from public data (used by the `full-assessment` skill).
These are vendor-documented defaults; confirm with the user.

- **RDAP or WHOIS registration data** names the sponsoring registrar, the registration and expiry dates,
  the EPP status codes (locks), and the nameservers. RDAP is queried over HTTPS; a bootstrap service such
  as `rdap.org` redirects to the right registry.
- **Nameserver patterns:** Namecheap BasicDNS uses `dns1.registrar-servers.com` and
  `dns2.registrar-servers.com`; GoDaddy uses `nsNN.domaincontrol.com`; Cloudflare uses
  `<name>.ns.cloudflare.com`; Amazon Route 53 uses `ns-NNN.awsdns-NN` names under several TLDs.
- **Registrar features visible in DNS:** parking pages, URL forwarding (an A record to the registrar's
  redirect service), and registrar email forwarding (MX records pointing at the registrar's forwarding
  hosts).
- **On devices:** a registrar's mobile app, browser bookmarks, renewal or expiry emails, and DDNS or ACME
  DNS-01 clients configured with a registrar API (configuration files naming the registrar's API host).

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles): the list of domains the user owns, and which of them they want assessed. Mark anything you
can't inspect **Not assessed**.

### Access and baseline

Start with public data, which needs no access. Then walk the user through the registrar dashboard.

Candidate read-only lookups (**vendor-documented** standard tools; `dig` and `delv` from BIND, `curl`
for RDAP; check they're installed):

```sh
curl -s https://rdap.org/domain/example.com      # registrar, status codes, dates, nameservers (JSON)
whois example.com                                # legacy; may be unavailable or limited for gTLDs
dig +short NS example.com
dig +short NS example.com @<parent-tld-server>   # delegation as the parent sees it
dig +short SOA example.com
dig +short DS example.com                        # DNSSEC delegation signer at the parent
dig +dnssec +multi DNSKEY example.com
delv example.com A                               # validates DNSSEC (reports "fully validated" or why not)
dig +short CAA example.com
dig +short MX example.com
dig +short TXT example.com
dig +short TXT _dmarc.example.com
dig +short CNAME <subdomain>.example.com         # for each known subdomain
```

Finding subdomains to review: the DNS host's zone export or record list (best), the user's own
inventory, and certificate transparency logs (for example `crt.sh` searches for the domain), which list
every name a public certificate was issued for. Don't brute-force subdomain names against the user's
nameservers without approval; it's active probing.

**Never do these during Discover:**

- Request, unlock, or display a transfer authorization code; toggle locks; or change contacts.
- Register, claim, or create the resource a dangling record points to (a bucket name, app name, or
  hosting site), even to "prove" a takeover.
- Change nameservers, DS records, or any DNS record.
- Create API keys or grant delegated access for the assessment.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Registrar account security

- **MFA:** enabled for the registrar login, preferably with a security key or passkey where supported,
  otherwise an authenticator app. SMS-only is weak (see [MFA](../../identity/mfa/SKILL.md)). Whether the
  registrar offers extra confirmation for sensitive actions (some send a code before nameserver changes,
  transfers, or contact changes).
- **Account email:** not on a domain held in this account; protected with strong MFA; not shared or
  auto-forwarded. Recovery phone current.
- **Password:** unique, in a password manager (see [password managers](../../identity/password-managers/SKILL.md)).
- **Other people with access:** delegated or shared access (GoDaddy delegate access, Namecheap domain
  sharing, or the registrar's equivalent), former web designers or IT providers, and sub-accounts. Each
  should be needed and limited.
- **Login history and notifications:** recent sign-ins the user recognizes; notifications on for logins,
  DNS changes, nameserver changes, contact changes, and transfer requests.
- **Payment method and billing contact:** current card (an expired card is a common cause of a missed
  renewal), and billing notices reaching a monitored address.

#### B. Locks and transfer protection

- **Registrar lock** (EPP status `clientTransferProhibited`) on every domain, shown in the RDAP status.
  Also `clientUpdateProhibited` and `clientDeleteProhibited` where the registrar exposes them.
- **Registry lock** (`serverTransferProhibited`, `serverUpdateProhibited`, `serverDeleteProhibited`)
  for domains whose loss would be severe. It's set at the registry and needs an out-of-band verification
  to change; not all registrars or TLDs offer it, and it may cost extra.
- Paid registrar protection add-ons (offered under various names): what they actually do (often
  additional verification for changes), and whether the user has them.
- Transfer authorization codes: whether any were recently requested (a sign of a transfer attempt).
- Whether the domain is in a post-registration or post-transfer lock period (informational).

#### C. Renewal, expiry, and ownership

- Expiry date of every domain; **auto-renew** on; payment method valid; reminders reaching a monitored
  address. ICANN's Expired Registration Recovery Policy requires registrars to send renewal reminders for
  gTLDs, but reminders sent to a dead address are no help.
- Domains expiring within 90 days: flag with priority based on what depends on them (mail and account
  recovery make it high).
- Multi-year registration for critical domains.
- **Registrant contact:** the legal owner is the user or their organization, not a former designer,
  employee, or reseller. A registrant who isn't the user is a finding: in a dispute, the registrant wins.
- Understanding of post-expiry grace and redemption periods for the TLD (they vary by registry and
  registrar, and restoring in redemption usually costs extra). Verify for each TLD.

#### D. Registration data privacy

- WHOIS/RDAP privacy or proxy service on (many registrars include it free, for example Namecheap's
  Withheld for Privacy service; GoDaddy offers its own privacy option), or redaction under the
  registry's data policy.
- What is still published: email (often a forwarding or web-form address), organization name, country.
  Personal home addresses and phone numbers should not be public.
- Contact email used for registrar verification: reachable, because ICANN rules require contact data to
  be verified, and domains can be suspended if verification emails go unanswered.

#### E. Nameservers and delegation

- NS records at the parent match the NS records the zone itself publishes, and every listed nameserver
  answers authoritatively. A lame or mismatched delegation causes outages and can be a takeover risk.
- **Dangling NS delegations:** subdomains delegated (NS records) to a DNS host where the zone no longer
  exists (for example a deleted cloud DNS zone). Anyone who can create that zone at the same provider
  may take over the subdomain. Highest-risk dangling record type.
- Custom ("vanity" or "personal") nameservers and their glue records: still pointing at addresses the
  user controls.
- The DNS host account's security (if separate from the registrar) is in scope or marked
  **Not assessed**.

#### F. DNS records and subdomain takeover

- **Inventory every record** (from the DNS host's export): A, AAAA, CNAME, MX, TXT, SRV, NS, CAA.
- **Dangling CNAMEs:** records pointing at cloud or SaaS hostnames (storage buckets, static site hosts,
  app platforms, CDN endpoints, help desks, landing-page builders) where the resource was deleted. Check
  whether the target resolves, and what it returns (an error page naming the provider's "no such
  bucket", "no such app", or "site not found" is the classic sign). Public lists of takeover-prone
  services (see references) help classify the provider.
- **Dangling A/AAAA records:** addresses from a cloud provider the user no longer holds (released
  elastic or floating IPs can be reassigned to someone else).
- **Dangling MX:** mail records pointing at a provider or host the user no longer uses.
- **Wildcard records:** what they point to, and whether they make every name resolve.
- **Stale verification TXT records** for services the user no longer uses (low risk on their own, but a
  sign of forgotten integrations).
- **Registrar URL and email forwarding:** where they send traffic and mail; forwarding to an address the
  user no longer controls exposes mail.
- Mail records (SPF, DKIM, DMARC, null MX for non-mail domains) at least present; full review in
  [productivity suites](../productivity-suites/SKILL.md).

#### G. DNSSEC and CAA

- DNSSEC: enabled at the DNS host and the matching DS record published at the registrar; `delv`
  validates. Common failures: DS left at the registrar after moving DNS hosts (breaks resolution for
  validating resolvers), or DNSSEC signed at the host but no DS published (no protection).
- Whether the DNS host supports CDS/CDNSKEY automation and the registry or registrar honors it.
- **CAA:** records present, limited to the certificate authorities the user actually uses (including any
  their CDN or DNS host uses for edge certificates), with an `iodef` contact if wanted.
- Certificate transparency: are there certificates for the domain from CAs or for names the user doesn't
  recognize? (A sign of misissuance or takeover.)

#### H. API keys and automation

- Registrar API enabled or not; API keys that exist, their age, and which systems use them (DDNS
  updaters, ACME DNS-01 clients for certificates, scripts). Namecheap requires a whitelist of client IP
  addresses for API access; GoDaddy restricts production API access by account eligibility. Check the
  current rules, and whether the key can change nameservers or contacts or only DNS records.
- Where each key is stored (password manager, secret store, or a plaintext config file); file
  permissions only, never the value.
- Unused keys and API access left enabled after a project ended.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Everything that uses the domain:** email (inbound MX and outbound sending), websites, account
  logins and recovery addresses on the domain, SSO or domain verification at cloud services, and
  certificates.
- **Automation holding registrar or DNS credentials:** DDNS clients and ACME DNS-01 clients; rotating or
  narrowing a key breaks certificate renewal or dynamic DNS.
- **DNSSEC:** a wrong or stale DS record breaks resolution for every validating resolver; order matters.
- **Removing a dangling record:** confirm nothing legitimate still serves that name (some "dead"
  records are used by a forgotten service).
- **Changing the account email:** registrar confirmations go to the new address; make sure it works and
  has MFA before switching.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No MFA on registrar | Enable MFA with a security key, passkey, or authenticator app; store backup codes offline. | Re-sign-in; keep backup factor safe. |
| Account email on the same domain | Move the account email to an independent provider with strong MFA. | Confirmation emails go to the new address. |
| Unneeded delegated access | Remove former designers, providers, or sub-accounts. | They lose access; check they don't run DNS-dependent services. |
| Registrar lock off | Turn on registrar (transfer) lock for every domain. | Must unlock before a legitimate transfer. |
| Critical domain without registry lock | Consider registry lock where offered. | Changes require an out-of-band process and may cost extra. |
| Auto-renew off or card expired | Turn on auto-renew, update payment, consider multi-year renewal. | Cost. |
| Registrant isn't the user | Change registrant to the user or organization (check change-of-registrant rules and any resulting lock). | A transfer lock may apply after the change. |
| Personal data public | Turn on privacy or proxy service. | Some ccTLDs don't allow it. |
| Dangling NS or CNAME | Delete the record (or re-create the resource in the user's own account if still needed). | Nothing, if truly unused. |
| Dangling A record to released cloud IP | Delete or update the record. | None, if unused. |
| No DNSSEC | Enable at the DNS host, then publish DS at the registrar. | Wrong DS breaks resolution; follow the order in Remediate. |
| Stale DS after a DNS move | Remove the old DS at the registrar (or replace with the new host's DS). | Validating resolvers fail until fixed; urgent. |
| No CAA | Add CAA for the CAs in use, including the CDN's. | Wrong values block certificate renewal. |
| Registrar API key broad or unused | Disable API access if unused; otherwise restrict by IP and rotate. | Automation must be updated. |
| Parked domain spoofable | SPF `-all`, DMARC `p=reject`, null MX. | None if truly unused for mail. |

Hiding the registrar, obscure subdomain names, and privacy services are supplementary only. Never
recommend them as the main fix for a weak account or missing locks.

Group the plan: immediate containment (if any) → urgent fixes (registrar MFA, circular account email,
domains about to expire, dangling NS/CNAMEs, broken DNSSEC) → high-priority hardening (locks, registrant
correctness, API keys) → routine maintenance (stale records, delegated access) → optional defense in
depth (registry lock, CAA, DNSSEC where not urgent). Then ask for approval (core: modes and
authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. The user makes each change in the
registrar or DNS host dashboard; the agent guides and verifies with public lookups. Registrar specifics:

- **Capture before change.** Export the zone (BIND-format export where the host offers one) and
  screenshot nameservers, DS records, locks, and contacts before changing them.
- **Keep a way back in.** Confirm the new account email receives mail and that MFA backup codes are
  stored before changing the account email or MFA.
- **Record changes:** lower the TTL a day ahead for planned changes to important records; change one
  record at a time; verify with `dig` against the authoritative nameserver and a public resolver.
- **Dangling records:** delete the record, then confirm the name no longer resolves. If the service is
  still needed, re-create the resource in the user's own provider account first (a remediation on the
  user's own account, not a probe).
- **DNSSEC enable:** sign the zone at the DNS host, wait for the DNSKEY to be published, add the DS at
  the registrar exactly as the host provides it, then validate with `delv`. **DNSSEC disable or DNS host
  move:** remove the DS at the registrar first, wait for the DS TTL (and the parent's caches) to expire,
  then turn off signing or move. Getting this order wrong takes the domain offline for validating
  resolvers. This is **C2**.
- **Nameserver changes are C2:** pre-create every record at the new host, compare zones, then change NS
  at the registrar.
- **Locks:** turning a lock on is **C1**; turning it off is only for an approved transfer.
- **Transfers between registrars** are a project, not a security fix: approved separately, with locks,
  DNSSEC, and auth codes handled by the user.

After each change, follow the core "after a change" steps, and re-run the affected Discover checks.

### Hard stops (refer to a specialist; never automate)

- Initiating, approving, or rejecting a domain transfer, or handling an authorization code.
- Changing the registrant (legal owner) of a domain without the user confirming the legal and transfer-
  lock consequences.
- Letting a domain lapse, deleting a domain, or disabling auto-renew on a domain still in use.
- Claiming or registering resources at third-party providers to "test" a takeover.
- Disputes over domain ownership (UDRP, registry disputes): refer to the registrar, the registry, or a
  lawyer.

---

## Respond

On any P0 indicator (nameservers or DNS records changed without the user's knowledge, a transfer
request or authorization code the user didn't initiate, unknown logins, changed account email or
contacts, mail suddenly not arriving, certificates issued for the domain by an unknown party), switch to
Respond immediately. Follow the core playbook plus the registrar-specific steps in
[incident-response.md](incident-response.md).

---

## Worked example (invented)

### REG-001: Dangling CNAME to a deleted static-site bucket, and registrar account email on the same domain

**Confidence:** Confirmed
**Priority:** P2. `files.example.com` is a CNAME to a cloud storage website endpoint whose bucket was
deleted; anyone who creates a bucket with the same name at that provider can serve content (or phishing
pages) from the user's subdomain. Separately, the registrar account email is an address on
`example.com`, so losing the domain would also lose registrar account recovery.
**State:** Open
**Component:** Registrar account and DNS zone for `example.com` (registrar-hosted DNS)
**Evidence:** Observed 2026-10-28: `dig +short CNAME files.example.com` returns a storage website
endpoint; an HTTPS request to the name returns the provider's "no such bucket" error page. The user
confirmed they deleted that bucket a year ago. Registrar dashboard screenshot (redacted) shows the
account email on `example.com` and MFA by authenticator app.
**Expected secure state:** no DNS records pointing at resources the user doesn't control; registrar
account email on an independent provider (cloud provider subdomain takeover guidance; registrar account
security guidance).
**Exposure and prerequisites:** anyone with an account at the storage provider who notices the record;
takeover-prone names are actively scanned for.
**Dependencies / blast radius:** none; no current service uses `files.example.com`.
**Recommended remediation:** delete the `files` CNAME; move the registrar account email to an
independent mailbox with strong MFA.
**Operation class:** C1 for the record deletion (the record can be re-created); C2 for the account email
change (confirmation flow).
**Approval required:** Yes.
**Verification:** `dig files.example.com` returns no CNAME at the authoritative nameserver and a public
resolver; the registrar shows the new account email, and a test notification arrives there.
**Rollback:** re-create the CNAME from the captured zone export (not recommended unless the bucket is
re-created in the user's account).

---

## Version history

- **1.0** (2026-10-31): Initial version.
