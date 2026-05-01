# ADR-005: Policy Engine blocks, not warns

**Status**: Accepted
**Date**: 2026-02-05

## Context

Security and compliance scanners often produce warnings that teams
learn to ignore. In a regulated financial services environment,
policy violations cannot be advisory — they represent actual risk.

## Decision

All Policy Engine violations FAIL the pipeline. There are no warnings.
A violation means the build stops. Teams must remediate before proceeding.
Policy exceptions require formal risk acceptance through the change
management process.

## Rationale

- Warnings are ignored; failures force remediation
- Consistent enforcement builds trust in the control plane
- Aligns with regulatory requirements for hard controls
- Exception process creates audit trail for risk acceptance

## Consequences

Easier:
- Policy compliance is measurable and auditable
- No ambiguity about whether a policy applies
- Regulators can see consistent enforcement

Harder:
- Higher initial friction for teams with technical debt
- Requires mature exception handling process
- Policy changes must be carefully tested to avoid build outages

## Compliance implications

Hard enforcement satisfies SOC 2 CC6.1 and PCI-DSS Requirement 6
requirements for mandatory security controls.
