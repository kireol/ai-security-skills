# Cloud Provider Accounts: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only cloud-provider-specific steps for a leaked key, a compromised account, or
abuse such as crypto-mining.

## Triage and containment

- **Speed matters more here than almost anywhere.** Automated scanners find keys in public code within
  minutes, and mining fleets start in every region at once. Contain first; investigate second.
- **Leaked or misused key:**
  1. **Deactivate** the key (AWS access key "Make inactive"; disable the Google service account key;
     revoke the DigitalOcean or Linode token; remove the Azure client secret). Deactivating keeps the key
     ID for investigation; delete it only after the investigation.
  2. If the key's principal has high privileges, also attach a deny-all policy or remove its role
     bindings temporarily, because the attacker may already have created other credentials.
  3. Don't delete the IAM user or service account yet; its history is evidence.
- **Compromised console account (root, owner, admin):** from a clean device, reset the password,
  re-register MFA (remove factors the user didn't add), and sign out other sessions. If the root or owner
  account is lost, use the provider's account recovery or support process immediately. Each provider
  documents a support or abuse channel for compromised accounts; find it on the provider's own support
  site (AWS and Google Cloud guidance is linked in [references.md](references.md)).
- **Look for attacker persistence before you think you're done:** new IAM users, access keys, roles and
  trust policies, federated identity providers, service account keys, Azure app registrations and
  secrets, team members or invitations, API tokens, SSH keys added to instances or project metadata,
  Lambda or Cloud Functions, scheduled jobs, and StackScripts.
- **Stop the spending:** stop (don't terminate yet) unknown instances in **every region**; snapshot one
  for evidence if the user wants forensic help. Scale down unknown Kubernetes node pools and
  instance groups that would re-create instances. Terminate only after evidence is captured.
- **Public data exposure:** make the bucket, snapshot, or image private right away (reversible), after
  recording its current policy as evidence.
- **Contact the provider early.** Open a support or abuse case: providers can help identify attacker
  activity and often have a process to review charges caused by compromise. Don't assume they will
  waive them.

## Evidence to preserve (cloud-provider-specific)

- **AWS:** CloudTrail event history (90 days) for every region, exported; any trail logs in S3;
  GuardDuty findings; the credential report; IAM Access Analyzer findings; billing by service and region;
  the support case from AWS about an exposed key, and the attached quarantine policy.
- **Azure:** Activity log for each subscription, Entra sign-in and audit logs, Defender for Cloud alerts,
  cost analysis by resource.
- **Google Cloud:** Admin Activity audit logs (and Data Access logs where enabled) for each project,
  IAM policy history, service account key list with creation times, billing reports.
- **DigitalOcean:** team security history and activity, Droplet and token lists. **Linode:** account
  events, login history, token list.
- Lists of every resource in every region, with creation time and creator, taken before cleanup.
- Where the key leaked from (repository and commit, file, chat, screenshot) and when.

## Scope checks specific to cloud accounts

- **Every region and every project or subscription,** not just the default.
- **What the leaked principal could do:** its policies and any roles it could assume; data in buckets,
  databases, and secrets managers it could read (assume read if it was allowed).
- **Secrets stored in the account** (secrets managers, parameter stores, instance user data, environment
  variables of functions or apps) that the attacker could read; rotate them at the systems they belong to.
- **Other accounts sharing the same root email, password, or device,** and the developer's other tokens
  (code hosting, package registries, CI/CD) if the leak came from a compromised workstation.
- **Outbound abuse:** whether instances were used to attack others, send spam, or host phishing; the
  provider may have already received abuse reports.

## Eradication and recovery

- Remove every attacker-created resource and credential found above, then delete the leaked key and
  any credentials the attacker could have read.
- Rebuild instances the attacker touched from known-good images; don't clean them in place.
- Rewrite repository history only after rotation, and remember forks and caches may keep the old commit.
- Close the entry path: secret scanning and push protection on repositories, short-lived credentials,
  least-privilege keys, root MFA, and budgets with alerts.
- Watch billing and threat detection daily for at least two weeks.

## Quick checklist tailored for cloud accounts

When the user says "I got a huge cloud bill" or "I pushed my keys to GitHub," start with the core quick
checklist, plus:

- [ ] Deactivate the key or token now (from the console, on a clean device).
- [ ] List and stop unknown instances in every region; check for new users, keys, roles, and tokens.
- [ ] Export the audit logs (CloudTrail, Activity log, Cloud Audit Logs, account events).
- [ ] Open a support or abuse case with the provider.
- [ ] Rotate every secret the leaked principal could read.
- [ ] Add a budget alert and secret scanning before you go back to normal work.
