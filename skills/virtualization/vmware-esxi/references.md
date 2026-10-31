# VMware ESXi: References

Always prefer current Broadcom documentation. Licensing, patch access, and download locations have
changed several times since the Broadcom acquisition; re-verify every link and policy when using this
skill.

Last verified: 2026-10-31

## Vendor (authoritative)

- VMware Security Advisories (VMSAs) on the Broadcom support portal:
  https://support.broadcom.com/web/ecx/security-advisory?segment=VC
- Broadcom product lifecycle (end of general support dates): https://support.broadcom.com/group/ecx/productlifecycle
- End of general support for vSphere 7.0: https://knowledge.broadcom.com/external/article/415405
- Unified VCF versioning in ESX releases (9.x naming): https://knowledge.broadcom.com/external/article/395110
- ESXi and vSphere technical documentation (security, lockdown mode, ESXi firewall, accounts):
  https://techdocs.broadcom.com/
- vSphere / VCF security configuration and hardening guides, VMSA notes, and ransomware resources
  (official Broadcom repository): https://github.com/vmware/vcf-security-and-compliance-guidelines
- How to disable or enable the SLP service on ESXi: https://knowledge.broadcom.com/external/article/318790
- Network ports for VMware products: https://ports.broadcom.com/
- Broadcom Support Portal (downloads, free vSphere Hypervisor edition, entitlement):
  https://support.broadcom.com/

## Upstream and government

- CISA Known Exploited Vulnerabilities catalog (search for VMware ESXi and vCenter):
  https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- IEEE OUI registry (to confirm MAC prefix owners): https://regauth.standards.ieee.org/standards-ra-web/pub/view.html#registries

BMC vendors (Dell iDRAC, HPE iLO, Lenovo XClarity, Supermicro and others) publish their own security
advisories and hardening guides; use the current page for the specific server model.

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Rapid7, CVE-2024-37085 (directory admin group) targeted in ransomware campaigns:
  https://www.rapid7.com/blog/post/2024/07/30/vmware-esxi-cve-2024-37085-targeted-in-ransomware-campaigns/
  Good summary of the attack path; use the Broadcom advisory for the fix.
- The Register, free ESXi edition reinstated (2025-04):
  https://www.theregister.com/2025/04/14/vmware_free_esxi_returns/ Context on the free edition; confirm
  current availability on the Broadcom portal.
- vninja.net, Broadcom statement on security patches for expired-support customers (2024-04):
  https://vninja.net/2024/04/16/vmware-by-broadcom-promises-security-updates Context only; verify the
  current policy with Broadcom.
- endoflife.date, ESXi release summary: https://endoflife.date/esxi Convenient overview; confirm dates on
  the Broadcom lifecycle page.
- VMware ESXi patch tracker (v-front): https://esxi-patches.v-front.de/ Build-number history; confirm
  against Broadcom release notes.
