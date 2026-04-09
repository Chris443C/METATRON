function Write-SegmentationReport {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [array]$Results,

        [Parameter(Mandatory)]
        [string]$ReportPath,

        [string]$Title = "Segmentation Test Summary"
    )

    $total = $Results.Count
    $pass = ($Results | Where-Object Outcome -eq "PASS").Count
    $fail = ($Results | Where-Object Outcome -eq "FAIL").Count
    $error = ($Results | Where-Object Outcome -eq "ERROR").Count
    $skipped = ($Results | Where-Object Outcome -eq "SKIPPED").Count

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# $Title")
    $lines.Add("")
    $lines.Add("## Overview")
    $lines.Add("- Total tests: $total")
    $lines.Add("- PASS: $pass")
    $lines.Add("- FAIL: $fail")
    $lines.Add("- ERROR: $error")
    $lines.Add("- SKIPPED: $skipped")
    $lines.Add("")

    $failures = $Results | Where-Object Outcome -eq "FAIL"
    if ($failures.Count -gt 0) {
        $lines.Add("## Notable Failures")
        foreach ($f in $failures) {
            $lines.Add("- $($f.SourceName) reached $($f.DestinationName) ($($f.DestinationIP)) on TCP $($f.Port) when the expected result was $($f.ExpectedResult).")
        }
        $lines.Add("")
    }

    $lines.Add("## Detailed Results")
    $lines.Add("")
    $lines.Add("| Test ID | Source | Destination | Port | Expected | Observed | Outcome |")
    $lines.Add("|---|---|---|---:|---|---|---|")
    foreach ($r in $Results) {
        $lines.Add("| $($r.TestID) | $($r.SourceName) | $($r.DestinationName) | $($r.Port) | $($r.ExpectedResult) | $($r.ObservedResult) | $($r.Outcome) |")
    }
    $lines.Add("")
    $lines.Add("## Analyst Notes")
    $lines.Add("Pair failed connectivity tests with firewall, routing, and source-host placement validation before final reporting.")

    $lines -join [Environment]::NewLine | Out-File -FilePath $ReportPath -Encoding utf8
}
