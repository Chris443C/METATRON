function Test-GcpSegmentation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [pscustomobject]$TestRow
    )

    [PSCustomObject]@{
        TestID          = $TestRow.TestID
        Timestamp       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        SourceName      = $TestRow.SourceName
        SourceType      = $TestRow.SourceType
        DestinationName = $TestRow.DestinationName
        DestinationIP   = $TestRow.DestinationIP
        Port            = [int]$TestRow.Port
        Protocol        = $TestRow.Protocol
        ExpectedResult  = $TestRow.ExpectedResult
        ObservedResult  = "NotRun"
        Outcome         = "SKIPPED"
        Environment     = $TestRow.Environment
        Notes           = "$($TestRow.Notes) | GCP helper stub: extend with gcloud inventory and firewall context."
        TestMethod      = "GCPHelperStub"
    }
}
