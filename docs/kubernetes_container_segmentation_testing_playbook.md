# Kubernetes and Container Segmentation Testing Playbook

---

# Purpose

Validate segmentation within:

- Kubernetes clusters
- Containers
- Microservices
- Namespaces

---

# Areas to Test

- Namespace isolation
- Network policies
- Pod‑to‑pod connectivity
- Service exposure

---

# Kubernetes Testing

List Pods

```
kubectl get pods -A
```

---

Deploy Test Pod

```
kubectl run test --image=alpine -- sleep 3600
```

---

Connectivity Testing

```
kubectl exec test -- nc <target-ip> 4444
```

---

Expected Results

Blocked = Segmentation working
Connected = Segmentation failure

---

# Docker Testing

Run Test Container

```
docker run -it alpine
```

Test Connectivity

```
nc <target-ip> 4444
```

---

Evidence Template

| Source Pod | Destination | Result |
|------------|-------------|--------|

---

Reporting Narrative

Container segmentation controls were validated using controlled connectivity testing.

---

Safety

- Non intrusive
- No persistence

---

End

