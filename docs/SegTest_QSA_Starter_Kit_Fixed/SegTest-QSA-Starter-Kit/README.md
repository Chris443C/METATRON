# SegTest-QSA Starter Kit

A PowerShell-first starter kit for controlled segmentation testing across on-prem, jump host, cloud, Kubernetes, and Active Directory environments.

## Contents

- `config/test-matrix.csv` — sample test matrix
- `config/toolkit-settings.json` — basic toolkit settings
- `config/environments.json` — environment metadata
- `scripts/Invoke-SegmentationTest.ps1` — main orchestrator
- `scripts/Test-TcpPath.ps1` — reusable TCP connectivity function
- `scripts/Test-JumpHostPath.ps1` — jump host wrapper
- `scripts/Test-AwsSegmentation.ps1` — AWS helper stub
- `scripts/Test-AzureSegmentation.ps1` — Azure helper stub
- `scripts/Test-GcpSegmentation.ps1` — GCP helper stub
- `scripts/Test-KubernetesSegmentation.ps1` — Kubernetes helper stub
- `scripts/Write-SegmentationReport.ps1` — markdown report writer
- `docs/operator-guide.md` — operator guide

## Quick start

1. Review and update:
   - `config/test-matrix.csv`
   - `config/toolkit-settings.json`
   - `config/environments.json`

2. Open PowerShell and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Invoke-SegmentationTest.ps1 -RootPath .
```

3. Review outputs:
   - `output/normalised/segmentation-results.csv`
   - `output/normalised/segmentation-results.json`
   - `output/reports/segmentation-summary.md`

## Notes

- Default execution uses `Test-NetConnection` for low-impact TCP validation.
- Cloud and Kubernetes modules are helper stubs ready for expansion.
- The toolkit is deliberately non-intrusive by default.
