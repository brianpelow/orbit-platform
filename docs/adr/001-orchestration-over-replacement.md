# ADR-001: Orchestration over replacement

**Status**: Accepted
**Date**: 2026-01-15

## Context

The organization has invested significantly in existing tools: ServiceNow for
change management, Datadog for observability, Ansible Automation Platform for
execution, and GitLab for source control. Replacing these would require years
of migration and significant budget.

## Decision

Orbit orchestrates existing tools via APIs rather than replacing them.
The control plane adds governance, policy enforcement, and audit trails
on top of the existing tool ecosystem.

## Rationale

- Preserves existing tool investments
- Faster time to value — no migration required
- Teams continue using familiar tools
- Control plane can evolve independently of underlying tools

## Consequences

Easier:
- Adoption — teams do not need to change their tools
- Integration — APIs are well-defined and stable

Harder:
- Orbit is dependent on the reliability of downstream tool APIs
- Feature limitations are inherited from underlying tools

## Compliance implications

Orchestration creates a single audit trail across all tools,
satisfying SOC 2 and financial services regulatory requirements.
