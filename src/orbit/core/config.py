"""Configuration for orbit-platform."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class OrbitConfig(BaseModel):
    """Runtime configuration for the Orbit control plane."""

    service_registry_url: str = Field("http://localhost:8001", description="Service Registry API URL")
    policy_engine_url: str = Field("http://localhost:8181", description="OPA Policy Engine URL")
    registry_url: str = Field("registry.example.com", description="Container/artifact registry URL")
    kafka_brokers: str = Field("localhost:9092", description="Kafka broker addresses")
    database_url: str = Field("sqlite:///orbit.db", description="Service Registry database URL")
    anthropic_api_key: str = Field("", description="Anthropic API key for AI narratives")
    industry: str = Field("fintech", description="Industry context")

    @classmethod
    def from_env(cls) -> "OrbitConfig":
        return cls(
            service_registry_url=os.environ.get("ORBIT_REGISTRY_URL", "http://localhost:8001"),
            policy_engine_url=os.environ.get("ORBIT_POLICY_URL", "http://localhost:8181"),
            registry_url=os.environ.get("ORBIT_ARTIFACT_REGISTRY", "registry.example.com"),
            kafka_brokers=os.environ.get("ORBIT_KAFKA_BROKERS", "localhost:9092"),
            database_url=os.environ.get("ORBIT_DATABASE_URL", "sqlite:///orbit.db"),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        )