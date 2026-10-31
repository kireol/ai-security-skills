# GPU Hosts: References

Always prefer current vendor documentation. GPU drivers, the Container Toolkit, and the GPU Operator
release often, and bulletins name specific branches. Re-verify links and contents when updating this
skill; record the date checked.

Last verified: 2026-10-31

## Vendor (authoritative)

- NVIDIA
  - Product security (security bulletins for GPU drivers, vGPU, Container Toolkit, GPU Operator, DCGM,
    Triton, Jetson, and more): https://www.nvidia.com/en-us/security/
  - Data center driver lifecycle (production branches, long-term support branches, end-of-life dates):
    https://docs.nvidia.com/datacenter/tesla/drivers/driver-lifecycle.html
  - Supported drivers and CUDA toolkit versions:
    https://docs.nvidia.com/datacenter/tesla/drivers/supported-drivers-and-cuda-toolkit-versions.html
  - NVIDIA Container Toolkit documentation (install, configuration, CDI):
    https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/
  - Container Toolkit specialized configuration (`NVIDIA_VISIBLE_DEVICES`, default value `all` in CUDA base
    images, runtime selection):
    https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html
  - GPU Operator documentation (time-slicing, MIG, security notes):
    https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/
  - MIG user guide: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/
  - DCGM Exporter installation (port 9400, remote host engine on 5555):
    https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html
- AMD
  - AMD product security bulletins: https://www.amd.com/en/resources/product-security.html
  - ROCm documentation and compatibility matrix: https://rocm.docs.amd.com/
- Jupyter
  - Jupyter Server security (tokens, passwords, bind address, XSRF):
    https://jupyter-server.readthedocs.io/en/latest/operators/security.html
  - JupyterHub security overview: https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html
- Ray
  - Ray security documentation (designed for trusted networks; job API runs code):
    https://docs.ray.io/en/latest/ray-security/index.html

Generic vulnerability and incident sources (CISA KEV, NVD, CVE, CISA ransomware guidance, IC3) are listed in
the core documents.

## Third-party (not authoritative)

- Wiz research on the NVIDIA Container Toolkit container-escape class ("NVIDIAScape"):
  https://www.wiz.io/blog/nvidia-ai-vulnerability-cve-2025-23266-nvidiascape
  Useful explanation of why toolkit hooks matter; take affected and fixed versions from NVIDIA's bulletin.
- Bottlerocket NVIDIA container runtime settings (documents the env-var and volume-mount options and
  defaults for that OS): https://bottlerocket.dev/en/os/1.46.x/api/settings/nvidia-container-runtime/
  Defaults there may differ from the upstream toolkit; check NVIDIA's documentation for the installed
  version.

## Not verified when writing this skill

- Default values of `accept-nvidia-visible-devices-envvar-when-unprivileged` and
  `accept-nvidia-visible-devices-as-volume-mounts` in the current upstream toolkit release.
- Default bind addresses of `dcgm-exporter` and `nv-hostengine` on the current release.
- Sunshine's default web UI port on the current release.
- Whether the installed Ray version supports built-in authentication.
