# AI App Builders: References

Always prefer each product's current documentation and security advisories. These projects release
often, and defaults (authentication, auto-login, sandbox behavior) have changed between versions.
Re-verify links and contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

- Flowise
  - Authorization overview (app level and chatflow level): https://docs.flowiseai.com/configuration/authorization
  - App-level authentication (email and password since v3.0.1, deprecated `FLOWISE_USERNAME` and
    `FLOWISE_PASSWORD`, JWT and session secrets and their defaults, warning about default secrets):
    https://docs.flowiseai.com/configuration/authorization/app-level
  - Chatflow-level API keys: https://docs.flowiseai.com/configuration/authorization/chatflow-level
  - Environment variables (`PORT`, `SECRETKEY_PATH`, `FLOWISE_SECRETKEY_OVERWRITE`,
    `SECRETKEY_STORAGE_TYPE`, `TOOL_FUNCTION_BUILTIN_DEP`, `TOOL_FUNCTION_EXTERNAL_DEP`,
    `CUSTOM_MCP_PROTOCOL`, `CUSTOM_MCP_SECURITY_CHECK`, `HTTP_DENY_LIST`, `CORS_ORIGINS`,
    `IFRAME_ORIGINS`, `DATABASE_PATH`, `LOG_PATH`, `NUMBER_OF_PROXIES`):
    https://docs.flowiseai.com/configuration/environment-variables
  - Security advisories: https://github.com/FlowiseAI/Flowise/security/advisories
- Dify
  - Environment variables (`SECRET_KEY`, `INIT_PASSWORD`, `CODE_EXECUTION_API_KEY`, `SANDBOX_API_KEY`,
    `SANDBOX_ENABLE_NETWORK`, `SANDBOX_PORT`, `SSRF_PROXY_HTTP_URL`, `DB_PASSWORD`, `REDIS_PASSWORD`,
    `FORCE_VERIFYING_SIGNATURE`, `EXPOSE_NGINX_PORT`, `EXPOSE_PLUGIN_DEBUGGING_PORT`,
    `PLUGIN_DEBUGGING_HOST`, `NGINX_HTTPS_ENABLED`, `ALLOW_REGISTER`):
    https://docs.dify.ai/en/self-host/configuration/environments
  - Third-party plugin signature verification:
    https://docs.dify.ai/en/develop-plugin/publishing/standards/third-party-signature-verification
  - Security advisories: https://github.com/langgenius/dify/security/advisories
  - Code sandbox service: https://github.com/langgenius/dify-sandbox
- Langflow
  - API keys and authentication (`LANGFLOW_AUTO_LOGIN`, `LANGFLOW_SUPERUSER`,
    `LANGFLOW_SUPERUSER_PASSWORD`, `LANGFLOW_SECRET_KEY`, `LANGFLOW_SKIP_AUTH_AUTO_LOGIN`,
    `LANGFLOW_NEW_USER_IS_ACTIVE`, `LANGFLOW_ENABLE_SUPERUSER_CLI`, `x-api-key`):
    https://docs.langflow.org/api-keys-and-authentication
  - Security advisories: https://github.com/langflow-ai/langflow/security/advisories
- CISA Known Exploited Vulnerabilities catalog (check builder products here during triage):
  https://www.cisa.gov/known-exploited-vulnerabilities-catalog

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- GitLab Advisory Database entries for Flowise (Custom MCP and Custom JS Function code-execution
  advisories): https://advisories.gitlab.com/pkg/npm/flowise/
  Useful for affected and fixed version ranges; confirm against the vendor's GitHub advisories.
- Help Net Security on Langflow CVE-2025-3248 exploitation and its KEV listing:
  https://www.helpnetsecurity.com/2025/05/06/langflow-cve-2025-3248-exploited/
  Background on why exposed builders are targeted; use KEV and the vendor advisory for facts.
- OWASP Top 10 for LLM Applications (2025): https://genai.owasp.org/llm-top-10/

## Not verified at time of writing

- Whether a fresh Flowise 3.x instance lets the first visitor register the admin account; check the
  app-level authentication docs for the installed version.
- Internal container ports in the Dify Compose stack other than those named in the environment
  documentation (API, web, plugin daemon); read the installed `docker-compose.yml`.
- How dify-sandbox isolates code (its README describes system-call restrictions); not re-checked.
- Telemetry opt-out settings for each builder.
- The Flowise chatflow-level, Dify sandbox repository, and Langflow and Dify advisory pages were not
  fetched for this version.
