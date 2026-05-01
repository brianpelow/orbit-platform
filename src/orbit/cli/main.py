"""Orbit CLI — control plane operations and service team onboarding."""

from __future__ import annotations

import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from orbit.core.config import OrbitConfig
from orbit.registry.client import ServiceRegistryClient
from orbit.validator.pipeline import PipelineValidator
from orbit.models.service import ServiceRegistration, SLODefinition

app = typer.Typer(name="orbit", help="Production Services Control Plane CLI.")
console = Console()


@app.command("validate")
def validate(
    repo: str = typer.Option(..., "--repo", "-r", help="GitLab repo path (org/repo)"),
    dockerfile: str = typer.Option("", "--dockerfile", "-d", help="Path to Dockerfile"),
    output_json: bool = typer.Option(False, "--json"),
) -> None:
    """Run Step 2 validation — check if a repo can build through Orbit."""
    config = OrbitConfig.from_env()
    validator = PipelineValidator(config)

    df_content = ""
    if dockerfile:
        from pathlib import Path
        df_path = Path(dockerfile)
        if df_path.exists():
            df_content = df_path.read_text(errors="ignore")

    result = validator.validate(repo, df_content)

    if output_json:
        print(json.dumps(result.model_dump(), indent=2))
        return

    if result.can_build:
        console.print(Panel.fit(
            f"[green]PASSED[/green] — Service: {result.service_id}\n"
            f"Repository: {result.repo_url}\n"
            f"Build is authorized to proceed.",
            title="Orbit Validation",
            border_style="green",
        ))
    else:
        all_failures = result.failures + result.policy_violations
        failure_text = "\n".join(f"  [red]✗[/red] {f}" for f in all_failures)
        console.print(Panel.fit(
            f"[red]FAILED[/red] — Build blocked\n\n{failure_text}",
            title="Orbit Validation",
            border_style="red",
        ))
        raise typer.Exit(code=1)


@app.command("status")
def status(
    service: str = typer.Option(..., "--service", "-s", help="Service name or ID"),
) -> None:
    """Show current status of a service in the control plane."""
    config = OrbitConfig.from_env()
    client = ServiceRegistryClient(config)
    onboarding = client.get_onboarding_status(service)

    color = "green" if onboarding.is_complete else "yellow"
    console.print(Panel.fit(
        f"Service: [cyan]{onboarding.service_name}[/cyan]\n"
        f"Orbit ready: [{color}]{onboarding.is_complete}[/{color}]\n"
        f"Completion: [{color}]{onboarding.completion_pct}%[/{color}]",
        title="Service Status",
        border_style="blue",
    ))

    table = Table(border_style="dim")
    table.add_column("Prerequisite")
    table.add_column("Status", justify="center")

    checks = [
        ("1. Registered in Service Registry", onboarding.registered),
        ("2. SLO declared", onboarding.slo_declared),
        ("3. Dependencies mapped", onboarding.dependencies_mapped),
        ("4. OpenTelemetry enabled", onboarding.observability_enabled),
        ("5. GitLab scanning enabled", onboarding.gitlab_scanning_enabled),
    ]

    for name, done in checks:
        table.add_row(name, "[green]✓[/green]" if done else "[red]✗[/red]")

    console.print(table)


@app.command("register")
def register(
    name: str = typer.Option(..., "--name", "-n", help="Service name"),
    owner: str = typer.Option(..., "--owner", "-o", help="Team DL email"),
    repo: str = typer.Option(..., "--repo", "-r", help="GitLab repo URL"),
    tier: int = typer.Option(2, "--tier", "-t", help="1=critical, 2=important, 3=standard"),
) -> None:
    """Register a service in the Orbit Service Registry."""
    config = OrbitConfig.from_env()
    client = ServiceRegistryClient(config)

    registration = ServiceRegistration(
        service_name=name,
        owner=owner,
        repo_url=repo,
        tier=tier,
    )

    result = client.register_service(registration)
    console.print(f"[green]✓[/green] Service registered: [cyan]{result.service_id}[/cyan]")
    console.print(f"  Name: {result.service_name}")
    console.print(f"  Owner: {result.owner}")
    console.print(f"  Tier: {result.tier}")
    console.print(f"\nNext steps:")
    console.print(f"  orbit onboard --service {name}")


@app.command("onboard")
def onboard(
    service: str = typer.Option(..., "--service", "-s", help="Service name"),
) -> None:
    """Interactive onboarding guide — walk through all 5 prerequisites."""
    config = OrbitConfig.from_env()
    client = ServiceRegistryClient(config)
    status_data = client.get_onboarding_status(service)

    console.print(f"\n[bold]Orbit Onboarding — {service}[/bold]\n")
    console.print(f"Progress: [cyan]{status_data.completion_pct}%[/cyan] complete\n")

    steps = [
        (
            status_data.registered,
            "Register service in Service Registry",
            f"orbit register --name {service} --owner team@example.com --repo org/{service}",
        ),
        (
            status_data.slo_declared,
            "Declare Service Level Objectives",
            "See docs/onboarding/02-declare-slos.md",
        ),
        (
            status_data.dependencies_mapped,
            "Map service dependencies",
            "See docs/onboarding/03-map-dependencies.md",
        ),
        (
            status_data.observability_enabled,
            "Enable OpenTelemetry observability",
            "See docs/onboarding/04-enable-observability.md",
        ),
        (
            status_data.gitlab_scanning_enabled,
            "Enable GitLab security scanning",
            "See docs/onboarding/05-gitlab-scanning.md",
        ),
    ]

    for i, (done, description, action) in enumerate(steps, 1):
        if done:
            console.print(f"  [green]✓[/green] {i}. {description}")
        else:
            console.print(f"  [red]✗[/red] {i}. {description}")
            console.print(f"       [dim]→ {action}[/dim]")

    if status_data.is_complete:
        console.print(f"\n[green]✓ All prerequisites complete — {service} can build through Orbit.[/green]")
    else:
        remaining = 5 - sum([
            status_data.registered, status_data.slo_declared,
            status_data.dependencies_mapped, status_data.observability_enabled,
            status_data.gitlab_scanning_enabled,
        ])
        console.print(f"\n[yellow]{remaining} prerequisite(s) remaining before {service} can build through Orbit.[/yellow]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()