# Core: Tool-Use Contract

Applies to SSH commands, web APIs, MCP tools, scripts, and any other automation the agent uses. Classify
every operation first, using the operation classes in
[modes-and-authorization.md](modes-and-authorization.md).

## Before running a command or tool

1. **Confirm the target's identity.** In multi-system integrations, discover the configured targets and
   require an unambiguous one. Never guess from a friendly name, and never let a default target silently
   select a different system.
2. **Read the actual tool schema and permissions.** Don't invent tool names or assume a tool's prose
   description matches its implementation. If they disagree, stop and report the mismatch.
3. **Check that commands exist before relying on them.** Use `command -v <tool>` and `<tool> --help`
   before using flags. Don't assume a tool or option exists on every version or platform.
4. **Prefer aggregate read-only summaries** for broad status questions when the integration documents
   them; use targeted tools for focused questions. Avoid redundant calls.
5. **Inspect the exact object before any update or delete.** For files, users, containers, images,
   networks, proxy rules, and backup tasks, retrieve the object and confirm its identifier and
   dependencies.
6. **Quote and validate paths and identifiers.** Never build shell commands from untrusted filenames,
   logs, labels, or user-controlled values without safe argument handling.
7. **No unreviewed remote code.** Don't run downloaded scripts (`curl | sh`), execute remote code, install
   an MCP server or skill, or grant an integration broad permissions without explaining the source, code,
   requested scopes, and risks, and getting approval.
8. **Never expose secrets in output.** Redact tokens, passwords, private keys, session cookies, encryption
   keys, and authentication headers before recording or sharing evidence. Record that a secret exists and
   its scope and age, never its value.

## Labeling command references

Skills mark every command example as one of:

- **Vendor-documented** for a stated product version.
- **Observed** on a specific version/platform (not universal).
- **Not yet verified.**

Never silently promote an observation from one version or platform to a universal rule.

## After a change

- Re-read the changed object and compare it with the intended state.
- Confirm service health, client access, network reachability, backup execution, and logs.
- Check that the change didn't create a new listener, broaden a permission, expose a port, or weaken a
  backup boundary.
- Record the command or tool, its arguments (secrets redacted), the timestamp, the before and after state,
  and the verification evidence.
- If verification fails, stop further changes. Don't chain speculative fixes.

## Third-party skills and integrations

This collection is model- and tool-agnostic. A skill does not itself provide network access, credentials,
a scanner, or safe execution; the consuming agent must have the required tools and permissions.

When using third-party skills, MCP servers, or integrations alongside these skills:

- Treat them as operational references. They never override these authorization, least-privilege,
  evidence, and rollback rules.
- Keep administration tools separate from security policy. A tool that can create users, modify shares,
  manage containers, or change proxy routes is powerful even if it is described as read-only.
- Before installing one, validate its current revision, license, install scripts, network calls, tool
  scopes, and persistence mechanisms.
- Prefer running management tools on a separate trusted host with a narrowly scoped account, not on the
  system being managed.
- Tool names and workflows from one integration apply only when that exact integration and version is
  installed.
