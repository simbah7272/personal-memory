"""Goal CLI commands."""
from datetime import date, datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.database import get_db
from src.core.exceptions import PersonalMemoryError
from src.services.record_service import RecordService

app = typer.Typer(help="Goal tracking commands")
console = Console()


@app.command()
def add(text: str = typer.Argument(..., help="Natural language description of the goal")):
    """Add a goal (e.g., '目标：每月跑步50公里' or '今年要读12本书')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            goal = loop.run_until_complete(service.add_goal_from_text(text))
            loop.close()

            # Calculate progress percentage
            progress_pct = service.goal_repo.calculate_progress_percentage(goal.id)

            # Display result
            console.print(
                f"🎯 [green]Successfully added goal[/green]: "
                f"{goal.title} ({goal.goal_type})\n"
                f"   Target: {goal.target_value} {goal.unit} | "
                f"Progress: [cyan]{progress_pct:.1f}%[/cyan]"
            )
    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_goals(
    status: str = typer.Option(None, help="Filter by status (active/completed/paused/cancelled)"),
    goal_type: str = typer.Option(None, help="Filter by goal type"),
):
    """List goals"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Get goals
            if status:
                goals = service.goal_repo.get_by_status(service.user_id, status)
            elif goal_type:
                goals = service.goal_repo.get_by_type(service.user_id, goal_type)
            else:
                goals = service.goal_repo.get_all(service.user_id, limit=50)

            if not goals:
                console.print("[yellow]No goals found.[/yellow]")
                return

            # Display table
            table = Table(title="Goals")
            table.add_column("ID", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Title", style="white")
            table.add_column("Progress", style="yellow")
            table.add_column("Target", style="magenta")
            table.add_column("Deadline", style="blue")
            table.add_column("Status", style="bold")

            for goal in goals:
                progress_pct = service.goal_repo.calculate_progress_percentage(goal.id)
                status_icon = {
                    "active": "🔄",
                    "completed": "✅",
                    "paused": "⏸️",
                    "cancelled": "❌",
                }.get(goal.status, "❓")

                # Color code status
                status_style = {
                    "active": "green",
                    "completed": "green",
                    "paused": "yellow",
                    "cancelled": "red",
                }.get(goal.status, "white")

                table.add_row(
                    str(goal.id),
                    goal.goal_type,
                    goal.title[:30] + "..." if len(goal.title) > 30 else goal.title,
                    f"{progress_pct:.1f}%",
                    f"{goal.current_value}/{goal.target_value} {goal.unit}",
                    str(goal.target_date),
                    f"[{status_style}]{status_icon} {goal.status}[/{status_style}]",
                )

            console.print(table)
    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def progress(
    goal_id: int = typer.Argument(..., help="Goal ID"),
    value: float = typer.Argument(..., help="Progress value to add"),
    notes: str = typer.Option(None, help="Optional notes about this progress"),
):
    """Update goal progress"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            goal = loop.run_until_complete(service.update_goal_progress(goal_id, value, notes))
            loop.close()

            # Calculate new progress percentage
            progress_pct = service.goal_repo.calculate_progress_percentage(goal.id)

            # Display result
            console.print(
                f"📈 [green]Progress updated[/green]\n"
                f"   Goal: {goal.title}\n"
                f"   Added: +{value} {goal.unit}\n"
                f"   Current: {goal.current_value}/{goal.target_value} {goal.unit} "
                f"([cyan]{progress_pct:.1f}%[/cyan])"
            )

            # Check if goal is completed
            if goal.status == "completed":
                console.print(f"\n   🎉 [bold green]Goal Completed![/bold green]")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats(
    days: int = typer.Option(30, help="Number of days to look ahead for due goals"),
):
    """Show goal statistics"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Get all goals
            all_goals = service.goal_repo.get_all(service.user_id, limit=100)

            if not all_goals:
                console.print("[yellow]No goals found.[/yellow]")
                return

            # Count by status
            active = sum(1 for g in all_goals if g.status == "active")
            completed = sum(1 for g in all_goals if g.status == "completed")
            paused = sum(1 for g in all_goals if g.status == "paused")
            cancelled = sum(1 for g in all_goals if g.status == "cancelled")

            # Count by type
            from collections import Counter
            goal_types = Counter(g.goal_type for g in all_goals)

            # Display summary
            console.print(f"\n🎯 [bold]Goal Statistics[/bold]\n")
            console.print(f"Total Goals: [cyan]{len(all_goals)}[/cyan]")
            console.print(f"  • Active: [green]{active}[/green]")
            console.print(f"  • Completed: [green]{completed}[/green]")
            console.print(f"  • Paused: [yellow]{paused}[/yellow]")
            console.print(f"  • Cancelled: [red]{cancelled}[/red]")

            if goal_types:
                console.print(f"\nBy Type:")
                for goal_type, count in goal_types.most_common():
                    console.print(f"  • {goal_type}: {count}")

            # Show goals due soon
            due_soon = service.goal_repo.get_goals_due_soon(service.user_id, days=days)
            if due_soon:
                console.print(f"\n⏰ [bold yellow]Goals Due Soon (Next {days} days):[/bold yellow]")
                for goal in due_soon:
                    progress_pct = service.goal_repo.calculate_progress_percentage(goal.id)
                    days_left = (goal.target_date - date.today()).days
                    console.print(
                        f"  • {goal.title}\n"
                        f"    Due in [cyan]{days_left} days[/cyan] | "
                        f"Progress: [yellow]{progress_pct:.1f}%[/yellow]"
                    )

            # Show recent progress
            if active > 0:
                console.print(f"\n📈 Recent Progress (Last 7 days):")
                end_date = date.today()
                start_date = end_date - timedelta(days=7)

                total_progress = 0
                progress_count = 0
                for goal in all_goals:
                    if goal.status == "active":
                        progress_records = service.goal_progress_repo.get_by_date_range(
                            goal.id, start_date, end_date
                        )
                        if progress_records:
                            total_progress += sum(p.value for p in progress_records)
                            progress_count += 1

                if progress_count > 0:
                    console.print(f"  • {progress_count} goals updated")
                    console.print(f"  • Total progress: [cyan]+{total_progress:.2f}[/cyan]")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
