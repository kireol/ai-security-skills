# Smart TVs and Streaming Devices: References

Always prefer the platform's and TV maker's current support pages; settings menus change with every OS
release and differ between brands using the same platform. Re-verify links and contents when updating
this skill.

Last verified: 2026-10-30

## Vendor (authoritative for their own products)

- Roku, External Control Protocol (ECP, TCP 8060; commands that need "control by mobile apps"):
  https://developer.roku.com/docs/developer-program/discovery/external-control-api.md
- Roku, controlling a Roku device with an app (External Control network-access options):
  https://support.roku.com/en-gb/article/can-my-roku-streaming-device-be-controlled-using-an-app
- Google TV, ad settings (advertising ID reset or delete; ads can't be turned off):
  https://support.google.com/googletv/answer/13392198
- Android TV, ad settings: https://support.google.com/androidtv/answer/10012572
- Amazon Fire TV, connecting through ADB (where ADB debugging and unknown-sources settings live):
  https://developer.amazon.com/docs/fire-tv/connecting-adb-to-device.html
- Apple, TCP and UDP ports used by Apple software products (AirPlay, Bonjour):
  https://support.apple.com/en-us/103229
- For every TV maker: look for its security or vulnerability-disclosure page, its software-update support
  policy (years of updates per model year), and its privacy settings help pages. Samsung announced seven
  years of Tizen OS updates for recent models in 2024, and LG runs a webOS upgrade program for recent
  models; verify the current scope and model years on the vendors' own pages.

## Regulators and government (factual history)

- FTC and New Jersey, Vizio settlement (2017): viewing data collected from about 11 million TVs without
  consumers' consent through automated content recognition:
  https://www.ftc.gov/news-events/news/press-releases/2017/02/vizio-pay-22-million-ftc-state-new-jersey-settle-charges-it-collected-viewing-histories-11-million
- FBI / IC3 public service announcement on BADBOX 2.0 (June 2025): uncertified Android TV boxes and other
  devices with preinstalled or app-delivered malware used as residential proxies; warning signs include
  devices that require Play Protect to be disabled: https://www.ic3.gov/PSA/2025/PSA250605

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- TechRadar, Texas Attorney General lawsuits against five TV makers over ACR (December 2025):
  https://www.techradar.com/televisions/your-tv-is-a-mass-surveillance-system-says-texas-and-the-state-is-suing-lg-samsung-hisense-tcl-and-more-to-stop-it
  Litigation status may have changed; check the Texas Attorney General's site.
- TechRadar, Samsung's seven-year TV update commitment:
  https://www.techradar.com/televisions/samsung-promises-free-updates-for-its-tvs-for-7-years-fixing-one-of-their-biggest-issues
- Tom's Guide, Samsung and LG software support compared:
  https://tomsguide.com/tvs/samsung-one-ups-lg-with-a-7-year-software-support-promise-for-its-smart-tvs
- Radware, ADB.Miner botnet (2018) spreading through exposed Android ADB on TCP 5555, including TVs and
  set-top boxes: https://www.radware.com/security/ddos-threats-attacks/threat-advisories-attack-reports/adb-miner/
  Historical; illustrates the risk, not current prevalence.
- Consumer Reports, how to turn off smart TV snooping features:
  https://www.consumerreports.org/electronics/privacy/how-to-turn-off-smart-tv-snooping-features-a4840102036/
  Brand-by-brand menu paths; may be paywalled and menus change yearly.
