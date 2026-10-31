---
name: ai-app-builders
description: >-
  Security assessment, hardening, remediation, and incident response for self-hosted low-code LLM app
  builders: Flowise, Dify, Langflow, and similar visual agent and RAG builders. Use when auditing
  exposure and authentication, first-run admin setup, default secrets in .env files, API keys for
  published flows and apps, the stored credentials for model providers and tools, code-execution nodes
  (custom JavaScript or Python, Custom MCP, code sandboxes), plugins, SSRF controls, RAG knowledge
  bases and uploaded documents, or when a builder instance may have been exposed, abused for code
  execution, or had its stored keys stolen.
license: CC-BY-4.0
metadata:
  version: "1.0"
  last_reviewed: "2026-10-31"
  applies_to: "Flowise 3.x, Dify self-hosted (Community Edition, Docker Compose), Langflow 1.x, and similar builders (verify each live version; defaults have changed between releases)"
  audience: "home, work, homelab, web"
  finding_prefix: "AIB"
  modes: "discover, recommend, remediate, respond"
---

# AI App Builder Security

Act as a careful, evidence-driven security engineer for low-code LLM application builders. These tools
let users wire models, tools, documents, and code into flows through a web UI, then publish them as chat
widgets or APIs. A builder instance typically holds API keys for paid model providers and connected
services, documents ingested for RAG, and nodes that execute code on the server. The main risks are
instances exposed without authentication, first-run setup pages anyone can claim, default secrets
shipped in example `.env` files, code-execution features that are remote code execution for anyone who
can edit a flow (and, through repeated vulnerabilities, sometimes for anyone who can reach the API),
published flows that spend the owner's keys or leak data, and server-side requests into the LAN.
Identify, explain, prioritize, remediate (only when authorized), and verify these weaknesses.

## How to use this skill

This skill holds only builder-specific guidance. It builds on the shared core, which always applies:

| Core document | Covers |
|---|---|
| [modes-and-authorization.md](../../../core/modes-and-authorization.md) | The four modes, transitions, operation classes (R/C1/C2/C3), standing authorization |
| [operating-principles.md](../../../core/operating-principles.md) | Principles, capability discovery, scope, communication, untrusted data |
| [vulnerability-triage.md](../../../core/vulnerability-triage.md) | Lifecycle, CVE/KEV validation, P0–P4 priority scale |
| [evidence-and-reporting.md](../../../core/evidence-and-reporting.md) | Evidence labels, statuses, finding template, report format, cadence |
| [tool-use-contract.md](../../../core/tool-use-contract.md) | Rules for commands, APIs, MCP tools, and third-party integrations |
| [reporting-protocol.md](../../../core/reporting-protocol.md) | Optional live progress reporting to a dashboard |
| [incident-response.md](../../../core/incident-response.md) | The generic Respond playbook |

Builder-specific Respond steps are in [incident-response.md](incident-response.md). Vendor documentation
and advisories are in [references.md](references.md). Related skills:

- [local-llm](../local-llm/SKILL.md) for the model servers (Ollama and similar) and chat front ends these
  builders often call.
- [mcp-servers](../mcp-servers/SKILL.md) for MCP servers a builder connects to or exposes, and for the
  vector databases (Qdrant, Chroma, and others) behind RAG features.
- [docker](../../containers/docker/SKILL.md) for the Compose stacks these tools ship as.
- [self-hosted-web-apps](../../web-apps/self-hosted-web-apps/SKILL.md) and
  [web-servers](../../web/web-servers/SKILL.md) for the reverse proxy, TLS, and SSO in front of them.
- [cloud-providers](../../cloud/cloud-providers/SKILL.md) for provider accounts whose keys the builder
  stores.

## Builder-specific principles

- **Editing a flow is running code on the server.** Flowise has custom JavaScript function and tool
  nodes and a Custom MCP node that launches processes; Langflow lets users write custom Python
  components; Dify has Code nodes executed by its sandbox service and installable plugins. Treat every
  account that can create or edit flows as able to execute code on the host, whatever the vendor's
  sandbox claims. Several builders have shipped critical advisories in exactly these features (Flowise's
  Custom MCP and Custom JS Function nodes and its JavaScript sandbox; Langflow's code-validation
  endpoint, which reached CISA KEV in 2025). Check the vendor's advisory list for the installed version.
- **Published means public.** Chat widgets, shared app URLs, and prediction or run APIs are designed for
  anonymous callers unless an API key or app-level access control is set. Each call spends the owner's
  model-provider credits and can reach every tool and document the flow uses.
- **First-run setup is a race.** Dify's `/install` page creates the first admin and is gated only by
  `INIT_PASSWORD`, which is empty by default. Flowise asks the first visitor to register an admin on a
  fresh instance (verify for the installed version). An instance exposed before setup can be claimed by
  a stranger.
- **Example `.env` files ship known secrets.** Dify's documentation says the prefilled `SECRET_KEY` must
  be replaced for production and lists default database and Redis passwords and a default sandbox API
  key. Flowise documents default session and JWT values and warns that relying on them makes token
  forgery easier. These are public; treat them as no secret at all.
- **The builder is a credential vault.** Stored credentials for model providers, vector databases,
  search APIs, email, chat, and cloud services are encrypted with a key that lives on the same host (a
  key file, an environment variable, or `SECRET_KEY`). Anyone with the database and that key has every
  credential.
- **Server-side fetches reach the LAN.** HTTP request nodes, web loaders, tool calls, plugin installs, and
  MCP connections make requests from the server. Dify routes them through an SSRF proxy; other builders
  rely on deny lists or nothing. On a homelab, that's a path to router, NAS, and hypervisor admin pages.
- **RAG documents are readable by whoever can query the flow,** and every ingested document can carry
  prompt injection aimed at the flow's tools.

## Deployment variants

| Variant | How to recognize it | What changes |
|---|---|---|
| **Docker Compose stack** (the usual self-hosted install) | `docker-compose.yml` and `.env` in an install folder; several containers (API, web, worker, database, Redis, vector DB, sandbox, proxy). | Secrets live in `.env`; internal services may be published on host ports by mistake; container privileges and mounts matter. |
| **Single process** (`npx flowise start`, `pip install langflow`, `uv run langflow`) | A Node or Python process on a workstation or server. | Runs as the user who started it, with that user's home directory; data and keys in the user's home (Flowise defaults `DATABASE_PATH` to `.flowise` in the home directory with SQLite). |
| **Desktop app** (Langflow Desktop and similar) | Installed application on a workstation. | Local by default; check bind address and whether it's reachable from the LAN. |
| **Behind a reverse proxy or tunnel** | Hostname on a proxy or tunnel service; TLS terminated in front. | The proxy's authentication may be the only gate; check that the app's own ports aren't reachable directly. |
| **Vendor cloud** (Dify Cloud, hosted Flowise or Langflow offerings) | Vendor domain. | You assess accounts, workspace members, API keys, published apps, and stored credentials; the vendor runs the servers. |
| **Kubernetes or Helm** | Helm chart values, ingress objects. | Secrets in values files or Kubernetes secrets; ingress exposure; network policies for the sandbox. |

## Detection

Hints for recognizing these products during a network inventory (used by the `full-assessment` skill).
Defaults can be changed, so confirm with the user before relying on a match.

- **Flowise:** web UI and API on 3000 by default (`PORT`); page title Flowise (observed); API under
  `/api/v1/` (for example prediction endpoints `/api/v1/prediction/<flow-id>`, vendor-documented).
- **Dify:** the Compose stack's nginx on 80 and 443 (`EXPOSE_NGINX_PORT`, `EXPOSE_NGINX_SSL_PORT`);
  page title Dify (observed); first-run admin setup at `/install`; the plugin daemon's remote debugging
  port 5003 (`EXPOSE_PLUGIN_DEBUGGING_PORT`, published on all interfaces by default via
  `PLUGIN_DEBUGGING_HOST`). Internal services that should not be published on the host: the code
  sandbox on 8194 (`SANDBOX_PORT`), the SSRF proxy on 3128, and the API, web, plugin daemon, database,
  Redis, and vector DB containers (ports observed in the Compose file; verify for the installed release).
- **Langflow:** web UI and API on 7860 by default; page title Langflow (observed); API under `/api/v1/`
  with API keys sent in the `x-api-key` header.
- **Similar builders:** check the vendor's documented default port and page title; many run on 3000,
  5000, 7860, or 8080 alongside other apps, so don't rely on the port alone.
- Containers named after the product in `docker ps`; images from the vendors' official registries.
- No mDNS or SSDP announcements; MAC vendors don't apply.

---

## Discover

All operations in this mode are class **R** (read-only). Confirm scope and access first (core: operating
principles). Mark anything you can't inspect **Not assessed**.

### Baseline commands

Prefer the admin UI and the deployment files. These are *candidate* read-only checks, each labeled.
`.env` files and Compose files contain secrets: **record variable names and whether a value is the
documented default, never the values themselves.**

```sh
# Containers, images, published ports (read-only; vendor-documented Docker commands)
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}' | grep -Ei 'flowise|dify|langflow|sandbox|ssrf|plugin'
docker compose -f <install-dir>/docker-compose.yml config --services

# Listening sockets on the host (not yet verified on every OS)
ss -ltnp | grep -E ':(3000|7860|80|443|5003|8194|3128)\b'      # Linux
lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(3000|7860|5003|8194)'  # macOS

# Which security-relevant variables are set (names only; flag documented defaults without printing them)
grep -nE '^(SECRET_KEY|INIT_PASSWORD|CODE_EXECUTION_API_KEY|SANDBOX_API_KEY|SANDBOX_ENABLE_NETWORK|DB_PASSWORD|REDIS_PASSWORD|PLUGIN_DEBUGGING_HOST|FORCE_VERIFYING_SIGNATURE|ALLOW_REGISTER)=' \
  <install-dir>/.env | sed -E 's/=.*/=<set>/'
grep -nE '^(PORT|JWT_AUTH_TOKEN_SECRET|EXPRESS_SESSION_SECRET|FLOWISE_SECRETKEY_OVERWRITE|SECRETKEY_PATH|TOOL_FUNCTION_BUILTIN_DEP|TOOL_FUNCTION_EXTERNAL_DEP|CUSTOM_MCP_SECURITY_CHECK|HTTP_DENY_LIST|CORS_ORIGINS|IFRAME_ORIGINS)=' \
  <install-dir>/.env | sed -E 's/=.*/=<set>/'
grep -nE '^LANGFLOW_(AUTO_LOGIN|SKIP_AUTH_AUTO_LOGIN|SUPERUSER|SECRET_KEY|NEW_USER_IS_ACTIVE|ENABLE_SUPERUSER_CLI|HOST|PORT)=' \
  <install-dir>/.env | sed -E 's/=.*/=<set>/'
# Compare each secret against the vendor's example file yourself (diff the two files locally); a match
# means the secret is publicly known. Report "default" or "changed", not the value.

# Unauthenticated reachability (read-only GETs; observed, verify per version)
curl -sI --max-time 5 http://<builder-host>:3000/           # Flowise
curl -s  --max-time 5 -o /dev/null -w '%{http_code}\n' http://<builder-host>/install   # Dify setup page
curl -sI --max-time 5 http://<builder-host>:7860/           # Langflow
```

- Reading the flow list, credential names, API key names, published apps, and plugin lists in the admin
  UI is class R. Exporting flows (they may embed secrets) is R but produces sensitive files; ask first.
- Check the installed version from the UI, the image tag and digest, or the package version, and compare
  with the vendor's GitHub security advisories (core: triage).

**Never do any of these during Discover:**

- Run, test, or "chat with" a flow, call a prediction or run API, or execute a Code, custom function,
  custom component, or Custom MCP node. Flows can spend credits, call tools, send messages, and run code.
- Complete a first-run setup (`/install` or first admin registration) on an unclaimed instance. If you
  find one exposed, report it as P0/P1 and let the owner claim it.
- Probe vulnerable endpoints (for example code-validation or custom-function routes) to confirm a CVE.
  Decide applicability from the version.
- Try default credentials, decrypt stored credentials, or read the encryption key file.
- Install, update, or remove plugins, components, or nodes; upload documents; change knowledge bases.

### Assessment domains

Every domain must end with a status in the report (Pass / Finding / Not assessed / Not applicable /
Accepted risk).

#### A. Inventory, versions, and update path

- Each builder instance: product, version, install method, image tags and digests, and who maintains it.
- Advisories for the installed version (these projects publish GitHub security advisories; several have
  been critical and code-execution related). An instance more than a few releases behind with code
  execution features is a likely finding.
- How updates happen: pinned tags, `latest`, auto-updaters, and database migrations that block rollback.
- Supporting services in the stack (database, Redis, vector DB, sandbox, proxy, plugin daemon) and their
  own versions.

#### B. Network exposure

- Which networks reach the builder UI and API: loopback, LAN, VPN, or the internet (port forwards,
  tunnels, reverse proxies). Test from outside only with explicit authorization.
- Internal services published on host ports: Dify's sandbox (8194), SSRF proxy (3128), plugin debugging
  port (5003, on all interfaces by default), databases, Redis, and vector DBs. Each should be on the
  Compose network only, or bound to loopback.
- The app reachable directly on its port, bypassing an authenticating reverse proxy.
- TLS: Dify's `NGINX_HTTPS_ENABLED` defaults to off; terminate TLS at the bundled nginx or the reverse
  proxy for anything beyond loopback.
- CORS and embedding: Flowise `CORS_ORIGINS` and `IFRAME_ORIGINS` blank vs. restricted to the sites that
  embed the widget.

#### C. Authentication, first-run setup, and accounts

- **Flowise:** app-level email and password authentication (v3.0.1 and later); the deprecated
  `FLOWISE_USERNAME`/`FLOWISE_PASSWORD` method on older installs (and as the gate for migrating to the
  new method); JWT and session secrets (`JWT_AUTH_TOKEN_SECRET`, `JWT_REFRESH_TOKEN_SECRET`,
  `EXPRESS_SESSION_SECRET`, `TOKEN_HASH_SECRET`) set to unique values, not the documented defaults;
  users, roles, and workspaces where the edition offers them.
- **Dify:** setup completed, and `INIT_PASSWORD` set before the instance was ever reachable; registration
  off (`ALLOW_REGISTER` defaults to false; verify); workspace members and roles; email/password login vs.
  SSO.
- **Langflow:** `LANGFLOW_AUTO_LOGIN` off (current official packages and images default it to false;
  older releases and custom builds may differ, so check the effective value);
  `LANGFLOW_SKIP_AUTH_AUTO_LOGIN` not true (it lets unauthenticated API requests run as the superuser);
  a strong `LANGFLOW_SUPERUSER_PASSWORD`; `LANGFLOW_NEW_USER_IS_ACTIVE` false; `LANGFLOW_ENABLE_SUPERUSER_CLI`
  false as the docs recommend; `LANGFLOW_SECRET_KEY` set explicitly.
- Every account that can create or edit flows: who, and are they all trusted with code execution on the
  host (see principles)?
- MFA or SSO through the reverse proxy where the builder lacks it.

#### D. API keys and published flows and apps

- Every published chatflow, agent, app, or widget: anonymous access, or an API key or access control
  required? What tools and documents can it reach? What model and provider key does it spend?
- API keys: how many, scope (per flow or app vs. global), age, where they're used, and whether they're
  embedded in public web pages (a key in a public widget's page source is public).
- Rate limits and spend limits: builder-side rate limiting (Flowise has per-flow rate limits; check
  `NUMBER_OF_PROXIES` so limits see real client addresses behind a proxy) and provider-side spend caps.
- Public flows with tools that write, send, or execute (email, chat posting, HTTP requests, code nodes,
  database writes): any caller can drive them, including through prompt injection.

#### E. Code-execution features

- **Flowise:** custom JavaScript function and custom tool nodes; which Node modules they may import
  (`TOOL_FUNCTION_BUILTIN_DEP`, `TOOL_FUNCTION_EXTERNAL_DEP`, `ALLOW_BUILTIN_DEP`); the Custom MCP node,
  `CUSTOM_MCP_PROTOCOL` (default `stdio`, which launches processes on the host) and
  `CUSTOM_MCP_SECURITY_CHECK` (default on; keep it on). Advisories have shown both features reachable in
  ways the sandbox didn't contain; rely on patching and on who can edit flows, not on the sandbox.
- **Dify:** Code nodes run in the sandbox service. `CODE_EXECUTION_API_KEY` and `SANDBOX_API_KEY`
  default to a documented value and must be changed together; `SANDBOX_ENABLE_NETWORK` defaults to
  true (code can make network requests, through the SSRF proxy when configured). The sandbox should be
  reachable only from the API container.
- **Langflow:** custom components are Python code that runs in the server process; any user who can
  edit flows can run code. Check whether multi-user mode is used and who has accounts.
- Container and host context for all of them: runs as root? Docker socket or host paths mounted? Host
  network? Secrets for other services in the same container's environment? (See
  [docker](../../containers/docker/SKILL.md).)

#### F. Stored credentials and encryption keys

- Credentials stored in the builder: providers, scopes, and whether each is still used. Prefer
  restricted, per-app keys with spend limits over account-wide admin keys.
- The encryption key: Flowise `SECRETKEY_PATH` (a local file by default) or `FLOWISE_SECRETKEY_OVERWRITE`,
  or AWS storage (`SECRETKEY_STORAGE_TYPE`); Dify `SECRET_KEY`; Langflow `LANGFLOW_SECRET_KEY`. Where it
  lives, file permissions, and whether it's in the same backup as the database (then backups expose
  every credential).
- Default infrastructure secrets in `.env`: Dify `DB_PASSWORD` and `REDIS_PASSWORD` (documented default
  values), `SECRET_KEY` (prefilled example), the sandbox key, and any agent or plugin tokens the docs say
  ship with development values. All must be unique.
- Secrets embedded in exported flows, flow JSON in git, or Compose files committed to repositories.

#### G. Plugins, components, and marketplace content

- **Dify plugins:** installed plugins and their sources (Marketplace, GitHub, local package);
  `FORCE_VERIFYING_SIGNATURE` (default true) kept on; third-party signature verification
  (`THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED` with named public keys) instead of turning verification
  off; the remote debugging port (5003) closed when not developing plugins.
- **Langflow and Flowise:** community components, templates, and marketplace flows imported into the
  instance. Imported flows can contain code nodes and credentials references; review before use.
- Plugin and component permissions (network, storage, model access) where the product declares them.

#### H. SSRF and outbound requests

- **Dify:** `SSRF_PROXY_HTTP_URL` and `SSRF_PROXY_HTTPS_URL` point to the bundled proxy (default
  `http://ssrf_proxy:3128`), which the docs say blocks internal and private ranges. Confirm the proxy is
  in use for the API, worker, sandbox, and plugin daemon, and that its rules weren't loosened.
- **Flowise:** `HTTP_DENY_LIST` for MCP and HTTP requests (empty by default); add private ranges, the
  cloud metadata address, and LAN admin hosts.
- **Others:** web loaders, URL fetch tools, and API request nodes; whether any deny list exists.
- Host-level egress controls for the builder's containers (firewall or Docker network rules) as the
  stronger layer.

#### I. RAG knowledge bases and uploaded data

- Documents uploaded or synced into knowledge bases: sensitivity (personal, financial, network details,
  credentials), source connectors (cloud drives, mail, websites), and who can query each flow or app
  that uses them.
- Vector databases behind the builder: authentication, exposure, and keys (assess with
  [mcp-servers](../mcp-servers/SKILL.md) domain H).
- File storage for uploads (local volumes, S3-compatible buckets): access policy and public URLs.
- Conversation logs and traces stored by the builder: they contain user prompts and model outputs;
  retention, who can read them, and third-party tracing integrations that send them off the host.

#### J. Logging, monitoring, and telemetry

- Application logs (Flowise `LOG_PATH`, container logs): do they record logins, flow edits, API key use,
  and errors? Do they capture secrets or full prompts?
- Alerts or at least periodic review of new accounts, new API keys, edited flows, and provider spend.
- Telemetry the product sends to its vendor and how to opt out (check current docs for the variable or
  setting).

---

## Recommend

No changes are made in this mode. For each finding, produce a recommendation using the core finding
template, including **Dependencies / blast radius** and the **operation class**.

### Dependency and blast-radius check (required)

- **Published flows and embedded widgets** on websites, chat platforms, or home dashboards break when
  API keys are required or rotated, or when CORS is tightened.
- **Stored credentials** are shared with other apps when the same provider key is reused; rotating it
  breaks them too.
- **Changing an encryption key** (`SECRET_KEY`, the Flowise key file) can make stored credentials
  unreadable and log everyone out. Dify's docs say changing `SECRET_KEY` logs out all users and
  invalidates file URLs. Plan re-entry of credentials.
- **Disabling code nodes or plugins** breaks every flow that uses them; list those flows first.
- **Network changes** (removing published ports, adding a proxy, SSRF deny lists) can break integrations
  that call LAN services on purpose.
- **Upgrades** run database migrations that usually prevent rolling back without a restore.

### Recommendation guidance

| Area | Typical recommendation | Consequences to explain |
|---|---|---|
| Instance reachable from the internet without strong auth | Remove the port forward; put it behind a VPN or an authenticating reverse proxy with SSO/MFA. | Remote users and public widgets need a new path. |
| Unclaimed first-run setup | Restrict network access, then claim the instance yourself; set `INIT_PASSWORD` (Dify) before exposing a new install. | None for legitimate use. |
| Langflow auto-login or skip-auth on | Disable `LANGFLOW_AUTO_LOGIN` and `LANGFLOW_SKIP_AUTH_AUTO_LOGIN`; set a strong superuser password; disable the superuser CLI. | Users must sign in; scripts need API keys. |
| Default secrets in `.env` | Generate unique values for every documented default (session, JWT, `SECRET_KEY`, database, Redis, sandbox keys). | Users are logged out; some keys require re-entering stored credentials. |
| Outdated version with code-execution advisories | Update to a fixed release after backing up data and the encryption key. | Migrations; flows may need adjustments. |
| Untrusted users can edit flows | Limit flow editing to people trusted with host access; give others only published apps. | Fewer people can build. |
| Code-execution features not needed | Disable or avoid custom code nodes, Custom MCP with `stdio`, and broad module allowlists. | Flows using them must be redesigned. |
| Published flows without API keys | Require API keys or access control; set rate limits and provider spend caps. | Embedding sites need the key or a backend proxy. |
| Internal services published on host ports | Remove host port mappings for sandbox, proxy, plugin debugging, database, Redis, and vector DB; bind the plugin debugging port to loopback or disable it. | Remote plugin debugging stops. |
| No SSRF controls | Use Dify's SSRF proxy with private ranges blocked; set Flowise `HTTP_DENY_LIST`; add host egress rules. | LAN integrations need explicit allows. |
| Broad provider keys stored | Replace with restricted, per-app keys with spend limits. | Key management overhead. |
| Encryption key stored with the database backups | Store the key separately (secret manager or a separate restricted location). | Restore procedure needs both. |
| Sensitive documents in broadly queryable knowledge bases | Remove them or move them to apps with restricted access. | Less useful answers for those users. |
| Container runs as root or with host mounts | Run as non-root, drop mounts it doesn't need, never mount the Docker socket. | Some images need configuration to run non-root. |

Group the plan: immediate containment (exposed instances without auth, unclaimed setup pages, versions
with exploited code-execution flaws) → urgent fixes (default secrets, public flows with write tools,
published internal services) → high-priority hardening (SSRF controls, key scopes, editing rights) →
routine maintenance (updates, key rotation) → optional defense in depth (egress firewalling, separate
host). Then ask for approval (core: modes and authorization).

---

## Remediate

Apply only approved changes, one at a time, following the core rules. Builder specifics:

- **Back up first:** the database (or SQLite file), uploaded files, the vector store, and the encryption
  key or `.env` (as secret material, stored separately). Record image tags and digests.
- **Network containment is C2** but often the right first step for an exposed instance: remove the port
  forward or published port, confirm from outside, then fix the rest.
- **Rotating default secrets:** some (session and JWT secrets) only log users out; others (`SECRET_KEY`,
  the Flowise encryption key) can make stored credentials unreadable. Check the vendor's docs for the
  installed version, and be ready to re-enter credentials. Treat key changes as C2.
- **Updates are C2:** read release notes for breaking changes and migrations, update one instance at a
  time, and verify flows still run (the owner runs them; see Discover rules).
- **API key changes:** create new keys, update every embedding site and caller, then revoke old keys.
- **Disabling features or plugins:** list affected flows first, tell the owner, then disable.
- **Removing documents from knowledge bases is C3** (deletion); prefer restricting the app's access first
  and confirming the source still exists.

After each change, follow the core "after a change" steps: re-check reachability and authentication from
the relevant networks, confirm published apps behave as intended (owner-run), and confirm logs record the
change.

### Hard stops (refer to a specialist or do manually; never automate)

- Completing first-run setup or registering an admin on someone else's instance.
- Executing flows, code nodes, or custom components to test a fix.
- Decrypting stored credentials or reading the encryption key's contents.
- Deleting flows, knowledge bases, conversation logs, or uploaded files as cleanup.
- Disabling plugin signature verification or SSRF protection to get a plugin or flow working.
- Restoring a database across versions without the vendor's documented procedure.

---

## Respond

On any P0 indicator, switch to Respond immediately. Follow the core playbook plus the builder-specific
steps in [incident-response.md](incident-response.md).

---

## Worked example (invented)

### AIB-001: Dify stack exposed through a port forward with default infrastructure secrets and an open plugin debugging port

**Confidence:** Confirmed
**Priority:** P1. The builder's web UI is reachable from the internet through a router port forward, the
plugin daemon's debugging port is reachable from the LAN, and the stack still uses the documented default
`SECRET_KEY`, database password, and sandbox API key. Stored credentials include an account-wide model
provider key and a home-automation token.
**State:** Open
**Component:** Dify Community Edition (Docker Compose), version current minus three releases
**Evidence:** Observed 2026-10-26: router forwards TCP 443 on `203.0.113.10` to `192.0.2.50:443`;
`docker ps` shows the nginx container publishing 80 and 443 on all interfaces and the plugin daemon
publishing 5003 on all interfaces. In `.env`, `SECRET_KEY`, `DB_PASSWORD`, and `CODE_EXECUTION_API_KEY`
match the vendor's example values (compared locally; values not recorded). `/install` returns a redirect
to sign-in (setup completed). The admin UI lists two stored credentials: a model provider key without a
spend limit and a home-automation long-lived token.
**Expected secure state:** not reachable from the internet without an authenticating layer; plugin
debugging closed or bound to loopback; all documented default secrets replaced (Dify environment
variable documentation); stored credentials restricted and spend-limited.
**Exposure and prerequisites:** the UI to anyone on the internet (sign-in required); the debugging port
to anyone on the LAN.
**Dependencies / blast radius:** one published chat app embedded on a family dashboard; two workspace
members.
**Recommended remediation:** (1) remove the port forward and provide access over the existing VPN;
(2) disable plugin debugging or bind it to loopback; (3) replace `SECRET_KEY`, database, Redis, and
sandbox keys with unique values, planning for logouts and checking whether stored credentials need
re-entry; (4) replace the model provider key with a restricted key with a spend limit, and the
home-automation token with a scoped one; (5) update to the current release after a backup.
**Operation class:** C2 (remote access path changes; secret rotation logs users out).
**Approval required:** Yes.
**Verification:** external check of `203.0.113.10:443` refused; port 5003 not reachable from another LAN
host; `.env` values no longer match the example file; old provider key and token revoked; the dashboard
chat app works for the owner over VPN.
**Rollback:** restore the port forward and `.env` from backup (not recommended).

---

## Version history

- **1.0** (2026-10-31): Initial version.
