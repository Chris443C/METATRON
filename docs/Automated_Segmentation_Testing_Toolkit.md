# Automated Segmentation Testing Toolkit
PCI DSS • On-Prem • Cloud • Jump Host • Kubernetes • PowerShell

Author: Chris Ince Toolkit Draft
Version: 1.0

---

## Purpose

This document defines an **Automated Segmentation Testing Toolkit** intended to support controlled, defensible, low-impact segmentation validation across:

- On-prem networks
- PCI DSS CDE boundaries
- AWS
- Azure
- GCP
- Jump host / bastion paths
- Kubernetes and container estates
- Active Directory admin tiers

The toolkit is designed to support:

- PCI DSS Requirement 11.4.5 style segmentation validation
- QSA evidence gathering
- Repeatable internal security testing
- Safe production-friendly connectivity validation
- Standardised output for reporting and retest

---

## Core Design Principles

The toolkit should be:

- **Non-intrusive by default**
- **Read-only wherever possible**
- **Evidence-driven**
- **Repeatable**
- **Environment-aware**
- **Operator-controlled**
- **Suitable for production use when approved**

The toolkit should avoid:

- persistence
- payload deployment
- credential dumping
- destructive actions
- uncontrolled scanning
- noisy exploitation activity

---

## Toolkit Objectives

The automation layer should:

1. Read a defined segmentation test matrix
2. Execute approved connectivity tests
3. Record blocked vs allowed paths
4. Standardise evidence output
5. Generate report-ready summaries
6. Support retesting after remediation
7. Support multiple environments from one framework

---

## Recommended Toolkit Architecture

```text
Test Definition File
        |
        v
Execution Engine
        |
        +-- On-Prem Module
        +-- PowerShell Module
        +-- Ncat / TCP Module
        +-- AWS Module
        +-- Azure Module
        +-- GCP Module
        +-- Jump Host Module
        +-- Kubernetes Module
        |
        v
Results Normalisation Layer
        |
        v
Evidence Output
        |
        +-- CSV
        +-- JSON
        +-- Markdown Summary
        +-- Analyst Notes
```

---

## Recommended File Structure

```text
segmentation-toolkit/
├── config/
│   ├── test-matrix.csv
│   ├── toolkit-settings.json
│   └── environments.json
├── scripts/
│   ├── Invoke-SegmentationTest.ps1
│   ├── Test-TcpPath.ps1
│   ├── Test-JumpHostPath.ps1
│   ├── Test-AwsSegmentation.ps1
│   ├── Test-AzureSegmentation.ps1
│   ├── Test-GcpSegmentation.ps1
│   ├── Test-KubernetesSegmentation.ps1
│   └── Write-SegmentationReport.ps1
├── output/
│   ├── raw/
│   ├── normalised/
│   ├── evidence/
│   └── reports/
└── docs/
    ├── methodology.md
    └── operator-guide.md
```

---

## Test Matrix Format

A CSV-driven model is the cleanest option.

### Example `test-matrix.csv`

```csv
TestID,SourceName,SourceType,DestinationName,DestinationIP,Port,Protocol,ExpectedResult,Environment,Notes
T001,Corporate-LAN,OnPrem,CDE-Web01,10.10.20.15,443,TCP,Blocked,Production,Corporate should not reach CDE
T002,JumpHost-01,JumpHost,CDE-Web01,10.10.20.15,443,TCP,Allowed,Production,Approved admin path
T003,Guest-WiFi,OnPrem,CDE-DB01,10.10.20.25,1433,TCP,Blocked,Production,Guest isolation validation
T004,Azure-Admin-Subnet,Azure,Azure-CDE-App,10.50.4.10,443,TCP,Allowed,Azure,Expected management path
T005,AWS-App-Subnet,AWS,AWS-CDE-DB,10.60.5.21,5432,TCP,Blocked,AWS,App subnet should not hit DB directly
T006,K8s-TestPod,Kubernetes,Payment-API,10.70.8.12,443,TCP,Blocked,Kubernetes,Namespace isolation check
```

---

## Execution Model

Each row in the test matrix should trigger:

1. Selection of the correct module
2. Controlled TCP connectivity test
3. Timestamp capture
4. Result comparison against expected state
5. Output write to standard structure

### Standard result states

- `PASS` — observed result matched expectation
- `FAIL` — observed result did not match expectation
- `ERROR` — test could not be completed reliably
- `SKIPPED` — test intentionally not run

---

## PowerShell as the Primary Orchestrator

For your environment, **PowerShell is the best control layer** because it handles:

- Windows estates
- Azure estates
- CLI invocation
- CSV parsing
- JSON output
- evidence generation
- easy packaging for consultants

### Core orchestrator

Recommended main script:

- `Invoke-SegmentationTest.ps1`

This should:
- import config
- loop through test matrix rows
- call module-specific functions
- collect results
- export normalised output
- generate markdown evidence summary

---

## PowerShell Example: Core TCP Test Function

```powershell
function Test-TcpPath {
    param(
        [Parameter(Mandatory)]
        [string]$ComputerName,

        [Parameter(Mandatory)]
        [int]$Port
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    try {
        $result = Test-NetConnection -ComputerName $ComputerName -Port $Port -WarningAction SilentlyContinue

        [PSCustomObject]@{
            Timestamp        = $timestamp
            Destination      = $ComputerName
            Port             = $Port
            TcpTestSucceeded = [bool]$result.TcpTestSucceeded
            RemoteAddress    = $result.RemoteAddress
            SourceAddress    = $result.SourceAddress
            TestMethod       = "Test-NetConnection"
            Status           = "Complete"
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
            TestMethod       = "Test-NetConnection"
            Status           = "Error"
            Error            = $_.Exception.Message
        }
    }
}
```

---

## PowerShell Example: Matrix Execution Wrapper

```powershell
$tests = Import-Csv ".\config\test-matrix.csv"
$results = @()

foreach ($test in $tests) {
    $tcpResult = Test-TcpPath -ComputerName $test.DestinationIP -Port ([int]$test.Port)

    $observed = if ($tcpResult.TcpTestSucceeded) { "Allowed" } else { "Blocked" }
    $status = if ($observed -eq $test.ExpectedResult) { "PASS" } else { "FAIL" }

    $results += [PSCustomObject]@{
        TestID          = $test.TestID
        Timestamp       = $tcpResult.Timestamp
        SourceName      = $test.SourceName
        SourceType      = $test.SourceType
        DestinationName = $test.DestinationName
        DestinationIP   = $test.DestinationIP
        Port            = $test.Port
        Protocol        = $test.Protocol
        ExpectedResult  = $test.ExpectedResult
        ObservedResult  = $observed
        Outcome         = $status
        Environment     = $test.Environment
        Notes           = $test.Notes
    }
}

$results | Export-Csv ".\output\normalised\segmentation-results.csv" -NoTypeInformation
$results | ConvertTo-Json -Depth 5 | Out-File ".\output\normalised\segmentation-results.json"
```

---

## Ncat Integration

Ncat should be treated as the **explicit listener or socket validation layer** for cases where you want stronger proof than a simple client-side connection test.

### Use cases
- proving CDE reachability
- proving failed segmentation
- validating allowed admin path
- proving one-way versus two-way access

### Example destination listener

```bash
ncat -lvnp 4444
```

### Example source connection

```bash
ncat 10.10.20.15 4444
```

### Recommended approach

Use PowerShell to:
- register the test
- invoke the source-side check
- record the result
- reference screenshot or listener evidence file

Ncat is especially useful where you need a cleaner demonstration for a client or ROC narrative.

---

## AWS Module Design

### Objectives
Validate:
- VPC boundary behaviour
- security group enforcement
- route controls
- private endpoint restrictions
- Transit Gateway pathing
- EC2 to EC2 segmentation
- management path restrictions

### Inputs
- AWS profile or role
- region
- source workload or test host
- destination private IP or service
- approved ports

### Suggested commands
- `aws ec2 describe-instances`
- `aws ec2 describe-security-groups`
- `aws ec2 describe-route-tables`
- `aws ec2 describe-network-acls`

### PowerShell integration pattern

The PowerShell module should:
1. enumerate the target estate
2. resolve destination metadata
3. optionally run a connectivity check from an approved test instance
4. record findings alongside config context

### Important note

For AWS, connectivity evidence is strongest when paired with:
- actual test result
- security group review
- route table review
- subnet context

---

## Azure Module Design

### Objectives
Validate:
- VNET and subnet isolation
- NSG enforcement
- Azure Firewall rules
- Private Endpoint restrictions
- peering behaviour
- jump/admin path restriction
- management plane exposure

### Suggested commands
- `az vm list`
- `az network vnet list`
- `az network nsg list`
- `az network nic list`
- `az network route-table list`

### PowerShell modules
- `Az.Accounts`
- `Az.Network`
- `Az.Compute`
- `Az.Resources`

### Best fit for your workflow

Azure is especially well suited to a PowerShell-led approach because you can:
- authenticate cleanly
- export rich resource context
- produce evidence tables quickly
- build repeatable consultant-led scripts

---

## GCP Module Design

### Objectives
Validate:
- project-level segmentation
- VPC firewall enforcement
- service exposure
- private service connectivity
- workload isolation
- service account adjacency risks

### Suggested commands
- `gcloud compute instances list`
- `gcloud compute firewall-rules list`
- `gcloud compute networks subnets list`

### Recommended output
The GCP module should produce:
- target inventory summary
- firewall context
- connectivity test result
- note on expected segmentation model

---

## Jump Host Module Design

### Objective

Validate that access to sensitive systems is only available through approved bastion or jump infrastructure.

### Tests
- jump host to CDE: expected allowed
- corporate LAN to CDE: expected blocked
- admin workstation direct to CDE: expected blocked unless explicitly authorised
- reverse path where relevant

### Evidence to collect
- source host identity
- destination host
- tested port
- observed result
- screenshot or command output
- access path explanation

This is particularly useful in your PCI work where clients often claim “all admin access goes through the jump host” and the test needs to prove that properly.

---

## Kubernetes Module Design

### Objectives
Validate:
- namespace isolation
- network policies
- pod-to-pod reachability restrictions
- service exposure boundaries
- admin namespace separation
- egress restrictions

### Suggested commands
- `kubectl get pods -A`
- `kubectl get networkpolicy -A`
- `kubectl exec`
- `kubectl run`

### Example test pod

```bash
kubectl run net-test --image=alpine --restart=Never -- sleep 3600
kubectl exec net-test -- nc -zv 10.70.8.12 443
```

### Output
The module should record:
- source pod / namespace
- destination service or IP
- port
- expected result
- observed result
- related network policy reference if known

---

## Active Directory Segmentation Module

### Objectives
Validate:
- privileged admin tier separation
- workstation to DC restrictions
- server-to-DC access limits
- admin jump path enforcement
- management port control

### Tests
Common ports:
- 445
- 3389
- 5985 / 5986
- 135
- 389 / 636
- 88

### Example PowerShell test

```powershell
Test-NetConnection -ComputerName 10.10.30.10 -Port 445
```

### Evidence benefit
This supports narratives around:
- admin path hygiene
- privileged access control
- weak internal segmentation
- improper workstation-to-DC trust

---

## Output and Evidence Standards

The toolkit should generate at least four outputs.

### 1. Raw CSV results
Machine-friendly export of every test.

### 2. JSON results
Useful for future AI correlation and dashboards.

### 3. Markdown analyst summary
Human-readable summary of:
- tests run
- passes
- fails
- errors
- notable failed controls

### 4. Evidence-ready table
A concise report appendix format.

### Example evidence table

| Test ID | Source | Destination | Port | Expected | Observed | Outcome |
|---|---|---|---:|---|---|---|
| T001 | Corporate-LAN | CDE-Web01 | 443 | Blocked | Allowed | FAIL |
| T002 | JumpHost-01 | CDE-Web01 | 443 | Allowed | Allowed | PASS |

---

## Markdown Report Generation

The toolkit should automatically generate a markdown summary like this:

```markdown
# Segmentation Test Summary

## Overview
- Total tests: 12
- PASS: 9
- FAIL: 2
- ERROR: 1

## Notable Failures
- Corporate-LAN was able to reach CDE-Web01 on TCP 443
- Guest-WiFi was able to reach CDE-DB01 on TCP 1433

## Observations
The failed tests indicate that segmentation controls are not fully enforced between non-CDE networks and CDE systems.
```

---

## Recommended MVP

The first build should cover:

### Phase 1
- CSV-driven test matrix
- PowerShell TCP testing
- CSV and JSON export
- markdown summary output

### Phase 2
- Ncat-assisted proof mode
- jump host path testing
- richer evidence logging

### Phase 3
- AWS/Azure/GCP enumeration helpers
- Kubernetes module
- AD/admin tier module

### Phase 4
- AI-assisted result correlation
- attack-path clustering
- report draft generation

---

## Best Language Choices

### Primary
- **PowerShell** for orchestration, Windows estates, Azure, and reporting

### Secondary
- **Python** if you later want:
  - dashboards
  - richer parsing
  - cross-platform packaging
  - web front end

### Utility tools
- Ncat
- Nmap
- kubectl
- AWS CLI
- Azure CLI
- gcloud

For your immediate use, I would start with **PowerShell first**.

---

## Recommended Naming

Suggested project name:

**SegTest-QSA**

Alternative names:
- PCI-Seg-Toolkit
- BoundaryProof
- Segmentation Validator
- ScopeGuard

`SegTest-QSA` is probably the cleanest for internal use.

---

## Risks and Controls

### Risks
- false confidence from testing only one port
- results misread due to transient firewall behaviour
- source host not actually in the claimed zone
- cloud path misunderstood due to routing complexity
- Kubernetes test pod placed in wrong namespace

### Controls
- validate source host placement before testing
- test multiple representative ports
- capture target metadata
- log timestamp and operator
- pair technical results with architecture review
- repeat critical failures before final reporting

---

## Recommended Next Deliverables

1. `Invoke-SegmentationTest.ps1`
2. `test-matrix.csv` template
3. markdown report generator
4. jump host test module
5. AWS / Azure / GCP helper modules
6. operator guide
7. evidence pack template

---

## Straight recommendation

For your work, the best first implementation is:

- **PowerShell-based**
- **CSV-driven**
- **Ncat-enhanced**
- **cloud-aware**
- **markdown-reporting by default**

That gives you a practical toolkit you can use in real assessments without overengineering it.

---

## Next Build Step

After this design, the natural next move is to generate:

1. the **actual PowerShell toolkit skeleton**
2. the **CSV template**
3. the **reporting template**
4. the **module stubs for AWS, Azure, GCP, Jump Host, and Kubernetes**

That would turn this from methodology into a working starter pack.
