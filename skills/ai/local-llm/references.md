# Local LLM and Generative-AI Servers: References

Always prefer current vendor documentation. These projects release often and change defaults, flags, and
ports between versions. Re-verify links and contents when updating this skill.

Last verified: 2026-10-31

## Vendor (authoritative)

- Ollama
  - FAQ (bind address, `OLLAMA_HOST`, `OLLAMA_ORIGINS`, proxies, model storage, cloud features):
    https://docs.ollama.com/faq
  - Troubleshooting (log locations): https://docs.ollama.com/troubleshooting
  - API reference: https://github.com/ollama/ollama/blob/main/docs/api.md
  - Security advisories: https://github.com/ollama/ollama/security/advisories
- llama.cpp server
  - Server README (host, port, `--api-key`, endpoints, tools/MCP warnings):
    https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
  - Security advisories: https://github.com/ggml-org/llama.cpp/security/advisories
- vLLM
  - Security guide (API key scope, unauthenticated endpoints, dev mode, multi-node, media fetching):
    https://docs.vllm.ai/en/latest/usage/security.html
  - Security advisories: https://github.com/vllm-project/vllm/security/advisories
- LM Studio
  - Server settings (authentication, local network, CORS, MCP options):
    https://lmstudio.ai/docs/developer/core/server/settings
  - Integration page documenting the default port and token headers:
    https://lmstudio.ai/docs/integrations/claude-code
- LocalAI
  - CLI reference (address, API keys, web UI, CORS, CSRF, galleries, P2P, auth flags):
    https://localai.io/docs/reference/cli-reference/
  - Authentication and authorization (accounts, first admin, registration modes, legacy keys):
    https://localai.io/docs/features/authentication/
  - Advanced usage (preloaded models, `/models/apply`, external gRPC backends, `.env` files):
    https://localai.io/docs/advanced/
  - Distributed inference (P2P token, DHT, federated mode, workers):
    https://localai.io/docs/features/distribute/
  - Security advisories: https://github.com/mudler/LocalAI/security/advisories
- LiteLLM proxy
  - Security best practices (env credential login, SSO, network, secrets, docs endpoints):
    https://docs.litellm.ai/docs/proxy/security_best_practices
  - Production checklist (master key, salt key, database, `LITELLM_MODE`):
    https://docs.litellm.ai/docs/proxy/prod
  - Admin UI (path, `UI_USERNAME`, `UI_PASSWORD`, `DISABLE_ADMIN_UI`, login limits):
    https://docs.litellm.ai/docs/proxy/ui
  - Virtual keys, budgets, and rate limits: https://docs.litellm.ai/docs/proxy/virtual_keys
  - Health endpoints (unauthenticated probes): https://docs.litellm.ai/docs/proxy/health
  - Security notices (including the March 2026 PyPI compromise and verified releases):
    https://docs.litellm.ai/blog/tags/security
  - Security advisories: https://github.com/BerriAI/litellm/security/advisories
- Open WebUI
  - Environment variable reference (signup, roles, auth, API keys, CORS, persistent config, admin
    posture): https://docs.openwebui.com/reference/env-configuration
  - Roles and permissions: https://docs.openwebui.com/features/authentication-access/rbac/roles
  - Security advisories: https://github.com/open-webui/open-webui/security/advisories
- ComfyUI
  - Documentation: https://docs.comfy.org/
  - ComfyUI-Manager configuration (`security_level`, `network_mode`): https://docs.comfy.org/manager/configuration
  - ComfyUI-Manager: https://github.com/Comfy-Org/ComfyUI-Manager
  - Security advisories: https://github.com/Comfy-Org/ComfyUI/security/advisories
- AUTOMATIC1111 Stable Diffusion web UI
  - Command-line arguments (`--listen`, `--share`, `--api-auth`, extension and unpickle flags):
    https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Command-Line-Arguments-and-Settings
  - Security advisories: https://github.com/AUTOMATIC1111/stable-diffusion-webui/security/advisories
- Hugging Face
  - Pickle scanning and its limits: https://huggingface.co/docs/hub/security-pickle
  - safetensors format: https://github.com/huggingface/safetensors

For forks and other Gradio apps (Forge, SD.Next, text-to-speech UIs), use the project's own README,
launch flags, and GitHub security advisories for the installed version.

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- OWASP Top 10 for LLM Applications (2025): https://genai.owasp.org/llm-top-10/
  Risk categories (prompt injection, supply chain, excessive agency, unbounded consumption, vector and
  embedding weaknesses). Useful for naming risks; it doesn't describe any product's settings.
