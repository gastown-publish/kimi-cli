"""Convoy command for Kimi Code CLI - Gas Town convoy integration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Annotated, TypedDict

import typer

cli = typer.Typer(help="Gas Town convoy integration.")


class ConvoyInfo(TypedDict):
    """Convoy information data structure."""

    convoy_id: str | None
    rig: str | None
    role: str | None
    work_dir: str | None
    agent: str | None


@dataclass
class ConvoyContext:
    """Gas Town convoy context."""

    convoy_id: str | None
    rig: str | None
    role: str | None
    work_dir: str | None
    agent: str | None

    @classmethod
    def from_env(cls) -> ConvoyContext:
        """Extract convoy context from environment variables."""
        return cls(
            convoy_id=os.getenv("GT_CONVOY_ID"),
            rig=os.getenv("GT_RIG"),
            role=os.getenv("GT_ROLE"),
            work_dir=os.getenv("GT_WORK_DIR"),
            agent=os.getenv("GT_AGENT"),
        )

    def to_dict(self) -> ConvoyInfo:
        """Convert to dictionary."""
        return {
            "convoy_id": self.convoy_id,
            "rig": self.rig,
            "role": self.role,
            "work_dir": self.work_dir,
            "agent": self.agent,
        }

    def is_in_convoy(self) -> bool:
        """Check if running within a Gas Town convoy."""
        return self.convoy_id is not None or self.rig is not None


def _emit_info(json_output: bool) -> None:
    """Emit convoy information."""
    context = ConvoyContext.from_env()

    if json_output:
        typer.echo(json.dumps(context.to_dict(), indent=2, ensure_ascii=False))
        return

    if not context.is_in_convoy():
        typer.echo("Not running within a Gas Town convoy.")
        typer.echo("")
        typer.echo("To use convoy features, run via Gas Town:")
        typer.echo("  gt convoy create <name>")
        typer.echo("  gt sling <bead-id> <rig>")
        return

    lines = ["Convoy Information:", ""]

    if context.convoy_id:
        lines.append(f"  Convoy ID: {context.convoy_id}")
    if context.rig:
        lines.append(f"  Rig:       {context.rig}")
    if context.role:
        lines.append(f"  Role:      {context.role}")
    if context.agent:
        lines.append(f"  Agent:     {context.agent}")
    if context.work_dir:
        lines.append(f"  Work Dir:  {context.work_dir}")

    for line in lines:
        typer.echo(line)


@cli.command(name="info")
def info(
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output information as JSON.",
        ),
    ] = False,
) -> None:
    """Show current convoy information.

    Displays information about the Gas Town convoy context if running
    within a convoy. Shows convoy ID, rig, role, and work directory.

    Examples:
        kimi convoy info              # Show human-readable convoy info
        kimi convoy info --json       # Output as JSON
    """
    _emit_info(json_output)


@cli.command(name="status")
def status(
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output information as JSON.",
        ),
    ] = False,
) -> None:
    """Show convoy status (alias for 'info').

    This is an alias for the 'info' command for convenience.
    """
    _emit_info(json_output)
