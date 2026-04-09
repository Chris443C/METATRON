function Test-KubernetesSegmentation {
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
        Notes           = "$($TestRow.Notes) | Kubernetes helper stub: execute from test pod and record namespace/policy context."
        TestMethod      = "KubernetesHelperStub"
    }
}
