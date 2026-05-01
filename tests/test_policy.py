"""Tests for Policy Engine client."""

from orbit.core.config import OrbitConfig
from orbit.policy.client import PolicyEngineClient, _mock_evaluate


def test_mock_evaluate_approved_base_image() -> None:
    allowed, violations = _mock_evaluate("image_build/allow", {
        "service_id": "SVC-12345",
        "dockerfile": "FROM golden-ubuntu-22.04:v2.1\nRUN apt-get update\n",
    })
    assert allowed is True
    assert violations == []


def test_mock_evaluate_unapproved_base_image() -> None:
    allowed, violations = _mock_evaluate("image_build/allow", {
        "service_id": "SVC-12345",
        "dockerfile": "FROM ubuntu:22.04\nRUN apt-get update\n",
    })
    assert allowed is False
    assert len(violations) > 0


def test_mock_evaluate_critical_cve_blocked() -> None:
    allowed, violations = _mock_evaluate("image_scan/allow", {
        "image_url": "registry.example.com/test:sha-abc123",
        "vulnerability_scan": {"critical_cves": 1, "high_cves": 0},
        "secret_scan": {"secrets_found": False},
    })
    assert allowed is False
    assert any("critical" in v.lower() for v in violations)


def test_mock_evaluate_clean_scan_passes() -> None:
    allowed, violations = _mock_evaluate("image_scan/allow", {
        "image_url": "registry.example.com/test:sha-abc123",
        "vulnerability_scan": {"critical_cves": 0, "high_cves": 2},
        "secret_scan": {"secrets_found": False},
    })
    assert allowed is True
    assert violations == []


def test_mock_evaluate_secrets_blocked() -> None:
    allowed, violations = _mock_evaluate("image_scan/allow", {
        "image_url": "registry.example.com/test:sha-abc123",
        "vulnerability_scan": {"critical_cves": 0, "high_cves": 0},
        "secret_scan": {"secrets_found": True},
    })
    assert allowed is False
    assert any("secret" in v.lower() for v in violations)


def test_policy_client_check_image_build() -> None:
    config = OrbitConfig()
    client = PolicyEngineClient(config)
    allowed, violations = client.check_image_build(
        "SVC-12345",
        "FROM golden-ubuntu-22.04:v2.1\nRUN apt-get update\n"
    )
    assert isinstance(allowed, bool)
    assert isinstance(violations, list)


def test_policy_client_check_scan_results_clean() -> None:
    config = OrbitConfig()
    client = PolicyEngineClient(config)
    allowed, violations = client.check_scan_results(
        "registry.example.com/test:sha-abc123",
        critical_cves=0, high_cves=1, secrets_found=False,
    )
    assert allowed is True
    assert violations == []