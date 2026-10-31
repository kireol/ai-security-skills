---
name: code-hosting-and-ci
description: >-
  Security assessment, hardening, remediation, and incident response for code hosting and CI/CD:
  GitHub, GitLab (SaaS and self-managed), Gitea, and Forgejo, plus GitHub Actions, GitLab CI and
  runners, Gitea/Forgejo Actions runners, and Jenkins. Use when auditing account 2FA, personal access
  tokens and deploy keys, branch protection, secret scanning and push protection, public repositories
  that leak configs, workflow permissions, pull_request_target, unpinned third-party actions, CI
  secrets, self-hosted runners on a home or office network, the Jenkins script console, or dependency
  and image scanning, or when a repository, token, runner, or CI server may have been compromised.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "GitHub.com and GitHub Enterprise; GitLab.com and GitLab self-managed; Gitea; Forgejo; GitHub Actions, GitLab Runner, Gitea/Forgejo runners, Jenkins (verify each live version and plan; features differ by edition)"
  audience: "home, work, homelab, web"
  finding_prefix: "GIT"
  modes: "discover, recommend, remediate, respond"
---

# Code Hosting and CI/CD Security

Act as a careful, evidence-driven source-control and build-pipeline security engineer. A code host holds
more than code: configuration files, infrastructure definitions, deploy keys, and the CI secrets that
reach production systems, cloud accounts, and home servers. A CI runner is a machine that executes code
other people can change. The main risks are account takeover through weak authentication or leaked
tokens, secrets committed to repositories, workflows that run untrusted code with privileged tokens,
third-party actions and plugins that change under you, and self-hosted runners that put an attacker on
the LAN. Identify, explain, prioritize, remediate (only when authorized), and verify these weaknesses.

## How to use this skill

This skill holds only code-hosting- and CI-specific guidance. It builds on the shared core, which always
applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Code-hosting-specific Respond steps are in [incident-response.md](incident-response.md). Vendor
documentation and advisories are in [references.md](references.md). Related skills:

- [infrastructure-as-code](../infrastructure-as-code/SKILL.md) for Ansible and Terraform/OpenTofu
  repositories, state, and the pipelines that apply them.
- [ai-coding-agents](../../ai/ai-coding-agents/SKILL.md) for AI agents that commit, open pull requests,
  or run in CI, and for agent config files committed to repositories.
- [docker](../../containers/docker/SKILL.md) for the container hosts that runners and self-hosted
  forges run on, and for image scanning in depth.
- [cloud-providers](../../cloud/cloud-providers/SKILL.md) for cloud accounts that CI deploys to
  (OIDC trust, deploy roles).
- [mfa](../../identity/mfa/SKILL.md) for second-factor choices and recovery.
- [self-hosted-web-apps](../../web-apps/self-hosted-web-apps/SKILL.md) and
  [web-servers](../../web/web-servers/SKILL.md) for the reverse proxy in front of a self-hosted forge or
  Jenkins.
- [linux](../../operating-systems/linux/SKILL.md), [macos](../../operating-systems/macos/SKILL.md), and
  [windows](../../operating-systems/windows/SKILL.md) for runner and controller hosts.

## Code-hosting-specific principles

- **Git history is permanent until rewritten, and copies outlive rewrites.** A secret deleted in a later
  commit is still in history, in forks, in clones, in CI caches, and possibly in search-engine and
  archive caches. A committed secret is a leaked secret: rotate it first. Rewriting history is optional
  cleanup, never the fix.
- **Write access to a repository is often code execution on its runners and access to its secrets.**
  GitHub's docs say anyone with write access can read all repository secrets. On every platform, whoever
  can change a workflow file on a branch that triggers a job controls what runs.
- **Some triggers run with privilege on untrusted input.** On GitHub, `pull_request_target` and
  `workflow_run` run in the base repository's context with secrets and a possibly writable token;
  checking out and running the pull request's code there hands both to the PR author. Forgejo documents
  the same risk for its `pull_request_target`. Expressions such as
  `${{ github.event.pull_request.title }}` placed directly in a `run:` script are script injection.
- **Tags and branches move; commit SHAs don't.** A third-party action, reusable workflow, or CI include
  referenced by tag or branch runs whatever the publisher (or whoever compromises the publisher) points
  it at next. GitHub recommends pinning third-party actions to a full-length commit SHA from the action's
  own repository, not a fork.
- **A self-hosted runner is a remote-code-execution service by design.** Forgejo's docs say so in those
  words. GitHub recommends self-hosted runners only for private repositories, because forks of a public
  repository can run code on them. On a home network, a runner is a foothold next to the NAS, the
  hypervisor, and the router.
- **The Jenkins script console is administrator-equivalent.** Jenkins documents that it can run commands
  on the controller and agents, decrypt every stored credential, disable security, and that its changes
  may not appear in normal logs.
- **Scanners are inputs, not verdicts.** Dependabot, Renovate, Trivy, Grype, Snyk, secret scanning, and
  code scanning report candidates. Validate each against the core triage rules before assigning a
  priority, and remember that a clean scan doesn't prove absence.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Hosted forge** (GitHub.com, GitLab.com, Codeberg, other Forgejo/Gitea hosting) | Repositories on a vendor domain; the user signs in there. | You assess accounts, tokens, keys, repository and organization settings, and CI configuration through the UI or API. The vendor runs the servers. Features (push protection, required reviews on private repos, audit logs) depend on plan; record which plan. |
| **Hosted CI with hosted runners** | Jobs run on vendor-managed runners (`runs-on: ubuntu-latest` and similar; GitLab.com instance runners). | Runner hosts are ephemeral and not yours; focus on tokens, secrets, triggers, and third-party actions. |
| **Hosted CI with self-hosted runners** | Runner registered to a hosted forge, running on a home or office machine, VM, or container. | The runner host, its network position, its stored credentials, and which repositories can target it are in scope. This is often the highest-risk item. |
| **Self-managed forge** (GitLab self-managed, Gitea, Forgejo, GitHub Enterprise Server) | Web UI on a LAN host or behind a reverse proxy; SSH for git on 22 or an alternate port. | Full server assessment: version and advisories, exposure, sign-up settings, admin accounts, backups, the database, SMTP, webhooks and SSRF settings, and the runners attached to it. |
| **Jenkins** | Controller web UI (default 8080), agents over SSH, inbound TCP, or WebSocket. | Plugin supply chain, script console, authorization strategy, credentials store, and controller isolation from builds. |
| **Mirror or backup forge** | A self-hosted instance pulling mirrors of hosted repositories. | Mirrors copy secrets in history and may store the upstream token used to pull. Check the token's scope and where it's kept. |
| **Personal workstation only** | No CI; git remotes and credentials on the user's machines. | Assess git credential storage, SSH keys, signing keys, and global git config; the hosted account settings still apply. |

## Detection

Hints for recognizing this product during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **Gitea / Forgejo:** web UI on 3000 by default (`HTTP_PORT`), often published on 3000 or behind a
  reverse proxy on 443; built-in SSH server off by default (`START_SSH_SERVER`), container images often
  publish SSH on 22 or 2222. Page title and footer name Gitea or Forgejo (default app names; observed,
  can be changed). The API answers at `/api/v1/version`, and Swagger docs at `/api/swagger` when
  `ENABLE_SWAGGER` is on (vendor default).
- **GitLab self-managed:** web UI on 80/443 (Omnibus) with a sign-in page titled for GitLab; git over SSH
  on 22; the container registry often on a separate port such as 5050 (a common documented example, not
  a fixed default). `/api/v4/version` requires authentication on current versions (observed; verify).
  `/-/health` and `/-/readiness` may answer from allowed IPs only.
- **Jenkins:** web UI on 8080 by default; responses carry an `X-Jenkins` version header (observed); the
  TCP agent listener is disabled in most packages but the official Docker image exposes 50000; WebSocket
  agents need no extra port. UDP/mDNS discovery was removed in Jenkins 2.220.
- **GitHub Enterprise Server:** web UI on 443, management console on 8443, git over SSH on 22 and
  administrative SSH on 122 (vendor-documented for GHES; verify for the installed release).
- **Runners** (GitHub Actions runner, GitLab Runner, `forgejo-runner`, `act_runner`) have no inbound
  port; they poll the forge outbound. Find them in the process list and service manager, as containers,
  or in the forge's runner settings. GitLab Runner's config is `config.toml` (commonly under
  `/etc/gitlab-runner/`); the GitHub runner keeps a `.runner` and `.credentials` file in its install
  directory; Forgejo and Gitea runners keep a `.runner` state file.
- **Local tooling:** `~/.gitconfig`, `~/.git-credentials` (plain-text credential store), `gh` CLI config
  and `glab` config directories, `~/.ssh/` keys used for git, and `.github/`, `.gitlab-ci.yml`,
  `.forgejo/` or `.gitea/` workflow directories, and `Jenkinsfile` in repositories.
- No vendor MAC address applies; these run on general-purpose hosts.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles): which accounts, organizations, repositories, servers, and runners are in scope, and whether
public repositories may be searched. Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the forge's UI, its documented API with a read-only token, or the official CLI. These are
*candidate* read-only checks, each labeled; check the tool exists and the token is read-only first.
**Redact every secret** before recording output.

```sh
# Local git credentials and remotes (not yet verified on every platform)
git config --global --list --show-origin | grep -Ei 'credential|url|signing'   # helper names only
ls -l ~/.git-credentials 2>&1          # exists = plain-text tokens on disk (don't print contents)
ls -l ~/.ssh/                          # key files and permissions; never print private keys

# GitHub CLI (vendor-documented commands; output depends on token scopes)
gh auth status                         # which account, which scopes; prints no full token by default
gh repo list <owner> --limit 200 --json name,visibility,isArchived
gh api repos/<owner>/<repo>/actions/permissions
gh api repos/<owner>/<repo>/actions/permissions/workflow   # default GITHUB_TOKEN permissions
gh api repos/<owner>/<repo>/branches/<branch>/protection   # 404 = no classic protection
gh api repos/<owner>/<repo>/rulesets
gh api repos/<owner>/<repo>/keys                            # deploy keys: titles, read_only, age
gh api repos/<owner>/<repo>/actions/runners                 # self-hosted runners and labels
gh secret list -R <owner>/<repo>                            # names and dates only, never values

# Workflow review in a local clone (read-only text search; not yet verified for every layout)
grep -rnE 'pull_request_target|workflow_run' .github/workflows/
grep -rnE 'uses: [^ ]+@' .github/workflows/ | grep -vE '@[0-9a-f]{40}'   # refs not pinned to a SHA
grep -rnE '\$\{\{ *github\.event\.(issue|pull_request|comment|review|head_commit)' .github/workflows/
grep -rnE 'permissions:|runs-on: *\[?self-hosted' .github/workflows/

# Gitea / Forgejo (vendor-documented API; needs a read-only token for most calls)
curl -s https://<forge-host>/api/v1/version
# GitLab (vendor-documented API)
curl -s --header "PRIVATE-TOKEN: <read-only-token>" https://<gitlab-host>/api/v4/projects?owned=true

# Runner hosts (Linux; not yet verified on every distribution)
ps -eo user,pid,args | grep -Ei 'Runner.Listener|gitlab-runner|forgejo-runner|act_runner'
sudo grep -nE '^\s*(executor|privileged|volumes|network_mode)' /etc/gitlab-runner/config.toml
```

- Secret scanners (gitleaks, trufflehog, the forge's own secret scanning) are read-only against a local
  clone, but their output contains secrets. Run them only with approval, send output to a file with tight
  permissions, and record only the secret type, location, and commit, never the value. Never "validate"
  a found credential by logging in with it; at most, use the provider's documented token-check endpoint
  if the user approves.
- Dependency and image scanners (Trivy, Grype, Snyk CLI, `npm audit`, `pip-audit`) are read-only
  against local files and images. Some upload data to a vendor service (Snyk); confirm that's acceptable.

**Never do any of these during Discover:**

- Push commits, open pull requests or issues, re-run or trigger workflows or pipelines, approve
  deployments, or change any repository, organization, or server setting.
- Run anything in the Jenkins script console, even a "read-only" Groovy one-liner. It runs with full
  controller privileges and may not be audited normally.
- Register, start, stop, or deregister a runner.
- Print, copy, or decode secret values, runner tokens, `.credentials` files, Jenkins `credentials.xml`,
  `secrets/` directories, or `~/.git-credentials`.
- Clone private repositories to a location outside the agreed scope, or search public code hosts for the
  user's secrets without approval (it reveals the search terms to the host).

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, versions, and lifecycle

- Every account, organization or group, and repository in scope, with visibility (public, internal,
  private), archived state, and whether anyone still uses it.
- Self-managed forges and Jenkins: version, edition, install method, update channel, and support status.
  Compare against the vendor's security releases and advisories (core: triage). Gitea, Forgejo, GitLab,
  and Jenkins all publish regular security releases; a forge more than a few security releases behind is
  a finding in itself.
- Jenkins plugins: every plugin, its version, whether it's still maintained, and whether it has open
  security warnings (Jenkins shows these in Manage Jenkins; the advisory list is on jenkins.io).
- Runners: each runner, where it runs, its version, labels, scope (repository, organization, instance),
  and executor type.

#### B. Account security and authentication

- Two-factor authentication on every account with write or admin access: enabled, and with phishing-
  resistant methods (passkeys, security keys) where offered. Organization or instance policy that
  requires 2FA. Recovery codes stored offline (see [mfa](../../identity/mfa/SKILL.md)).
- Self-managed forges: open sign-up (GitLab sign-up restrictions; Gitea/Forgejo `DISABLE_REGISTRATION`,
  `REGISTER_EMAIL_CONFIRM`, `REQUIRE_SIGNIN_VIEW`), admin accounts, default or initial admin passwords
  changed, external authentication (LDAP, OIDC) and who can sign in through it, password policy
  (Gitea/Forgejo `MIN_PASSWORD_LENGTH`, `PASSWORD_CHECK_PWN`).
- Organization owners and instance admins: how many, whether they're daily-use accounts, and whether
  outside collaborators hold admin.
- Email addresses on accounts: verified, and still controlled by the user (an expired domain on a
  recovery address is an account-takeover path).
- Commit signing (SSH, GPG, or S/MIME) and whether vigilant mode or required signed commits are in use.
  Optional for most homes; useful where the history is evidence.

#### C. Personal access tokens, OAuth apps, deploy keys, and SSH keys

- Personal access tokens: type (on GitHub, fine-grained preferred over classic; classic tokens reach
  every repository the user can), scopes, expiry, last use, and which ones have no expiry. GitHub lets
  organizations set maximum token lifetimes and require approval for fine-grained tokens; record whether
  those policies are on.
- Where each token is used (CI secrets, local credential stores, scripts, AI agents, MCP servers, backup
  and mirror jobs). Tokens shared across several uses can't be rotated cleanly.
- OAuth apps and GitHub/GitLab/Gitea apps installed on accounts and organizations: what they can access,
  whether they're still used, and who installed them.
- Deploy keys: which repositories, read-only or write, age, and where the private half lives. A
  write-enabled deploy key on a runner or server is a push credential that bypasses user 2FA.
- SSH keys on accounts: count, age, key type, and whether each is still on a machine the user owns.
- GitLab: project, group, and deploy tokens; runner authentication tokens. Gitea/Forgejo: access tokens
  and their scopes.
- Local storage: `~/.git-credentials` (plain text), credential helpers in use (OS keychain, Git
  Credential Manager, `gh` keyring storage), and tokens in shell history or dotfile repositories.

#### D. Branch protection, rules, and review

- Default and release branches protected (classic branch protection or rulesets on GitHub; protected
  branches on GitLab, Gitea, Forgejo): no force pushes, no deletion, required pull requests, required
  status checks, and whether admins are included.
- Required reviews: count, dismissal of stale approvals on new commits, and code owners for
  security-sensitive paths. GitHub recommends adding `.github/workflows` to CODEOWNERS so workflow
  changes need a designated reviewer.
- Who can bypass protections, and whether bypasses are logged.
- Tag protection for release tags, where release tags drive deployments.
- Single-maintainer homelab repositories can't have meaningful independent review; record the accepted
  risk, and still block force-push and deletion on the default branch.

#### E. Secrets in repositories and history

- Secret scanning: enabled? Alerts open, and how old? GitHub enables user-level push protection by
  default for pushes to public repositories on GitHub.com; repository-level push protection is off by
  default and depends on plan. GitLab offers secret detection and push protection by tier; Gitea and
  Forgejo rely on external scanners or hooks. Record what's actually on.
- Push-protection bypasses: who bypassed, for what reason, and whether the secret was later rotated.
- Scan history, not just the working tree: `.env` files, config exports, Home Assistant
  `secrets.yaml`, Docker Compose files, kubeconfigs, Terraform state and `.tfvars`, Ansible inventories,
  SSH keys, VPN configs, and notebooks with output cells.
- `.gitignore` coverage for local secret files, and whether ignored files were committed before the
  ignore rule existed.
- Forks and mirrors of repositories that ever contained a secret.

#### F. Public repositories and information exposure

- Public repositories (and gists, snippets, wikis, Pages sites, package registries) that publish
  infrastructure details: internal hostnames, IP plans, VPN endpoints, firewall rules, camera and device
  inventories, reverse-proxy configs, or backup layouts. Not secret, but useful reconnaissance; rate
  by what it reveals.
- Repositories meant to be private that are public, and "internal" visibility on a forge with open
  sign-up (effectively public).
- Self-managed forges: `REQUIRE_SIGNIN_VIEW` off and explore pages enabled means anonymous users can
  browse public repositories and the user list; decide whether that's intended.
- Issue trackers and CI logs on public repositories that show environment details or secrets.

#### G. CI workflow and pipeline configuration

- **Default token permissions.** GitHub: workflow permissions set to read-only by default at the
  organization and repository level, with `permissions:` raised per job only where needed; "Allow
  GitHub Actions to create and approve pull requests" off unless needed. GitLab: CI/CD job token
  allow-list for which projects a job token can reach.
- **Privileged triggers.** Every `pull_request_target` and `workflow_run` workflow: does it check out or
  build the PR's head code, download artifacts from an untrusted run, or pass PR data to a shell? Fork PR
  approval settings ("require approval for first-time contributors" or stricter).
- **Script injection.** Untrusted event fields (titles, bodies, branch names, commit messages, comment
  text) used directly in `run:` scripts or in `script:` blocks. The fix is an intermediate environment
  variable or an action argument.
- **Third-party actions, reusable workflows, and CI includes** referenced by tag or branch instead of a
  full-length commit SHA (or a lockfile where the platform supports one). Includes of remote templates in
  `.gitlab-ci.yml` by branch. Jenkins shared libraries loaded from mutable branches.
- **Gitea/Forgejo action resolution.** `DEFAULT_ACTIONS_URL` defaults to `github` on Gitea. Forgejo warns
  that on an instance with open registration, `uses: foo/bar@main` may resolve to a same-named
  repository a stranger created on the instance.
- **Who can change pipelines.** Branches that trigger deployment jobs or reach production secrets; can a
  contributor create an unprotected branch with a matching trigger (Forgejo documents this bypass)?
- **Artifacts and caches** shared between untrusted and trusted jobs (cache poisoning), and artifacts
  that contain secrets or `.env` files.
- **Logs.** Secrets echoed by scripts, structured secrets (JSON, YAML) stored as one secret so masking
  fails, and derived values (Base64, JWTs) not registered as secrets.

#### H. CI secrets and deployment credentials

- Where secrets live: repository, environment, organization or group, instance level, or a Jenkins
  credentials store. Names, scopes, and last-updated dates only.
- Environment protection: deployment environments with required reviewers and branch restrictions
  holding the production secrets, instead of repository-wide secrets.
- Long-lived cloud keys in CI where OIDC federation is available. If OIDC is used, the cloud-side trust
  policy must restrict the repository, branch, or environment claim (see
  [cloud-providers](../../cloud/cloud-providers/SKILL.md)).
- Secrets that reach the home network from CI: SSH keys to servers, Home Assistant or NAS tokens, VPN
  configs, Tailscale or WireGuard keys, Docker registry passwords. Each turns a CI compromise into a LAN
  compromise.
- GitLab: masked and protected variables, and whether protected variables are limited to protected
  branches. Jenkins: credential scope (global vs. folder), and folder or multibranch credentials that
  unprivileged users can reach (Jenkins documents this as a known surprise).

#### I. Runners and build agents

- **Which repositories can use each self-hosted runner.** A runner reachable by public repositories or
  by forks is a finding unless it is ephemeral, isolated, and holds nothing. Runner groups or narrowest
  registration scope (repository-level beats organization- or instance-level).
- **Executor and isolation.** GitLab shell executor (runs as the runner user, can read other projects'
  code on the host; GitLab says trusted builds only), Docker executor with `privileged = true` or the
  Docker socket mounted (host root), host-network mode. Forgejo/Gitea runner labels: `host` (no
  isolation, can read the runner's state file and impersonate it), `lxc`, or `docker`;
  `container.privileged`, `container.network: host`, `container.valid_volumes`, and registry logins on
  the runner host that every job inherits.
- **Ephemeral vs. persistent.** GitHub just-in-time runners (`--jitconfig`), Forgejo ephemeral mode,
  GitLab autoscaled VMs with one build each. Persistent runners keep tools, caches, and anything a
  previous job planted.
- **Runner host.** Runs as root or an admin user? Other services on the same host? Credentials in its
  home directory (SSH keys, cloud CLIs, kubeconfigs, `docker login` state)? Patched?
- **Network position.** Which VLAN the runner is on, and what it can reach: NAS shares, hypervisor and
  router admin pages, Home Assistant, cloud metadata endpoints. Ideally it sits in its own segment with
  outbound access limited to the forge, registries, and package mirrors.
- **Runner tokens.** Registration and authentication tokens stored on the host (GitHub `.credentials`,
  GitLab `config.toml`, Forgejo/Gitea `.runner`): file permissions, and who else on the host can read
  them. A copied token lets an attacker take jobs meant for the real runner (GitLab documents this).
- **Jenkins:** builds don't run on the built-in node (Jenkins says builds should not execute there; set
  its executors to 0), agent-to-controller access control on, agents connected through WebSocket or a
  fixed, firewalled inbound port.

#### J. Jenkins controller

- Authorization strategy: no "Anyone can do anything", no "Logged-in users can do anything" with
  anonymous read on an exposed controller, and the Overall/Administer permission limited to named admins
  (it includes the script console).
- CSRF protection on (default), markup formatter safe (default escapes HTML), Content Security Policy
  where the version supports it.
- Script Security: pending in-process script approvals, and approved signatures that are dangerous
  (anything touching `Runtime`, `ProcessBuilder`, file I/O, or Jenkins internals).
- Plugins: installed from the official update center, no unmaintained or warned-about plugins, and no
  plugins installed only "to try".
- Credentials: types, scopes, and which jobs use them. Credentials are encrypted with a key on the
  controller's disk (`secrets/`), so anyone who can read `JENKINS_HOME` can decrypt them; treat backups of
  `JENKINS_HOME` as secret material.
- Configuration as Code (JCasC) and job definitions in git: do they contain plain-text secrets?
- The Jenkins CLI and SSH server plugin: enabled? Who can use them?

#### K. Self-managed forge server

- Exposure: which networks reach the web UI and SSH; reverse proxy and TLS (see
  [web-servers](../../web/web-servers/SKILL.md)); admin pages reachable from the internet.
- Outbound request controls (SSRF): webhooks and repository migrations can make the server fetch URLs.
  Gitea/Forgejo `[security]`/`[webhook]`/`[migrations]` `ALLOWED_HOST_LIST` settings (check the exact
  section for the installed version) and whether private and loopback ranges are allowed; GitLab's
  "Allow requests to the local network from webhooks and integrations" setting (off by default on
  current versions; verify).
- Server secrets: Gitea/Forgejo `SECRET_KEY` and `INTERNAL_TOKEN` (or their `_URI` file variants), the
  `app.ini` file's permissions; GitLab `gitlab-secrets.json`. Backups of these are as sensitive as the
  server.
- Git hooks and server-side hooks: who can install them (Gitea/Forgejo can let users edit git hooks, which
  is code execution on the server; it should be off).
- Database and object storage: credentials, network exposure, backups and restore tests.
- Mail settings: sign-up confirmation and password-reset mail depend on them.

#### L. Dependency and image scanning (as checks, not separate products)

- Is dependency update and alerting enabled per repository: Dependabot alerts and security updates,
  Renovate, GitLab dependency scanning? Are alerts triaged or piling up?
- Note that Dependabot doesn't alert on actions pinned to SHAs; pair SHA pinning with Dependabot or
  Renovate version updates so pins still move forward deliberately.
- Container images built or deployed by CI: scanned with Trivy, Grype, Snyk, or the registry's scanner?
  Base images pinned by digest and updated on a schedule (see [docker](../../containers/docker/SKILL.md)).
- Scanner credentials (Snyk tokens, registry tokens) stored as CI secrets with minimal scope.
- Auto-merge of dependency updates: only with required checks, and never for major versions or for
  actions and CI tooling without review.

#### M. Audit logs and monitoring

- Audit logs available on the plan or edition, retention, and whether anyone reads them: new tokens, new
  deploy keys, new OAuth apps, visibility changes, protection changes, secret-scanning bypasses, new
  runners, new admins.
- Notifications for security alerts reach someone.
- Jenkins: audit trail plugin or equivalent; system log forwarding off the controller.
- Self-managed forges: logs forwarded off the server.

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Tokens and keys in use:** every script, CI job, mirror, backup job, AI agent, MCP server, and
  integration that uses a token or deploy key breaks when it is revoked. Find them first.
- **Branch protection and rules:** bots, release automation, and dependency updaters that push directly
  to protected branches stop working.
- **Workflow permission changes:** jobs that write releases, packages, comments, or tags fail when the
  default token goes read-only; list them and grant per-job permissions.
- **Runner changes:** pipelines that require a specific label stall when a runner is removed or rescoped.
- **Jenkins:** authorization changes can lock out every admin, including the one making the change.
  Plugin updates can break jobs and require restarts.
- **Self-managed forge updates:** database migrations usually can't be rolled back without a restore.
- **The agent's own access:** if the assessing agent uses one of these tokens, revoking it cuts the agent
  off mid-task. Plan the order.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| No 2FA on accounts with write/admin | Enable 2FA (passkey or security key preferred) and require it at org/instance level. | Accounts without 2FA lose access until enrolled; store recovery codes offline. |
| Classic or non-expiring tokens | Replace with fine-grained, repository-scoped tokens with expiry; or use `gh`/Git Credential Manager sign-in. | Each consumer needs a new token; expiries need a renewal routine. |
| Plain-text `~/.git-credentials` | Switch to the OS keychain credential helper; rotate tokens that were stored. | One re-authentication per machine. |
| Write-enabled deploy key | Make it read-only, or replace it with a scoped token or app. | Jobs that push need another credential with narrow scope. |
| Committed secret | Rotate at the provider immediately; then decide whether to rewrite history. | Rotation breaks old copies; history rewrite breaks every clone and fork, and doesn't remove copies elsewhere. |
| Push protection off | Enable it where the plan allows; add a pre-commit secret scanner locally. | Occasional false positives; bypasses need a reason. |
| Unprotected default branch | Protect it: no force push, no deletion, PRs and checks required. | Direct pushes stop; bots need explicit bypass. |
| Workflow token read/write by default | Set default to read-only; add `permissions:` per job. | Jobs that write need explicit grants. |
| `pull_request_target` running PR code | Split into an unprivileged `pull_request` build and a privileged `workflow_run` step that handles only trusted outputs; or remove the trigger. | Fork PRs lose some automation (labels, comments) until redesigned. |
| Script injection | Move untrusted values into `env:` and quote them in the script. | None functionally. |
| Actions or includes by tag/branch | Pin to full-length SHAs; let Dependabot or Renovate propose updates. | Updates become PRs that need review. |
| Self-hosted runner reachable by public repos or forks | Restrict to private repositories or a runner group; make it ephemeral; move it to an isolated VLAN with limited outbound access. | Setup effort; slower jobs without persistent caches. |
| Privileged or socket-mounted runner jobs | Use rootless builders or a dedicated, isolated, ephemeral VM for jobs that truly need privilege, limited to protected branches. | Some image-build workflows need rework. |
| Long-lived cloud keys in CI | Move to OIDC with a trust policy restricted by repo and branch or environment. | Cloud-side configuration; restricted claims block other branches by design. |
| Jenkins builds on built-in node | Set built-in node executors to 0; run builds on agents. | Requires at least one agent. |
| Jenkins broad authorization | Matrix-based or role-based authorization; Administer only for named admins. | Users lose permissions they didn't need; test with a non-admin account. |
| Unmaintained or warned Jenkins plugins | Update or remove after checking dependents. | Jobs using them break; some need replacements. |
| Self-managed forge open sign-up | Disable sign-up or require admin approval and email confirmation. | New users need an admin. |
| Forge allows webhooks to the LAN | Restrict outbound targets to an allow-list. | Legitimate LAN webhooks must be listed. |
| No dependency or image scanning | Enable Dependabot/Renovate and an image scanner in CI; triage on a schedule. | Alert volume; someone must own triage. |

Group the plan: immediate containment (leaked tokens, exposed Jenkins or runner footholds, active
compromise indicators) → urgent fixes (privileged triggers running PR code, runners open to forks, no
2FA on admins) → high-priority hardening (token types and expiry, branch protection, pinning) → routine
maintenance (scanning, updates) → optional defense in depth (signing, audit-log review). Then ask for
approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Code-hosting and CI specifics:

- **Rotate before you clean up.** For any exposed secret: create the replacement, update every consumer,
  verify, then revoke the old one at its provider. Never paste token values into chat, issues, commit
  messages, or logs.
- **Token and key changes are C2** when anything automated uses them. Revoking an unused token is C1 if
  its last-use date and consumers confirm it's unused; otherwise C2.
- **History rewrites are C3** (they destroy the existing history for everyone) and are never the security
  fix. Recommend them only after rotation, with the owner's explicit choice, a full mirror backup, and a
  plan for every clone and fork. Let the user run them.
- **Branch protection and rules are C1** to add for a solo repository, **C2** where bots or other people
  push. Add bypass entries for automation deliberately, not by disabling protection.
- **Workflow edits go through the normal review path** (a pull request), not a direct push to the
  default branch, even when the agent has access. Test changes on a branch first; a broken workflow can
  block releases.
- **Pin actions to the SHA of the version already in use** first (no behavior change), confirming the SHA
  belongs to the action's own repository. Update versions later as separate, reviewed changes.
- **Runner changes are C2.** Pause or drain the runner, change scope, labels, or executor settings,
  restart, and confirm a test job runs where expected and nowhere else. Re-registering issues new tokens;
  remove the old registration.
- **Jenkins:** back up `JENKINS_HOME` (as secret material) before authorization, plugin, or core changes.
  Keep an admin session open while changing authorization, and test from a second browser. Update
  plugins in small batches and read their changelogs.
- **Self-managed forge updates are C2:** take a vendor-supported backup, read the release notes for
  required upgrade paths (GitLab requires specific stop versions), and verify the backup restores.

After each change, follow the core "after a change" steps: re-read the setting through the API, confirm
dependent jobs and integrations work, and confirm the audit log recorded the change.

### Hard stops (refer to a specialist or do manually; never automate)

- Rewriting git history or force-pushing to shared branches as part of remediation.
- Deleting repositories, organizations, runners' work directories with unknown contents, or audit logs.
- Running Groovy in the Jenkins script console, or editing `credentials.xml` or `secrets/` by hand.
- Logging in with, or calling APIs with, a discovered credential to "confirm" it works.
- Disabling push protection, branch protection, or required reviews to get a change through.
- Changing organization-wide or instance-wide authentication (SSO, 2FA enforcement) without the owner
  present and a tested recovery path for every admin.
- Restoring or downgrading a self-managed forge's database without the vendor's procedure.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the code-hosting and CI
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### GIT-001: Self-hosted runner on the main LAN accepts jobs from a public repository's pull requests

**Confidence:** Confirmed
**Priority:** P1. Anyone with a GitHub account can open a pull request whose workflow runs on a
persistent runner inside the home LAN, with network access to the NAS and the hypervisor's admin
interface. No credentials are needed.
**State:** Open
**Component:** GitHub Actions self-hosted runner (current release) on a Linux VM, registered to a public
repository
**Evidence:** Observed 2026-10-25: `gh api repos/<owner>/<repo>/actions/runners` lists one self-hosted
runner with labels `self-hosted, linux`; the repository is public. `.github/workflows/ci.yml` uses
`on: pull_request` and `runs-on: self-hosted`. The fork pull request approval setting is "Require
approval for first-time contributors" only. On the VM, the runner service runs as a user in the `docker`
group, and the VM has an address in `192.0.2.0/24`, the same subnet as the NAS at `192.0.2.20`.
**Expected secure state:** self-hosted runners used only with private repositories, or ephemeral and
isolated with no LAN reach (GitHub Actions secure-use guidance and self-hosted runner docs).
**Exposure and prerequisites:** any GitHub user; one previously merged contribution removes the approval
step.
**Dependencies / blast radius:** the repository's CI uses the runner for a hardware-specific test; three
other private repositories use hosted runners.
**Recommended remediation:** (1) move the public repository's jobs to GitHub-hosted runners now; (2) keep
the self-hosted runner for private repositories only, through a runner group; (3) remove the runner user
from the `docker` group or run jobs rootless; (4) move the VM to an isolated VLAN with outbound access
limited to GitHub and package mirrors; (5) make it ephemeral with just-in-time registration.
**Operation class:** C2 (CI behavior and network placement change).
**Approval required:** Yes.
**Verification:** a test pull request from a fork runs on a hosted runner; the self-hosted runner no
longer appears for the public repository; from the runner VM, the NAS and hypervisor addresses are
unreachable.
**Rollback:** restore the previous `runs-on` value and runner registration (not recommended).

---

## Version history

- **1.0** (2026-10-31): Initial version.
