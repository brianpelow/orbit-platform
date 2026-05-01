# ADR-004: Service Registry is authoritative

**Status**: Accepted
**Date**: 2026-02-01

## Context

Multiple systems claim to know what services exist: CMDB tracks assets,
Datadog discovers services via instrumentation, GitLab knows repos.
Each has partial, often stale information. Orbit needs a single source
of truth for service ownership, SLOs, and dependencies.

## Decision

The Orbit Service Registry is the authoritative source for service
ownership, SLO definitions, and dependency relationships. The CMDB
remains authoritative for physical/virtual asset data and EOL dates.
A bidirectional sync keeps both systems consistent.

## Rationale

- Single source of truth eliminates conflicting data
- Registry is purpose-built for Orbit governance requirements
- CMDB sync preserves existing investment in asset management
- Clean ownership boundary between operational and engineering data

## Consequences

Easier:
- Policy Engine always has current ownership and SLO data
- Incident routing is accurate and up to date
- Blast radius calculation is reliable

Harder:
- Registry must be highly available (it blocks all builds if down)
- Sync with CMDB requires ongoing maintenance
