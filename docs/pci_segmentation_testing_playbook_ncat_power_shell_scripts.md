# PCI Segmentation Testing Playbook
Ncat • PowerShell • Standard Testing Scripts

---

# Executive Summary

This playbook provides:

1. PCI Segmentation Testing Methodology
2. Ncat Testing Scripts
3. PowerShell Segmentation Toolkit
4. Evidence Collection Templates
5. Standard Testing Matrix
6. QSA‑Friendly Testing Approach

---

# 1. PCI Segmentation Testing Methodology

## Objective

Validate segmentation controls between:

- Corporate networks
- Guest networks
- Development environments
- CDE environments
- Security‑impacting systems

---

## High Level Process

1. Identify segmentation boundaries
2. Deploy test listener
3. Execute connectivity tests
4. Record results
5. Validate firewall rules
6. Document findings

---

# 2. Standard Segmentation Test Matrix

| Source Network | Destination | Expected Result |
|----------------|-------------|-----------------|
| Corporate | CDE | Blocked |
| Guest WiFi | CDE | Blocked |
| Dev | Production | Blocked |
| Corporate | Jump Host | Allowed |
| Jump Host | CDE | Allowed |

---

# 3. Ncat Segmentation Testing

## Listener (Destination System)

Linux:

```
ncat -lvnp 4444
```

Windows:

```
ncat.exe -lvnp 4444
```

---

## Connectivity Test

From Source System:

```
ncat <target-ip> 4444
```

Expected:

Blocked = Segmentation Working
Connected = Segmentation Failure

---

# 4. Multi-Port Testing Script

Linux Bash Script

```
#!/bin/bash
TARGET=$1
PORTS="22 80 443 3389 445"

for port in $PORTS
do
 echo "Testing port $port"
 ncat -zv $TARGET $port
 done
```

---

# 5. Reverse Connectivity Testing

Test both directions:

Source → Destination
Destination → Source

This validates:

- One way segmentation
- Bidirectional controls

---

# 6. PowerShell Segmentation Toolkit

## Single Port Test

```
Test-NetConnection 10.10.10.20 -Port 4444
```

---

## Multi Port Script

```
$Target = "10.10.10.20"
$Ports = 22,80,443,3389,445

foreach ($Port in $Ports)
{
    Test-NetConnection -ComputerName $Target -Port $Port
}
```

---

# 7. Advanced PowerShell Segmentation Script

```
$Targets = @(
    "10.10.10.20",
    "10.10.10.21"
)

$Ports = @(22,80,443,3389,445)

foreach ($Target in $Targets)
{
    foreach ($Port in $Ports)
    {
        $Result = Test-NetConnection -ComputerName $Target -Port $Port

        [PSCustomObject]@{
            Target = $Target
            Port = $Port
            Success = $Result.TcpTestSucceeded
        }
    }
}
```

---

# 8. Evidence Collection

Capture:

- Source system
- Destination system
- Timestamp
- Port tested
- Result

---

# 9. Evidence Table Template

| Source | Destination | Port | Result | Notes |
|--------|-------------|------|--------|------|
| Corp | CDE | 4444 | Blocked | Expected |
| Corp | CDE | 3389 | Allowed | Failure |

---

# 10. Example QSA Narrative

Segmentation testing was performed using controlled TCP connectivity testing between corporate and CDE networks. Testing confirmed that direct connectivity from corporate networks to CDE systems was blocked in accordance with segmentation controls.

---

# 11. Automation Script (Combined)

```
$Sources = @(
    "Corporate",
    "Guest",
    "Dev"
)

$Targets = @(
    "10.10.10.20",
    "10.10.10.21"
)

$Ports = @(22,80,443,3389,445)

foreach ($Target in $Targets)
{
    foreach ($Port in $Ports)
    {
        Test-NetConnection -ComputerName $Target -Port $Port
    }
}
```

---

# 12. Recommended Tools

Primary

- Ncat
- Nmap
- PowerShell

Optional

- curl
- hping3

---

# 13. Recommended Testing Workflow

Step 1 — Confirm scope
Step 2 — Deploy listener
Step 3 — Test connectivity
Step 4 — Capture evidence
Step 5 — Document results
Step 6 — Remove test listener

---

# 14. Safety Guidelines

- Non intrusive testing
- No persistence
- No exploitation
- Approved scope only

---

# End of Playbook

