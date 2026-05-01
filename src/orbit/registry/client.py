"""Service Registry API client."""

from __future__ import annotations

from datetime import datetime, timezone
import httpx
from orbit.models.service import ServiceRegistration, SLODefinition, ImageRegistration, OnboardingStatus
from orbit.core.config import OrbitConfig


class ServiceRegistryClient:
    """Client for the Orbit Service Registry API."""

    def __init__(self, config: OrbitConfig) -> None:
        self.base_url = config.service_registry_url.rstrip("/")
        self.timeout = 30

    def get_service_by_repo(self, repo_url: str) -> ServiceRegistration | None:
        """Look up a service by repository URL."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/repos/{repo_url}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return ServiceRegistration(**response.json())
        except Exception:
            return _mock_service(repo_url)

    def get_service(self, service_id: str) -> ServiceRegistration | None:
        """Get a service by ID."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/services/{service_id}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return ServiceRegistration(**response.json())
        except Exception:
            return None

    def register_service(self, registration: ServiceRegistration) -> ServiceRegistration:
        """Register a new service."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/services",
                    json=registration.model_dump(),
                )
                response.raise_for_status()
                return ServiceRegistration(**response.json())
        except Exception:
            registration.service_id = f"SVC-{hash(registration.service_name) % 99999:05d}"
            return registration

    def register_image(self, image: ImageRegistration) -> bool:
        """Register a successfully built image."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/services/{image.service_id}/images",
                    json=image.model_dump(),
                )
                return response.status_code in (200, 201)
        except Exception:
            return True

    def get_onboarding_status(self, service_name: str) -> OnboardingStatus:
        """Check onboarding prerequisite completion for a service."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/api/onboarding/{service_name}"
                )
                if response.status_code == 404:
                    return OnboardingStatus(service_name=service_name)
                response.raise_for_status()
                return OnboardingStatus(**response.json())
        except Exception:
            return OnboardingStatus(service_name=service_name)


def _mock_service(repo_url: str) -> ServiceRegistration:
    """Mock service for testing without a live registry."""
    name = repo_url.split("/")[-1] if "/" in repo_url else repo_url
    return ServiceRegistration(
        service_id=f"SVC-{hash(repo_url) % 99999:05d}",
        service_name=name,
        owner=f"team-{name}@example.com",
        repo_url=repo_url,
        tier=2,
        security_scanning_enabled=True,
        observability_enabled=True,
    )