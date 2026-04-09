[CmdletBinding()]
param(
    [string]$RootPath = $(Split-Path -Parent $PSScriptRoot)
)

$configPath = Join-Path $RootPath "config\toolkit-settings.json"
$matrixPath = Join-Path $RootPath "config\test-matrix.csv"
$outputNormalised = Join-Path $RootPath "output\normalised"
$outputReports = Join-Path $RootPath "output\reports"

. (Join-Path $RootPath "scripts\Test-TcpPath.ps1")
. (Join-Path $RootPath "scripts\Test-JumpHostPath.ps1")
. (Join-Path $RootPath "scripts\Test-AwsSegmentation.ps1")
. (Join-Path $RootPath "scripts\Test-AzureSegmentation.ps1")
. (Join-Path $RootPath "scripts\Test-GcpSegmentation.ps1")
. (Join-Path $RootPath "scripts\Test-KubernetesSegmentation.ps1")
. (Join-Path $RootPath "scripts\Write-SegmentationReport.ps1")

if (-not (Test-Path $configPath)) {
    throw "Toolkit settings file not found: $configPath"
}

if (-not (Test-Path $matrixPath)) {
    throw "Test matrix file not found: $matrixPath"
}

$settings = Get-Content $configPath -Raw | ConvertFrom-Json
$tests = Import-Csv $matrixPath
$results = @()

foreach ($test in $tests) {
    Write-Host "Running $($test.TestID) from $($test.SourceName) to $($test.DestinationName):$($test.Port)"

    switch ($test.SourceType) {
        "JumpHost" {
            $result = Test-JumpHostPath -TestRow $test -RootPath $RootPath -TimeoutSeconds $settings.DefaultTimeoutSeconds
        }
        "AWS" {
            $result = Test-AwsSegmentation -TestRow $test
        }
        "Azure" {
            $result = Test-AzureSegmentation -TestRow $test
        }
        "GCP" {
            $result = Test-GcpSegmentation -TestRow $test
        }
        "Kubernetes" {
            $result = Test-KubernetesSegmentation -TestRow $test
        }
        default {
            $tcpResult = Test-TcpPath -ComputerName $test.DestinationIP -Port ([int]$test.Port) -TimeoutSeconds $settings.DefaultTimeoutSeconds
            $observed = if ($tcpResult.TcpTestSucceeded) { "Allowed" } else { "Blocked" }
            $outcome = if ($observed -eq $test.ExpectedResult) { "PASS" } else { "FAIL" }

            $result = [PSCustomObject]@{
                TestID          = $test.TestID
                Timestamp       = $tcpResult.Timestamp
                SourceName      = $test.SourceName
                SourceType      = $test.SourceType
                DestinationName = $test.DestinationName
                DestinationIP   = $test.DestinationIP
                Port            = [int]$test.Port
                Protocol        = $test.Protocol
                ExpectedResult  = $test.ExpectedResult
                ObservedResult  = $observed
                Outcome         = if ($tcpResult.Status -eq "Error") { "ERROR" } else { $outcome }
                Environment     = $test.Environment
                Notes           = $test.Notes
                TestMethod      = $tcpResult.TestMethod
                RemoteAddress   = $tcpResult.RemoteAddress
                SourceAddress   = $tcpResult.SourceAddress
                InterfaceAlias  = $tcpResult.InterfaceAlias
                Error           = $tcpResult.Error
            }
        }
    }

    if ($settings.RepeatFailures -and $result.Outcome -eq "FAIL" -and $test.SourceType -notin @("AWS", "Azure", "GCP", "Kubernetes")) {
        Start-Sleep -Seconds $settings.RepeatFailureDelaySeconds

        $retryTcp = Test-TcpPath -ComputerName $test.DestinationIP -Port ([int]$test.Port) -TimeoutSeconds $settings.DefaultTimeoutSeconds
        $retryObserved = if ($retryTcp.TcpTestSucceeded) { "Allowed" } else { "Blocked" }
        $retryOutcome = if ($retryObserved -eq $test.ExpectedResult) { "PASS" } else { "FAIL" }

        $result | Add-Member -NotePropertyName RetryObservedResult -NotePropertyValue $retryObserved -Force
        $result | Add-Member -NotePropertyName RetryOutcome -NotePropertyValue $retryOutcome -Force
    }

    $results += $result
}

if ($settings.CreateCsvOutput) {
    $results | Export-Csv (Join-Path $outputNormalised "segmentation-results.csv") -NoTypeInformation -Encoding utf8
}

if ($settings.CreateJsonOutput) {
    $results | ConvertTo-Json -Depth 6 | Out-File (Join-Path $outputNormalised "segmentation-results.json") -Encoding utf8
}

if ($settings.CreateMarkdownReport) {
    Write-SegmentationReport -Results $results -ReportPath (Join-Path $outputReports "segmentation-summary.md") -Title $settings.ReportTitle
}

Write-Host ""
Write-Host "Complete. Outputs written under:"
Write-Host " - $outputNormalised"
Write-Host " - $outputReports"
