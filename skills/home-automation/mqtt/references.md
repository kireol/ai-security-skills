# MQTT: References

Always prefer current broker documentation; Mosquitto 2.1 deprecated several options that 3.0 will remove.

Last verified: 2026-10-30

## Vendor (authoritative)

- Mosquitto configuration reference (`mosquitto.conf` man page: listeners, authentication, ACL format,
  TLS, bridges, logging, persistence): https://mosquitto.org/man/mosquitto-conf-5.html
- Mosquitto 2.0 migration notes (anonymous access and loopback-only defaults):
  https://mosquitto.org/documentation/migrating-to-2-0/
- Mosquitto authentication methods: https://mosquitto.org/documentation/authentication-methods/
- Mosquitto dynamic security plugin: https://mosquitto.org/documentation/dynamic-security/
- Mosquitto per-listener settings (deprecated in 2.1):
  https://mosquitto.org/documentation/listeners/per-listener-settings/
- `mosquitto_passwd` (hash algorithms, `-U`, `-b` warning): https://mosquitto.org/man/mosquitto_passwd-1.html
- Mosquitto 2.1.0 release notes: https://mosquitto.org/blog/2026/01/version-2-1-0-released/
- Mosquitto releases and security announcements: https://mosquitto.org/blog/
- Mosquitto GitHub security advisories page (security fixes are mainly announced on the blog and in the
  ChangeLog; the advisories page may be empty): https://github.com/eclipse-mosquitto/mosquitto/security/advisories
- Mosquitto ChangeLog: https://github.com/eclipse-mosquitto/mosquitto/blob/master/ChangeLog.txt
- Home Assistant Mosquitto broker app documentation:
  https://github.com/home-assistant/addons/blob/master/mosquitto/DOCS.md
- Home Assistant MQTT integration (discovery prefix, birth/will, TLS validation):
  https://www.home-assistant.io/integrations/mqtt/
- Zigbee2MQTT MQTT settings: https://www.zigbee2mqtt.io/guide/configuration/mqtt.html
- Zigbee2MQTT frontend (`auth_token`): https://www.zigbee2mqtt.io/guide/configuration/frontend.html
- Zigbee2MQTT topics and bridge requests: https://www.zigbee2mqtt.io/guide/usage/mqtt_topics_and_messages.html
- Frigate MQTT topics: https://docs.frigate.video/integrations/mqtt/

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- OASIS MQTT specifications (protocol behavior, retained messages, wildcards):
  https://mqtt.org/mqtt-specification/
  Useful for protocol semantics; broker-specific security settings come from each broker's own docs.
