"""Tests for Service Registry client."""

from orbit.core.config import OrbitConfig
from orbit.registry.client import ServiceRegistryClient, _mock_service
from orbit.models.service import ServiceRegistration


def test_mock_service_returns_registration() -> None:
    svc = _mock_service("org/retail-banking-api")
    assert svc.service_name == "retail-banking-api"
    assert svc.service_id != ""
    assert svc.security_scanning_enabled is True
    assert svc.observability_enabled is True


def test_mock_service_different_repos_different_ids() -> None:
    svc1 = _mock_service("org/service-a")
    svc2 = _mock_service("org/service-b")
    assert svc1.service_id != svc2.service_id


def test_registry_client_get_service_by_repo_no_server() -> None:
    config = OrbitConfig()
    client = ServiceRegistryClient(config)
    svc = client.get_service_by_repo("org/retail-banking-api")
    assert svc is not None
    assert svc.service_name == "retail-banking-api"


def test_registry_client_register_service_no_server() -> None:
    config = OrbitConfig()
    client = ServiceRegistryClient(config)
    reg = ServiceRegistration(
        service_name="test-service",
        owner="team@example.com",
        repo_url="org/test-service",
        tier=2,
    )
    result = client.register_service(reg)
    assert result.service_id != ""
    assert result.service_name == "test-service"


def test_registry_client_onboarding_status_no_server() -> None:
    config = OrbitConfig()
    client = ServiceRegistryClient(config)
    status = client.get_onboarding_status("new-service")
    assert status.service_name == "new-service"
    assert status.is_complete is False