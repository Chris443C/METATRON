function Test-AzureSegmentation {
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
        Notes           = "$($TestRow.Notes) | Azure helper stub: extend with Az module and NSG/VNET context."
        TestMethod      = "AzureHelperStub"
    }
}
