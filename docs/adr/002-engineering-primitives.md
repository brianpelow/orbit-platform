# ADR-002: Engineering primitives only

**Status**: Accepted
**Date**: 2026-01-20

## Context

Service teams have inconsistent practices: some use spreadsheets to track
dependencies, some have undocumented SLOs, some store configuration in
shared drives. Orbit cannot govern what it cannot read programmatically.

## Decision

Orbit only accepts version-controlled, schema-validated, API-accessible
engineering primitives. Spreadsheets, Word documents, and shared drives
are not valid inputs. All service metadata must be expressed as code.

## Rationale

- Version control provides audit trail for all changes
- Schema validation ensures data quality
- API accessibility enables automation
- Forces teams toward engineering best practices

## Consequences

Easier:
- Automated policy evaluation against structured data
- Change history for all service metadata
- Programmatic dependency graph construction

Harder:
- Teams must migrate from informal documentation to code
- Higher initial onboarding friction

## Compliance implications

Version-controlled primitives provide immutable evidence for
SOX ITGC change management controls.
