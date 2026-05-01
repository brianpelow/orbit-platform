"""Service Registry FastAPI application."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from orbit.models.service import (
    ServiceRegistration, SLODefinition, ImageRegistration, OnboardingStatus
)

app = FastAPI(
    title="Orbit Service Registry",
    description="Authoritative source for service ownership, SLOs, and dependencies",
    version="0.1.0",
)

# In-memory store for reference implementation
# Production uses PostgreSQL
_services: dict[str, ServiceRegistration] = {}
_slos: dict[str, list[SLODefinition]] = {}
_images: dict[str, list[ImageRegistration]] = {}


class HealthResponse(BaseModel):
    status: str
    version: str
    service_count: int


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0", service_count=len(_services))


@app.post("/api/services", status_code=201)
def register_service(registration: ServiceRegistration) -> ServiceRegistration:
    """Register a new service in the control plane."""
    if not registration.service_id:
        registration.service_id = f"SVC-{str(uuid.uuid4())[:8].upper()}"
    _services[registration.service_id] = registration
    _slos[registration.service_id] = []
    _images[registration.service_id] = []
    return registration


@app.get("/api/services/{service_id}")
def get_service(service_id: str) -> ServiceRegistration:
    if service_id not in _services:
        raise HTTPException(status_code=404, detail=f"Service not found: {service_id}")
    return _services[service_id]


@app.get("/api/repos/{org}/{repo}")
def get_service_by_repo(org: str, repo: str) -> ServiceRegistration:
    repo_url = f"{org}/{repo}"
    for svc in _services.values():
        if repo_url in svc.repo_url:
            return svc
    raise HTTPException(status_code=404, detail=f"No service registered for repo: {repo_url}")


@app.post("/api/services/{service_id}/slos", status_code=201)
def declare_slo(service_id: str, slo: SLODefinition) -> SLODefinition:
    if service_id not in _services:
        raise HTTPException(status_code=404, detail=f"Service not found: {service_id}")
    if not slo.slo_id:
        slo.slo_id = f"SLO-{service_id}-{slo.slo_type.upper()}-001"
    _slos[service_id].append(slo)
    return slo


@app.get("/api/services/{service_id}/slos")
def get_slos(service_id: str) -> dict:
    if service_id not in _services:
        raise HTTPException(status_code=404, detail=f"Service not found: {service_id}")
    return {"service_id": service_id, "slos": [s.model_dump() for s in _slos[service_id]]}


@app.post("/api/services/{service_id}/images", status_code=201)
def register_image(service_id: str, image: ImageRegistration) -> ImageRegistration:
    if service_id not in _services:
        raise HTTPException(status_code=404, detail=f"Service not found: {service_id}")
    image.built_at = datetime.now(timezone.utc).isoformat()
    _images[service_id].append(image)
    _services[service_id].current_image_url = image.image_url
    return image


@app.get("/api/onboarding/{service_name}")
def get_onboarding_status(service_name: str) -> OnboardingStatus:
    for svc in _services.values():
        if svc.service_name == service_name:
            return OnboardingStatus(
                service_name=service_name,
                service_id=svc.service_id,
                registered=True,
                slo_declared=len(_slos.get(svc.service_id, [])) > 0,
                dependencies_mapped=False,
                observability_enabled=svc.observability_enabled,
                gitlab_scanning_enabled=svc.security_scanning_enabled,
            )
    return OnboardingStatus(service_name=service_name)


def run() -> None:
    import uvicorn
    uvicorn.run("orbit.registry.api:app", host="0.0.0.0", port=8001, reload=False)