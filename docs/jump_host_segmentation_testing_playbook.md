# Jump Host Segmentation Testing Playbook

---

# Purpose

Validate segmentation via jump hosts / bastion hosts

---

# Architecture

User → Jump Host → CDE

---

# Testing Objectives

Validate:

- Only jump host can access CDE
- Corporate networks blocked
- Admin access controlled

---

# Ncat Testing

Listener on CDE

```
ncat -lvnp 4444
```

Test from Jump Host

```
ncat <cde-ip> 4444
```

Test from Corporate

```
ncat <cde-ip> 4444
```

---

# Expected Results

| Source | Expected |
|--------|----------|
| Jump Host | Allowed |
| Corporate | Blocked |

---

# PowerShell Testing

```
Test-NetConnection <cde-ip> -Port 4444
```

---

# Evidence Template

| Source | Destination | Result |
|--------|-------------|--------|

---

# Risk Indicators

- Direct CDE access
- Multiple admin paths
- Shared credentials

---

# Reporting Narrative

Segmentation testing confirmed that access to CDE systems is restricted to jump host infrastructure.

---

# End

