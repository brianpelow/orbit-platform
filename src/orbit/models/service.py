"""Service Registry data models."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class ServiceRegistration(BaseModel):
    """A service registered in the Orbit Service Registry."""

    service_id: str = ""
    service_name: str
    owner: str = Field(..., description="Team distribution list email")
    repo_url: str = Field(..., description="GitLab repository URL")
    tier: int = Field(1, description="1=revenue-critical, 2=important, 3=standard")
    security_scanning_enabled: bool = False
    observability_enabled: bool = False
    current_image_url: str = ""
    description: str = ""

    @property
    def is_orbit_ready(self) -> bool:
        return bool(
            self.service_id and
            self.security_scanning_enabled and
            self.observability_enabled
        )


class SLODefinition(BaseModel):
    """An SLO declared for a service."""

    slo_id: str = ""
    service_id: str
    slo_type: str = Field(..., description="availability/latency/error_rate")
    target: float = Field(..., description="Target value e.g. 0.999 for 99.9%")
    window_days: int = Field(30, description="Measurement window in days")
    data_source: str = ""


class ServiceDependency(BaseModel):
    """A dependency relationship between services."""

    service_id: str
    depends_on_service_id: str
    dependency_type: str = Field("hard", description="hard/soft")
    description: str = ""


class ImageRegistration(BaseModel):
    """An image registered after a successful build."""

    service_id: str
    image_url: str
    base_image: str = ""
    artifact_type: str = Field("container", description="container/vm/desktop")
    vulnerability_status: str = "unknown"
    critical_cves: int = 0
    high_cves: int = 0
    scan_passed: bool = False
    built_at: str = ""


class ValidationResult(BaseModel):
    """Result of Step 2 pipeline validation."""

    service_id: str = ""
    repo_url: str
    passed: bool = False
    failures: list[str] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    checked_at: str = ""

    @property
    def can_build(self) -> bool:
        return self.passed and not self.failures and not self.policy_violations


class OnboardingStatus(BaseModel):
    """Onboarding prerequisite status for a service team."""

    service_name: str
    registered: bool = False
    slo_declared: bool = False
    dependencies_mapped: bool = False
    observability_enabled: bool = False
    gitlab_scanning_enabled: bool = False
    service_id: str = ""

    @property
    def is_complete(self) -> bool:
        return all([
            self.registered,
            self.slo_declared,
            self.dependencies_mapped,
            self.observability_enabled,
            self.gitlab_scanning_enabled,
        ])

    @property
    def completion_pct(self) -> int:
        checks = [
            self.registered, self.slo_declared, self.dependencies_mapped,
            self.observability_enabled, self.gitlab_scanning_enabled,
        ]
        return int(sum(checks) / len(checks) * 100)