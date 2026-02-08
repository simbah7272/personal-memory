"""Social CLI commands."""
from datetime import date, datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table

from src.core.database import get_db
from src.core.exceptions import PersonalMemoryError
from src.services.record_service import RecordService

app = typer.Typer(help="Social tracking commands")
console = Console()


@app.command()
def add(text: str = typer.Argument(..., help="Natural language description of social activity")):
    """Add a social record (e.g., '和朋友聚餐，花了200块，很愉快')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            record = loop.run_until_complete(service.add_social_from_text(text))
            loop.close()

            # Display result
            console.print(
                f"👥 [green]Successfully added[/green]: "
                f"{record.relationship_type} - {record.activity} ({record.duration_hours}小时)"
            )
    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_records(
    days: int = typer.Option(7, help="Number of days to look back"),
    relationship: str = typer.Option(None, help="Filter by relationship type"),
):
    """List recent social records"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get records
            if relationship:
                records = service.social_repo.get_by_relationship(service.user_id, relationship)
            else:
                records = service.social_repo.get_by_date_range(
                    service.user_id, start_date, end_date
                )

            if not records:
                console.print("[yellow]No social records found.[/yellow]")
                return

            # Display table
            table = Table(title=f"Social Records (Last {days} days)")
            table.add_column("Date", style="cyan")
            table.add_column("Relationship", style="green")
            table.add_column("Activity", style="white")
            table.add_column("Duration", style="yellow")
            table.add_column("Enjoyment", style="magenta")
            table.add_column("Cost", style="blue")

            for record in records:
                enjoyment_display = f"⭐{record.enjoyment_score}" if record.enjoyment_score else "-"
                cost_display = f"¥{record.cost}" if record.cost else "-"
                table.add_row(
                    str(record.record_date),
                    record.relationship_type,
                    record.activity[:30] + "..." if len(record.activity) > 30 else record.activity,
                    f"{record.duration_hours}h",
                    enjoyment_display,
                    cost_display,
                )

            console.print(table)
    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats(
    days: int = typer.Option(30, help="Number of days to analyze"),
):
    """Show social statistics"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get statistics
            total_hours = service.social_repo.get_total_hours_by_date_range(
                service.user_id, start_date, end_date
            )

            total_cost = service.social_repo.get_total_cost_by_date_range(
                service.user_id, start_date, end_date
            )

            avg_enjoyment = service.social_repo.get_average_enjoyment_score(
                service.user_id, start_date, end_date
            )

            stats_by_relationship = service.social_repo.get_stats_by_relationship(
                service.user_id, start_date, end_date
            )

            # Display summary
            console.print(f"\n👥 [bold]Social Statistics (Last {days} days)[/bold]\n")
            console.print(f"Total Hours: [cyan]{total_hours:.1f}h[/cyan]")
            console.print(f"Total Cost: [blue]¥{total_cost:.2f}[/blue]")
            console.print(f"Average Enjoyment: [yellow]⭐{avg_enjoyment:.1f}[/yellow]")

            if stats_by_relationship:
                console.print(f"\nBy Relationship:")
                for stat in stats_by_relationship:
                    console.print(
                        f"  • {stat['relationship']}: "
                        f"[cyan]{stat['total_hours']:.1f}h[/cyan] "
                        f"({stat['count']} times)"
                    )
                    if stat['total_cost'] > 0:
                        console.print(f"    Cost: [blue]¥{stat['total_cost']:.2f}[/blue]")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
