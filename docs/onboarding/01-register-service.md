# Prerequisite 1: Register Service in Service Registry

**Time required**: 2 hours
**Validation**: Service ID assigned (format: SVC-XXXXX)

## Steps

### Option A: CLI

```bash
orbit register --name retail-banking-api --owner team@example.com --repo org/retail-banking-api --tier 1
```

### Option B: API

```bash
curl -X POST https://service-registry.example.com/api/services -H "Content-Type: application/json" -d @body.json
```

Where body.json contains:
```json
{
  "service_name": "retail-banking-api",
  "owner": "team-retail-banking@example.com",
  "repo_url": "org/retail-banking-api",
  "tier": 1
}
```

## Tier definitions

| Tier | Description | Examples |
|------|-------------|---------|
| 1 | Revenue-critical — outage = immediate business impact | Payment API, Auth service |
| 2 | Important — outage = significant degradation | Notification service, Reporting |
| 3 | Standard — outage = minor impact | Internal tooling, batch jobs |

## Ownership rules

- Owner must be a team distribution list, not an individual email
- Owner is paged during incidents — keep it current
- Changing owner requires a PR to the service registry config
