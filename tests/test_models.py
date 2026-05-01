"""Tests for Orbit data models."""

from orbit.models.service import (
    ServiceRegistration, SLODefinition, ImageRegistration,
    ValidationResult, OnboardingStatus
)


def test_service_registration_defaults() -> None:
    svc = ServiceRegistration(
        service_name="retail-banking-api",
        owner="team@example.com",
        repo_url="org/retail-banking-api",
    )
    assert svc.service_id == ""
    assert svc.tier == 1
    assert svc.security_scanning_enabled is False


def test_service_is_not_orbit_ready_without_id() -> None:
    svc = ServiceRegistration(
        service_name="test", owner="team@example.com", repo_url="org/test"
    )
    assert svc.is_orbit_ready is False


def test_service_is_orbit_ready() -> None:
    svc = ServiceRegistration(
        service_name="test", owner="team@example.com", repo_url="org/test",
        service_id="SVC-12345",
        security_scanning_enabled=True,
        observability_enabled=True,
    )
    assert svc.is_orbit_ready is True


def test_validation_result_can_build_true() -> None:
    result = ValidationResult(repo_url="org/test", passed=True)
    assert result.can_build is True


def test_validation_result_can_build_false_with_failures() -> None:
    result = ValidationResult(
        repo_url="org/test", passed=True,
        failures=["Repo not registered"]
    )
    assert result.can_build is False


def test_validation_result_can_build_false_with_violations() -> None:
    result = ValidationResult(
        repo_url="org/test", passed=True,
        policy_violations=["Base image not approved"]
    )
    assert result.can_build is False


def test_onboarding_status_not_complete() -> None:
    status = OnboardingStatus(service_name="test")
    assert status.is_complete is False
    assert status.completion_pct == 0


def test_onboarding_status_complete() -> None:
    status = OnboardingStatus(
        service_name="test",
        registered=True,
        slo_declared=True,
        dependencies_mapped=True,
        observability_enabled=True,
        gitlab_scanning_enabled=True,
    )
    assert status.is_complete is True
    assert status.completion_pct == 100


def test_onboarding_status_partial() -> None:
    status = OnboardingStatus(
        service_name="test",
        registered=True,
        slo_declared=True,
    )
    assert status.completion_pct == 40
    assert status.is_complete is False