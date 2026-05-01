# Orbit Architecture Overview

## The 6-stage control flow

Every artifact build passes through the same 6 stages regardless of type.

```
TRIGGER
  |
  v
VALIDATE -----> FAIL if: repo not registered, scanning disabled, policy violation
  |
  v
BUILD
  |
  v
SCAN ---------> FAIL if: critical CVE, secret detected, OPA policy violation
  |
  v
REGISTER
  |
  v
DEPLOY
```

## Component responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Service Registry | Service ownership, SLOs, dependencies | FastAPI + PostgreSQL |
| Policy Engine | Rego policy evaluation, build authorization | OPA |
| Pipeline Validator | Step 2 orchestration, 3-API-call validation | Python |
| GitLab CI | Pipeline orchestration, audit trail | GitLab |
| AAP | Build execution (Podman/Packer/DISM) | Ansible |
| Artifact Registry | Image storage, RBAC, layer deduplication | Harbor/ECR |

## Artifact type comparison

| Stage | Container | Linux VM | Desktop |
|-------|-----------|----------|---------|
| Trigger | Git push | Git push | Patch Tuesday |
| Build tool | Podman | Packer | DISM |
| Scan | Trivy + Gitleaks | Trivy | SCAP + OPA |
| Deploy | ArgoCD / K8s | Terraform | SCCM / Intune |

## Step 2 (VALIDATE) detail

Three sequential API calls must all succeed:

```
1. GET /api/repos/{org}/{repo}     -> FAIL if repo not registered
2. GET /api/services/{service_id}  -> FAIL if scanning not enabled
3. POST /v1/data/image_build/allow -> FAIL if policy violations exist
```

## Step 5 (REGISTER) detail

```
1. Push image to artifact registry (with layer deduplication)
2. POST /api/services/{service_id}/images -> record metadata, emit Kafka event
```
