# Code Hosting and CI/CD: Respond (Incident Response)

Use with the core playbook, [incident-response.md](../../../core/incident-response.md), which always
applies. This file adds only code-hosting- and CI-specific steps.

A code-hosting incident is usually one of four things: a **leaked credential** (token, deploy key, CI
secret, or password), an **account takeover**, a **malicious change** to code, workflows, or a dependency
(including a compromised third-party action or plugin), or a **compromised runner or CI server**. The
first two are account compromises of everything the credential reaches. The third is a supply-chain
incident for everyone who built or deployed from the repository. The fourth is a host compromise, often
inside the LAN.

## Triage and containment

- **Indicators:**
  - Secret-scanning alerts, push-protection bypasses, or a provider's leaked-credential notice.
  - New tokens, SSH keys, deploy keys, OAuth apps, webhooks, collaborators, or admins nobody added.
  - Commits, tags, releases, or workflow changes nobody made; force pushes; protection rules removed;
    repository visibility changed to public.
  - Workflow runs nobody triggered, runs on unexpected branches, or jobs that contact unknown hosts.
  - A third-party action, reusable workflow, or Jenkins plugin reported compromised or whose tag moved.
  - New runners registered, or runner hosts with unexpected processes, cron jobs, or SSH keys.
  - Jenkins: new admin users, changed security realm or authorization, unfamiliar jobs, or script
    console use.
- **Revoke first, investigate in parallel.** For a leaked credential, revoke or rotate it at the
  provider as soon as the user approves, from a clean device. Waiting to "see what the attacker does"
  is not a home or small-office option.
- **Account takeover:** from a clean device, reset the password, re-register 2FA, sign out all sessions,
  and revoke every token, SSH key, and OAuth grant on the account. Then rebuild the needed ones.
- **Stop the pipeline from spreading damage.** Disable the affected workflows or pipelines, pause
  self-hosted runners (stop the service; don't wipe the host), and block deployments by requiring
  environment approval. Each step needs approval unless an emergency standing authorization names it.
- **Compromised runner or Jenkins controller:** isolate the host at the switch, VLAN, or hypervisor
  without powering it off, and treat every secret it ever handled as exposed. Follow the core playbook
  for a compromised host.
- **Compromised dependency or action:** stop builds that use it, identify every run that used the bad
  version, and treat every secret available to those runs as exposed.

## Evidence to preserve (code-hosting-specific)

- Audit logs from the forge for the incident window (organization, enterprise, or instance level),
  exported before retention expires. Security logs for affected user accounts.
- Lists of tokens, SSH keys, deploy keys, OAuth and app installations, webhooks, collaborators, and
  admins, with creation and last-use dates (metadata only).
- Workflow and pipeline run history, run logs, and artifacts for suspicious runs. Download logs before
  deleting any that leaked secrets (deleting a log containing a secret is right after the secret is
  rotated and the log is saved somewhere restricted).
- The repository as it is now, as a mirror clone (`git clone --mirror`), including suspicious refs, plus
  the reflog on any machine that has it. Don't force-push or rewrite anything yet.
- Secret-scanning and push-protection alert details, including bypass reasons.
- For runners: the runner's logs and diagnostic folder, its config and token files (as secret material),
  the process list, network connections, cron and systemd units, and the work directory.
- For Jenkins: `JENKINS_HOME` backup (secret material), the system log, build logs, the list of users
  and their API tokens (metadata), installed plugins with versions, and pending or approved script
  signatures.
- For self-managed forges: the application log, access log, database backup, and server config (secret
  material).

## Scope checks specific to code hosting and CI

- **Every system the leaked credential reaches.** For a CI secret, that's every deploy target, cloud
  account, registry, and LAN service it opens. Review each one's own logs for the window.
- **Every run that had the secret.** If a workflow, action, or runner was compromised, list every run
  in the window and every secret those runs could read, including organization-level secrets shared
  across repositories.
- **Every repository the token could write to.** Check for malicious commits, tags, and workflow changes
  in all of them, not just the one where the leak was found.
- **Downstream consumers.** Anyone who pulled packages, images, or releases built during the window.
  Notify them if you publish publicly.
- **Other machines with the same credentials.** Local credential stores, AI agent configs, MCP server
  configs, and dotfile repositories that carry the same token.
- **Forks and mirrors** that contain the leaked secret or malicious commits.
- **Runner neighbors.** What the compromised runner could reach on the LAN: NAS shares, hypervisor,
  router, Home Assistant. Check those for access from the runner's address.

## Eradication and recovery

- Rotate every secret the scope check listed, then remove the old ones at their providers.
- Remove malicious commits through new reviewed commits (revert) on protected branches. Rewrite history
  only as a separate, deliberate decision after rotation (see the hard stops in [SKILL.md](SKILL.md)).
- Rebuild compromised runners and Jenkins controllers from clean images; re-register runners with new
  tokens and, where possible, as ephemeral runners. Restore Jenkins configuration from a backup taken
  before the earliest plausible compromise, and review it before starting.
- Pin the affected action or dependency to a known-good SHA or version, or replace it.
- Rebuild and re-publish affected artifacts from known-good commits; revoke or mark bad releases.
- Before re-enabling pipelines: default token read-only, privileged triggers reviewed, branch protection
  restored, 2FA enforced, runner scope narrowed, and the initial access path closed.

## Quick checklist tailored for code hosting and CI

Start with the core quick checklist, plus:

- [ ] From a clean device, revoke the leaked token or key, or reset the taken-over account and sign out
      all sessions.
- [ ] Export audit logs and run logs before anything expires or is deleted.
- [ ] Disable affected workflows and stop (don't wipe) self-hosted runners.
- [ ] List every secret the affected runs, runners, or tokens could reach, and rotate all of them.
- [ ] Check every repository the credential could write to for new commits, tags, workflows, webhooks,
      and deploy keys.
