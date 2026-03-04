"""Creator CLI — the human creator's interface to the agent."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click
import structlog

log = structlog.get_logger()


@click.group()
@click.option("--config", default="config/default.toml", help="Config file path")
@click.pass_context
def cli(ctx, config: str):
    """Self-Improve Machine — Creator CLI"""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


@cli.command()
@click.option("--balance", default=10.0, type=float, help="Initial balance (USD)")
@click.pass_context
def genesis(ctx, balance: float):
    """Create and start the agent (first birth)."""
    click.echo("=== GENESIS: Creating Self-Improve Agent ===")
    click.echo(f"Initial balance: ${balance:.2f}")
    click.echo(f"Config: {ctx.obj['config_path']}")
    click.echo()

    # Verify constitution exists
    constitution = Path("CONSTITUTION.md")
    soul = Path("SOUL.md")
    if not constitution.exists():
        click.echo("ERROR: CONSTITUTION.md not found!", err=True)
        sys.exit(1)
    if not soul.exists():
        click.echo("ERROR: SOUL.md not found!", err=True)
        sys.exit(1)

    click.echo("✓ Constitution loaded")
    click.echo("✓ Soul template loaded")
    click.echo()

    # Start the agent
    click.echo("Starting agent...")
    try:
        from agent_core.main import boot
        asyncio.run(boot(
            config_path=ctx.obj["config_path"],
            initial_balance=balance,
        ))
    except KeyboardInterrupt:
        click.echo("\nAgent stopped by creator.")
    except Exception as e:
        click.echo(f"Agent crashed: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Check agent status."""
    click.echo("=== Agent Status ===")
    try:
        snapshot_path = Path("data/snapshots/latest.json")
        if snapshot_path.exists():
            data = json.loads(snapshot_path.read_text())
            click.echo(f"State:    {data.get('survival_state', 'unknown')}")
            click.echo(f"Balance:  ${data.get('balance', 0):.2f}")
            click.echo(f"Cycles:   {data.get('cycle_count', 0)}")
            click.echo(f"Uptime:   {data.get('uptime_seconds', 0):.0f}s")
            click.echo(f"Task:     {data.get('current_task', 'none')}")
        else:
            click.echo("No snapshot found. Agent may not have started yet.")
    except Exception as e:
        click.echo(f"Error reading status: {e}", err=True)


@cli.command()
@click.argument("amount", type=float)
def fund(amount: float):
    """Add funds to the agent's balance."""
    click.echo(f"=== Funding Agent: +${amount:.2f} ===")
    # TODO: Interact with running agent via IPC or database
    click.echo("(Not yet implemented — will connect to running agent)")


@cli.command()
def ledger():
    """View the agent's financial ledger."""
    click.echo("=== Financial Ledger ===")
    db_path = Path("data/agent.db")
    if not db_path.exists():
        click.echo("No database found.")
        return

    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT timestamp, type, amount, source, description "
            "FROM ledger ORDER BY timestamp DESC LIMIT 20"
        )
        rows = cursor.fetchall()
        if not rows:
            click.echo("No transactions.")
            return

        click.echo(f"{'Time':<20} {'Type':<10} {'Amount':>10} {'Source':<20} {'Description'}")
        click.echo("-" * 80)
        for row in rows:
            import datetime
            ts = datetime.datetime.fromtimestamp(row[0]).strftime("%Y-%m-%d %H:%M")
            click.echo(f"{ts:<20} {row[1]:<10} ${row[2]:>9.2f} {row[3]:<20} {row[4]}")

        conn.close()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def audit():
    """View audit log."""
    click.echo("=== Audit Log ===")
    audit_file = Path("data/audit/audit.jsonl")
    if not audit_file.exists():
        click.echo("No audit log found.")
        return

    lines = audit_file.read_text().strip().split("\n")
    for line in lines[-20:]:
        try:
            entry = json.loads(line)
            import datetime
            ts = datetime.datetime.fromtimestamp(entry["timestamp"]).strftime("%m-%d %H:%M")
            status = "✓" if entry.get("success") else "✗"
            click.echo(f"{status} [{ts}] {entry['action']}: {entry['description'][:60]}")
        except Exception:
            continue


@cli.command()
@click.argument("task_description")
def assign(task_description: str):
    """Assign a task to the agent (creator initial task)."""
    click.echo(f"=== Assigning Task ===")
    click.echo(f"Task: {task_description}")
    # TODO: Send task via IPC/database queue
    click.echo("(Not yet implemented — will send to running agent)")


@cli.command()
def soul():
    """Display the agent's current soul."""
    soul_path = Path("SOUL.md")
    if soul_path.exists():
        click.echo(soul_path.read_text())
    else:
        click.echo("SOUL.md not found.")


@cli.command()
def constitution():
    """Display the constitution (immutable rules)."""
    const_path = Path("CONSTITUTION.md")
    if const_path.exists():
        click.echo(const_path.read_text())
    else:
        click.echo("CONSTITUTION.md not found.")


@cli.command()
def watchdog():
    """Start the watchdog (keeps agent alive)."""
    click.echo("=== Starting Watchdog ===")
    try:
        from agent_core.self_mod.watchdog import main as watchdog_main
        asyncio.run(watchdog_main())
    except KeyboardInterrupt:
        click.echo("\nWatchdog stopped.")


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
