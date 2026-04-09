# Cloud Segmentation Testing Playbook
AWS • Azure • GCP

---

# Purpose

Validate segmentation controls within cloud environments and between:

- Internet → Cloud
- Corporate → Cloud
- Cloud → On‑Prem
- Cloud → CDE
- Cloud → Management Networks

---

# Cloud Segmentation Testing Model

Test Segmentation Between:

- VPC / VNET / Projects
- Subnets
- Security Groups / NSGs / Firewall Rules
- Private Endpoints
- Peering Connections
- VPN / ExpressRoute / DirectConnect

---

# AWS Segmentation Testing

## Areas to Test

- VPC Peering
- Security Groups
- Network ACLs
- Route Tables
- Transit Gateway
- Private Endpoints
- Load Balancers

---

## AWS Testing Commands

### Ncat Listener

```
ncat -lvnp 4444
```

### Connectivity Test

```
ncat <target-ip> 4444
```

---

## AWS CLI Enumeration

```
aws ec2 describe-instances
aws ec2 describe-security-groups
aws ec2 describe-route-tables
```

---

# Azure Segmentation Testing

## Areas to Test

- VNET Peering
- NSG Rules
- Azure Firewall
- Private Endpoints
- Subnets
- Bastion Access

---

## Azure CLI Testing

```
az vm list
az network nsg list
az network vnet list
```

---

# GCP Segmentation Testing

## Areas to Test

- VPC Networks
- Firewall Rules
- Service Accounts
- Private Access

---

## GCP CLI Testing

```
gcloud compute instances list
gcloud compute firewall-rules list
```

---

# Evidence Template

| Source | Destination | Port | Result |
|--------|-------------|------|--------|

---

# Reporting Narrative

Cloud segmentation testing was performed between defined cloud network boundaries. Testing validated isolation between environments and confirmed segmentation enforcement.

---

# Safety

- Non intrusive
- No persistence
- Read‑only validation

---

# End

