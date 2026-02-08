"""Learning CLI commands."""
from datetime import date, datetime, timedelta

import typer
from rich.console import Console
from rich.table import Table

from src.core.database import get_db
from src.core.exceptions import PersonalMemoryError
from src.services.record_service import RecordService

app = typer.Typer(help="Learning tracking commands")
console = Console()


@app.command()
def add(text: str = typer.Argument(..., help="Natural language description of learning activity")):
    """Add a learning record (e.g., '读了2小时《深度工作》，完成了第一章')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            record = loop.run_until_complete(service.add_learning_from_text(text))
            loop.close()

            # Display result
            console.print(
                f"📚 [green]Successfully added[/green]: "
                f"{record.learning_type} - {record.title} ({record.duration_hours}小时)"
            )
    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_records(
    days: int = typer.Option(7, help="Number of days to look back"),
    learning_type: str = typer.Option(None, help="Filter by learning type"),
):
    """List recent learning records"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get records
            if learning_type:
                records = service.learning_repo.get_by_type(service.user_id, learning_type)
            else:
                records = service.learning_repo.get_by_date_range(
                    service.user_id, start_date, end_date
                )

            if not records:
                console.print("[yellow]No learning records found.[/yellow]")
                return

            # Display table
            table = Table(title=f"Learning Records (Last {days} days)")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Title", style="white")
            table.add_column("Duration", style="yellow")
            table.add_column("Progress", style="magenta")
            table.add_column("Rating", style="blue")

            for record in records:
                rating_display = f"⭐{record.rating}" if record.rating else "-"
                progress_display = f"{record.progress}%" if record.progress else "-"
                table.add_row(
                    str(record.record_date),
                    record.learning_type,
                    record.title[:30] + "..." if len(record.title) > 30 else record.title,
                    f"{record.duration_hours}h",
                    progress_display,
                    rating_display,
                )

            console.print(table)
    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats(
    days: int = typer.Option(30, help="Number of days to analyze"),
    learning_type: str = typer.Option(None, help="Filter by learning type"),
):
    """Show learning statistics"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get statistics
            total_hours = service.learning_repo.get_total_hours_by_date_range(
                service.user_id, start_date, end_date
            )

            stats_by_type = service.learning_repo.get_stats_by_type(
                service.user_id, start_date, end_date
            )

            # Display summary
            console.print(f"\n📚 [bold]Learning Statistics (Last {days} days)[/bold]\n")
            console.print(f"Total Hours: [cyan]{total_hours:.1f}h[/cyan]")

            if stats_by_type:
                console.print(f"\nBy Learning Type:")
                for stat in stats_by_type:
                    if learning_type is None or stat["learning_type"] == learning_type:
                        console.print(
                            f"  • {stat['learning_type']}: "
                            f"[cyan]{stat['total_hours']:.1f}h[/cyan] "
                            f"({stat['count']} records)"
                        )

            # Get all records for detailed stats
            records = service.learning_repo.get_by_date_range(
                service.user_id, start_date, end_date
            )

            if records:
                # Calculate average progress
                avg_progress = sum(r.progress for r in records if r.progress) / len(records) if records else 0
                console.print(f"\nAverage Progress: [magenta]{avg_progress:.0f}%[/magenta]")

                # Count ratings
                rated = [r for r in records if r.rating]
                if rated:
                    avg_rating = sum(r.rating for r in rated) / len(rated)
                    console.print(f"Average Rating: [yellow]⭐{avg_rating:.1f}[/yellow]")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
