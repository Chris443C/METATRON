# Operator Guide

## Intended use

This toolkit is intended for:
- controlled segmentation validation
- low-impact evidence gathering
- retesting after remediation
- consultant-led execution

## Pre-run checks

Before running:
- confirm source host placement is correct
- confirm target IPs are accurate
- confirm ports are representative
- confirm testing approval exists
- confirm production safeguards are in place

## Running the toolkit

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Invoke-SegmentationTest.ps1 -RootPath .
```

## Interpreting results

- `PASS` means observed behaviour matched expected segmentation state.
- `FAIL` means segmentation did not behave as expected.
- `ERROR` means the test could not be completed reliably.
- `SKIPPED` means a helper stub exists but the real execution logic has not yet been implemented.

## Important cautions

- Do not rely on a single port for final conclusions.
- Pair failed tests with firewall and routing review.
- Re-run critical failures from the real source zone.
- For jump hosts, execute from the actual bastion rather than a proxy approximation.
- For cloud estates, pair connectivity tests with control-plane evidence.
