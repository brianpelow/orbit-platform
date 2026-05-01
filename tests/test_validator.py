"""Tests for Pipeline Validator."""

from orbit.core.config import OrbitConfig
from orbit.validator.pipeline import PipelineValidator


def test_validate_registered_repo_passes() -> None:
    config = OrbitConfig()
    validator = PipelineValidator(config)
    result = validator.validate(
        "org/retail-banking-api",
        "FROM golden-ubuntu-22.04:v2.1\nRUN apt-get update\n"
    )
    assert result.service_id != ""
    assert result.can_build is True


def test_validate_unapproved_dockerfile_fails() -> None:
    config = OrbitConfig()
    validator = PipelineValidator(config)
    result = validator.validate(
        "org/retail-banking-api",
        "FROM ubuntu:latest\nRUN apt-get update\n"
    )
    assert result.can_build is False
    assert len(result.policy_violations) > 0


def test_validate_scan_results_clean_passes() -> None:
    config = OrbitConfig()
    validator = PipelineValidator(config)
    result = validator.validate_scan_results(
        service_id="SVC-12345",
        image_url="registry.example.com/test:sha-abc123",
        critical_cves=0,
        high_cves=2,
        secrets_found=False,
    )
    assert result.passed is True
    assert result.can_build is True


def test_validate_scan_results_critical_cve_fails() -> None:
    config = OrbitConfig()
    validator = PipelineValidator(config)
    result = validator.validate_scan_results(
        service_id="SVC-12345",
        image_url="registry.example.com/test:sha-abc123",
        critical_cves=1,
        high_cves=0,
        secrets_found=False,
    )
    assert result.can_build is False
    assert len(result.policy_violations) > 0


def test_validate_scan_results_secrets_fails() -> None:
    config = OrbitConfig()
    validator = PipelineValidator(config)
    result = validator.validate_scan_results(
        service_id="SVC-12345",
        image_url="registry.example.com/test:sha-abc123",
        critical_cves=0,
        high_cves=0,
        secrets_found=True,
    )
    assert result.can_build is False