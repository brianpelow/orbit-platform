"""Pipeline Validator — Step 2 of the Orbit control flow."""

from __future__ import annotations

from datetime import datetime, timezone
from orbit.models.service import ValidationResult
from orbit.registry.client import ServiceRegistryClient
from orbit.policy.client import PolicyEngineClient
from orbit.core.config import OrbitConfig


class PipelineValidator:
    """
    Implements Step 2 (VALIDATE) of the 6-stage Orbit control flow.

    Makes three sequential checks before any build is permitted:
    1. Service is registered in Service Registry
    2. Security scanning is enabled for the repo
    3. Policy Engine approves the build request
    """

    def __init__(self, config: OrbitConfig) -> None:
        self.registry = ServiceRegistryClient(config)
        self.policy = PolicyEngineClient(config)

    def validate(self, repo_url: str, dockerfile: str = "") -> ValidationResult:
        """
        Run the full 3-step validation.
        Returns a ValidationResult — pipeline proceeds only if result.can_build is True.
        """
        result = ValidationResult(
            repo_url=repo_url,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

        # API Call #1: Check if repo is registered
        service = self.registry.get_service_by_repo(repo_url)
        if service is None:
            result.failures.append(
                f"Repository '{repo_url}' is not registered in the Service Registry. "
                f"Register at: service-registry.example.com/register"
            )
            return result

        result.service_id = service.service_id

        # API Call #2: Check security scanning is enabled
        if not service.security_scanning_enabled:
            result.failures.append(
                f"Service {service.service_id} does not have security scanning enabled. "
                f"Enable SAST/secret scanning in your GitLab pipeline."
            )
            return result

        # API Call #3: Policy Engine evaluation
        if dockerfile:
            allowed, violations = self.policy.check_image_build(service.service_id, dockerfile)
            if not allowed:
                result.policy_violations.extend(violations)
                return result

        result.passed = True
        return result

    def validate_scan_results(
        self,
        service_id: str,
        image_url: str,
        critical_cves: int,
        high_cves: int,
        secrets_found: bool,
    ) -> ValidationResult:
        """
        Run Step 4 (SCAN) policy validation.
        Called after Trivy and Gitleaks have completed.
        """
        result = ValidationResult(
            repo_url="",
            service_id=service_id,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

        allowed, violations = self.policy.check_scan_results(
            image_url, critical_cves, high_cves, secrets_found
        )

        if not allowed:
            result.policy_violations.extend(violations)
            return result

        result.passed = True
        return result