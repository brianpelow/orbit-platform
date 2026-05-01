"""Nightly agent — validates platform health and updates documentation."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

REPO_ROOT = Path(__file__).parent.parent


def run_self_validation() -> None:
    from orbit.core.config import OrbitConfig
    from orbit.validator.pipeline import PipelineValidator

    config = OrbitConfig()
    validator = PipelineValidator(config)

    test_dockerfile = "FROM golden-ubuntu-22.04:latest\nRUN apt-get update\n"
    result = validator.validate("brianpelow/orbit-platform", test_dockerfile)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date": date.today().isoformat(),
        "self_validation": {
            "passed": result.can_build,
            "service_id": result.service_id,
            "failures": result.failures,
            "policy_violations": result.policy_violations,
        },
    }

    out = REPO_ROOT / "docs" / "nightly-validation.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"[agent] Self-validation: {'PASSED' if result.can_build else 'FAILED'} -> {out}")


def refresh_changelog() -> None:
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = date.today().isoformat()
    content = changelog.read_text()
    if today not in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n_Last validated: {today}_", 1)
        changelog.write_text(content)
    print("[agent] Refreshed CHANGELOG timestamp")


if __name__ == "__main__":
    print(f"[agent] Starting nightly agent - {date.today().isoformat()}")
    run_self_validation()
    refresh_changelog()
    print("[agent] Done.")