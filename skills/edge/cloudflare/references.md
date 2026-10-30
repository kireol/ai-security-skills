# Cloudflare: References

Always prefer current Cloudflare developer documentation; the dashboard and product names change often.

Last verified: 2026-10-30

## Vendor (authoritative)

- Security advisories (cloudflared and other open-source projects, on GitHub):
  https://github.com/cloudflare/cloudflared/security/advisories
- cloudflared releases and changelog: https://github.com/cloudflare/cloudflared/releases
- cloudflared downloads and version support policy (one year from the most recent release):
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/
- Tunnel tokens, rotation, and compromised-token procedure:
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/remote-tunnel-permissions/
- Locally managed tunnel configuration file, ingress rules, catch-all, `ingress validate`/`ingress rule`:
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/
- cloudflared origin parameters (`noTLSVerify`, `access`, `originServerName`):
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/cloudflared-parameters/origin-parameters/
- Useful tunnel commands:
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/tunnel-useful-commands/
- Tunnel metrics (default metrics address and ports):
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/monitor-tunnels/metrics/
- Tunnel firewall requirements (outbound port 7844):
  https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/tunnel-with-firewall/
- Access policies (actions, Bypass and Everyone warnings, rule types):
  https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
- Access service tokens: https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/
- Identity providers and one-time PIN:
  https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/
  https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
- Account 2FA and enforcement: https://developers.cloudflare.com/fundamentals/user-profiles/2fa/
- API tokens versus the Global API Key: https://developers.cloudflare.com/fundamentals/api/get-started/keys/
- Audit logs: https://developers.cloudflare.com/fundamentals/account/account-security/review-audit-logs/
  and https://developers.cloudflare.com/fundamentals/account/account-security/audit-logs/
- DNS proxy status (proxied versus DNS-only): https://developers.cloudflare.com/dns/proxy-status/
- DNSSEC: https://developers.cloudflare.com/dns/dnssec/
- CAA records and Cloudflare's certificate authorities:
  https://developers.cloudflare.com/ssl/edge-certificates/caa-records/
- SSL/TLS encryption modes: https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/
- Authenticated Origin Pulls: https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/
- Protecting the origin server: https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/
- Cloudflare IP ranges (current list for origin allowlists): https://www.cloudflare.com/ips/
- WAF and rate limiting rules: https://developers.cloudflare.com/waf/
- API reference: https://developers.cloudflare.com/api/
- Product changelog: https://developers.cloudflare.com/changelog/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Certificate transparency search (for example https://crt.sh/): shows which hostnames under a domain have
  had certificates issued, which is how attackers find "hidden" tunnel hostnames. Useful for scoping and
  for spotting unexpected issuance; results include historical names and don't prove a name is live.
