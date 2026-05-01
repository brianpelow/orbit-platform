# ADR-003: GitLab orchestrates, AAP executes

**Status**: Accepted
**Date**: 2026-01-25

## Context

Image builds require both orchestration (sequencing, decision-making,
policy enforcement) and execution (running build commands, managing
infrastructure). Conflating these concerns in a single tool creates
tight coupling and limits flexibility.

## Decision

Separate orchestration from execution. GitLab CI is the brain:
it sequences the 6 stages, makes policy decisions, and maintains
the audit trail. Ansible Automation Platform (AAP) is the hands:
it executes artifact-specific build playbooks when GitLab instructs.

## Rationale

- Clean separation of concerns
- GitLab provides native audit trail for all pipeline decisions
- AAP playbooks are reusable across multiple pipeline types
- Each tool does what it does best

## Consequences

Easier:
- Build playbooks are reusable and independently testable
- Pipeline logic is auditable in GitLab
- AAP can be swapped without changing orchestration logic

Harder:
- Two systems must be operational for builds to work
- Debugging requires correlation across GitLab and AAP logs
