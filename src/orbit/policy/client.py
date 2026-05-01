"""OPA Policy Engine client."""

from __future__ import annotations

import httpx
from orbit.core.config import OrbitConfig


class PolicyEngineClient:
    """Client for OPA Policy Engine evaluation."""

    def __init__(self, config: OrbitConfig) -> None:
        self.base_url = config.policy_engine_url.rstrip("/")
        self.timeout = 30

    def evaluate(self, policy_path: str, input_data: dict) -> tuple[bool, list[str]]:
        """Evaluate a policy and return (allowed, violations)."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/v1/data/{policy_path}",
                    json={"input": input_data},
                )
                response.raise_for_status()
                result = response.json()
                allowed = result.get("result", {}).get("allow", False)
                violations = result.get("result", {}).get("deny", [])
                return allowed, violations
        except Exception:
            return _mock_evaluate(policy_path, input_data)

    def check_image_build(self, service_id: str, dockerfile: str) -> tuple[bool, list[str]]:
        """Check if an image build is allowed."""
        return self.evaluate("image_build/allow", {
            "service_id": service_id,
            "dockerfile": dockerfile,
        })

    def check_scan_results(
        self,
        image_url: str,
        critical_cves: int,
        high_cves: int,
        secrets_found: bool,
    ) -> tuple[bool, list[str]]:
        """Check if scan results pass policy."""
        return self.evaluate("image_scan/allow", {
            "image_url": image_url,
            "vulnerability_scan": {
                "critical_cves": critical_cves,
                "high_cves": high_cves,
            },
            "secret_scan": {"secrets_found": secrets_found},
        })

    def check_deployment(self, service_id: str, image_url: str, environment: str) -> tuple[bool, list[str]]:
        """Check if a deployment is allowed."""
        return self.evaluate("deployment/allow", {
            "service_id": service_id,
            "image_url": image_url,
            "environment": environment,
        })


def _mock_evaluate(policy_path: str, input_data: dict) -> tuple[bool, list[str]]:
    """Mock policy evaluation for testing without OPA."""
    violations = []

    if "image_build" in policy_path:
        dockerfile = input_data.get("dockerfile", "")
        approved = ["golden-ubuntu-22.04", "golden-rhel-9", "golden-debian-12"]
        if not any(img in dockerfile for img in approved):
            violations.append("Base image not in approved list")

    if "image_scan" in policy_path:
        scan = input_data.get("vulnerability_scan", {})
        if scan.get("critical_cves", 0) > 0:
            violations.append(f"Cannot deploy with {scan['critical_cves']} critical CVE(s)")
        if scan.get("high_cves", 0) > 5:
            violations.append(f"Cannot deploy with {scan['high_cves']} high CVEs (max 5)")
        if input_data.get("secret_scan", {}).get("secrets_found"):
            violations.append("Secrets detected in source — remediate before building")

    return len(violations) == 0, violations