# MyAI - Environment Report

## Hardware

| Component | Details |
|-----------|---------|
| **OS** | Windows Server 2025 (Build 26100) |
| **CPU** | AMD EPYC 9J14 (3 cores / 6 threads, 2.6 GHz) |
| **RAM** | 55 GB total / 37 GB available |
| **GPU** | None (cloud VM - Microsoft Basic Display Adapter) |
| **Disk** | 200 GB total / 17 GB free |
| **CUDA** | Not available |
| **ROCm** | Not available |

## Software

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.14.7 | Installed |
| Node.js | 24.19.0 | Installed |
| Git | 2.55.0 | Installed |
| CMake | 4.4.3 | Installed |
| Docker | N/A | Not installed |

## Constraints

- **No GPU** - CPU-only inference
- **Limited disk** - 17 GB free (cannot run 7B+ models)
- **Cloud VM** - no direct Android USB connection
- **No Docker** - must run services natively

## Model Recommendation

Given 17 GB free disk and CPU-only:
- **Phi-3.5-mini** (Q4_K_M, ~2.3 GB) - best reasoning for size
- **Gemma 2 2B** (Q4_K_M, ~1.7 GB) - lightweight alternative
- **Qwen2.5-3B** (Q4_K_M, ~2.0 GB) - good multilingual

**Selected: Qwen2.5-3B-Instruct Q4_K_M** (~2 GB, good reasoning + tool calling)
