function Test-JumpHostPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [pscustomobject]$TestRow,

        [Parameter(Mandatory)]
        [string]$RootPath,

        [int]$TimeoutSeconds = 5
    )

    . (Join-Path $RootPath "scripts\Test-TcpPath.ps1")

    $baseResult = Test-TcpPath -ComputerName $TestRow.DestinationIP -Port ([int]$TestRow.Port) -TimeoutSeconds $TimeoutSeconds
    $observed = if ($baseResult.TcpTestSucceeded) { "Allowed" } else { "Blocked" }

    [PSCustomObject]@{
        TestID          = $TestRow.TestID
        Timestamp       = $baseResult.Timestamp
        SourceName      = $TestRow.SourceName
        SourceType      = $TestRow.SourceType
        DestinationName = $TestRow.DestinationName
        DestinationIP   = $TestRow.DestinationIP
        Port            = [int]$TestRow.Port
        Protocol        = $TestRow.Protocol
        ExpectedResult  = $TestRow.ExpectedResult
        ObservedResult  = $observed
        Outcome         = if ($observed -eq $TestRow.ExpectedResult) { "PASS" } else { "FAIL" }
        Environment     = $TestRow.Environment
        Notes           = $TestRow.Notes
        TestMethod      = "JumpHostWrapper"
        EvidenceHint    = "Run from the actual jump host for defensible evidence."
    }
}
