# Complete Segmentation Testing Framework
PCI DSS • Cloud • Jump Host • Kubernetes • Enterprise

Author: Chris Ince (QSA Methodology Pack)
Version: 1.0

---

# Executive Summary

This framework provides a **complete segmentation testing methodology** covering:

- On‑Prem Network Segmentation
- PCI DSS CDE Segmentation
- Cloud Segmentation (AWS / Azure / GCP)
- Jump Host / Bastion Segmentation
- Kubernetes / Container Segmentation
- Active Directory Segmentation
- Zero‑Trust Segmentation
- Payment Flow Segmentation

This framework is designed for:

- PCI DSS Assessments
- QSA Segmentation Validation
- Internal Security Reviews
- Red Team Testing (Controlled)

---

# 1. Core Segmentation Testing Principles

Segmentation testing validates:

- Network isolation
- Access control enforcement
- Firewall rule effectiveness
- Routing restrictions
- Identity‑based segmentation

Key Questions:

- Can corporate users access CDE?
- Can guest networks access production?
- Can cloud workloads reach CDE?
- Can containers access sensitive services?

---

# 2. Core Testing Tools

Primary

- Ncat
- Nmap
- PowerShell Test‑NetConnection

Supporting

- curl
- nc
- hping3

Cloud

- AWS CLI
- Azure CLI
- gcloud

Container

- kubectl
- docker

---

# 3. On‑Prem Segmentation Testing

## Listener

```
ncat -lvnp 4444
```

## Test

```
ncat <target-ip> 4444
```

Expected

Blocked = Segmentation working

---

# 4. Cloud Segmentation Testing

## AWS

Test:

- VPC segmentation
- Security groups
- Private endpoints

Commands

```
aws ec2 describe-instances
```

---

## Azure

Test:

- VNET segmentation
- NSG rules

Commands

```
az vm list
```

---

## GCP

Commands

```
gcloud compute instances list
```

---

# 5. Jump Host Segmentation

Architecture

User → Jump Host → CDE

Test

Jump Host Allowed
Corporate Blocked

---

# 6. Kubernetes Segmentation

Deploy Test Pod

```
kubectl run test --image=alpine -- sleep 3600
```

Test

```
kubectl exec test -- nc <target-ip> 4444
```

---

# 7. Active Directory Segmentation

Validate:

- Admin tiering
- Privileged access
- Domain controller isolation

PowerShell

```
Test-NetConnection <dc-ip> -Port 445
```

---

# 8. Zero‑Trust Segmentation

Validate:

- Identity based controls
- Conditional access
- Device trust

---

# 9. Payment Flow Segmentation

Validate:

- Payment pages isolated
- Tokenization segmentation
- Payment API isolation

---

# 10. Testing Matrix

| Source | Destination | Expected |
|--------|-------------|----------|
| Corporate | CDE | Blocked |
| Guest | CDE | Blocked |
| Cloud | CDE | Blocked |
| Jump Host | CDE | Allowed |

---

# 11. Evidence Collection

Capture:

- Source IP
- Destination IP
- Port
- Timestamp
- Result

---

# 12. Reporting Narrative Template

Segmentation testing was performed using controlled TCP connectivity testing between defined network boundaries. Testing confirmed segmentation controls were enforced.

---

# 13. Safety Guidelines

- Non intrusive
- No persistence
- No destructive testing

---

# 14. Recommended Workflow

Step 1 Scope
Step 2 Listener
Step 3 Test
Step 4 Capture
Step 5 Document

---

# End of Framework

