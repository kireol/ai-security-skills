# Frigate NVR: References

Always prefer current Frigate documentation; ports, authentication behavior, and configuration keys
change between releases. Recent releases have shipped many security fixes, so read the notes for every
version between the installed one and the current one.

Last verified: 2026-10-30

## Vendor (authoritative)

- Security advisories (GitHub): https://github.com/blakeblackshear/frigate/security/advisories
- Release notes (list fixed advisories per release): https://github.com/blakeblackshear/frigate/releases
- Installation, ports table, Docker and Home Assistant app variants: https://docs.frigate.video/frigate/installation
- Authentication (ports 8971 and 5000, users, roles, rate limiting, proxy auth, JWT secret):
  https://docs.frigate.video/configuration/authentication
- TLS: https://docs.frigate.video/configuration/tls
- Restream and go2rtc (RTSP credentials, restricted stream sources): https://docs.frigate.video/configuration/restream
- Recording and retention: https://docs.frigate.video/configuration/record
- Generative AI providers: https://docs.frigate.video/configuration/genai/genai_config
- Network requirements (outbound connections and how to turn them off):
  https://docs-dev.frigate.video/frigate/network_requirements (development docs; check whether the
  stable docs have an equivalent page for the installed version)
- Home Assistant integration (which port to use, notification endpoints):
  https://docs.frigate.video/integrations/home-assistant

## Upstream components

- go2rtc (security section: default listeners, API risk, hardening options): https://github.com/AlexxIT/go2rtc

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- GitHub Discussions for Frigate (https://github.com/blakeblackshear/frigate/discussions): community
  answers on configuration such as environment-variable substitution. Useful for edge cases; confirm
  against the docs for the installed version.
