function Test-TcpPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ComputerName,

        [Parameter(Mandatory)]
        [int]$Port,

        [int]$TimeoutSeconds = 5
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    try {
        $result = Test-NetConnection -ComputerName $ComputerName -Port $Port -WarningAction SilentlyContinue -InformationLevel Detailed

        [PSCustomObject]@{
            Timestamp        = $timestamp
            Destination      = $ComputerName
            Port             = $Port
            TcpTestSucceeded = [bool]$result.TcpTestSucceeded
            RemoteAddress    = $result.RemoteAddress
            SourceAddress    = $result.SourceAddress
            InterfaceAlias   = $result.InterfaceAlias
            TestMethod       = "Test-NetConnection"
            Status           = "Complete"
            Error            = $null
        }
    }
    catch {
        [PSCustomObject]@{
            Timestamp        = $timestamp
            Destination      = $ComputerName
            Port             = $Port
            TcpTestSucceeded = $false
            RemoteAddress    = $null
            SourceAddress    = $null
            InterfaceAlias   = $null
            TestMethod       = "Test-NetConnection"
            Status           = "Error"
            Error            = $_.Exception.Message
        }
    }
}
