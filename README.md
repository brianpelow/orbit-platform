# orbit-platform

> Production Services Control Plane — a 6-stage image build and deployment governance framework for regulated financial services.

![CI](https://github.com/brianpelow/orbit-platform/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)

## Overview

Orbit is a production services control plane that enforces a universal 6-stage
governance framework across all image build and deployment pipelines in a regulated
financial services organization. Every artifact — container images, VM images,
desktop images — passes through the same control framework regardless of type.

Built for platform engineering teams operating under SOC 2, PCI-DSS, and financial
services regulatory requirements where audit trails, policy enforcement, and
deployment governance are non-negotiable.

## The 6-stage control flow

```
1. TRIGGER     Git push / Schedule / Manual dispatch
2. VALIDATE    Service Registry + Policy Engine checks
3. BUILD       AAP executes artifact-specific playbook
4. SCAN        Trivy + Gitleaks + OPA policy validation
5. REGISTER    Push to registry + Update Service Registry
6. DEPLOY      GitOps / SCCM / Manual approval gate
```

What changes across artifact types: the build tool (Podman vs Packer vs DISM)
and deployment method (ArgoCD vs SCCM vs Intune).

What stays the same: the control framework.

## Components

| Component | Description |
|-----------|-------------|
| Service Registry | FastAPI service — authoritative source for service ownership, SLOs, dependencies |
| Policy Engine | OPA-based policy evaluation — violations FAIL pipelines, not warnings |
| Pipeline Validator | Step 2 validation logic — 3 sequential API calls before any build |
| Onboarding CLI | Walks service teams through the 5 prerequisites |
| GitLab CI Templates | Reusable 6-stage pipeline templates |
| OPA Policies | Rego policies for image builds, deployments, and desktop imaging |

## The 5 prerequisites for service teams

Before a team can build images through Orbit:

1. Register service in Service Registry (2 hours)
2. Declare Service Level Objectives (1-2 days)
3. Map service dependencies (4 hours)
4. Enable OpenTelemetry observability (3-5 days)
5. Migrate to registered GitLab repo with security scanning (1-3 days)

See docs/onboarding/ for the complete guide.

## Artifact types supported

| Artifact | Build tool | Scan | Deploy |
|----------|-----------|------|--------|
| Container image | Podman | Trivy + Gitleaks + OPA | ArgoCD / Kubernetes |
| Linux VM image | Packer | Trivy + OPA | Terraform / vSphere |
| Windows VM image | Packer | OPA + CIS | Terraform / vSphere |
| Desktop image | DISM | SCAP + OPA | SCCM / Intune |

## Quick start

```bash
pip install orbit-platform

# Check onboarding status for a service
orbit onboard status --service retail-banking-api

# Validate a service can build
orbit validate --service SVC-12345 --repo org/retail-banking-api

# Run policy check against a Dockerfile
orbit policy check --dockerfile ./Dockerfile --service SVC-12345
```

## Architecture

See docs/architecture/ for system context, component diagrams, and data flows.

## ADRs

See docs/adr/ for the 5 key architecture decision records.

## Contributing

See CONTRIBUTING.md.

## License

Apache 2.0
