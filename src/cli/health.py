"""Health CLI commands."""
from datetime import date, timedelta

import typer
from rich.console import Console
from rich.table import Table

from src.core.database import get_db
from src.core.exceptions import PersonalMemoryError
from src.services.record_service import RecordService

app = typer.Typer(help="Health tracking commands")
console = Console()


@app.command()
def add(text: str = typer.Argument(..., help="Natural language description of health data")):
    """Add a health record (e.g., '今天体重65kg' or '昨晚睡了8小时')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            record = loop.run_until_complete(service.add_health_from_text(text))
            loop.close()

            # Display result with icon based on indicator type
            icons = {
                "sleep": "😴",
                "exercise": "🏃",
                "diet": "🍽️",
                "body": "⚖️",
                "mental": "🧠",
                "medical": "💊",
            }
            icon = icons.get(record.indicator_type, "📊")

            console.print(
                f"{icon} [green]Successfully added health record[/green] for {record.record_date}"
            )
            console.print(
                f"  {record.indicator_name}: {record.value} {record.unit}"
            )
            if record.notes:
                console.print(f"  Notes: {record.notes}")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_records(
    days: int = typer.Option(7, help="Number of days to look back"),
    indicator_type: str = typer.Option(None, help="Filter by indicator type"),
):
    """List recent health records"""
    try:
        with get_db() as db:
            service = RecordService(db)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get records
            if indicator_type:
                records = service.health_repo.get_by_indicator_type(
                    service.user_id, indicator_type
                )
            else:
                records = service.health_repo.get_by_date_range(
                    user_id=service.user_id,
                    start_date=start_date,
                    end_date=end_date,
                )

            if not records:
                console.print("[yellow]No records found.[/yellow]")
                return

            # Create table
            table = Table(title=f"Health Records (Last {days} days)")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Indicator", style="white")
            table.add_column("Value", style="yellow")
            table.add_column("Notes")

            for record in records:
                table.add_row(
                    str(record.record_date),
                    record.indicator_type,
                    record.indicator_name,
                    f"{record.value} {record.unit}",
                    record.notes or "-",
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats(
    days: int = typer.Option(30, help="Number of days to analyze"),
):
    """Show health statistics"""
    try:
        with get_db() as db:
            service = RecordService(db)

            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # Get statistics
            stats = service.health_repo.get_indicator_summary(
                service.user_id, start_date, end_date
            )

            if not stats:
                console.print("[yellow]No health records found.[/yellow]")
                return

            # Display summary
            console.print(f"\n📊 [bold]Health Statistics (Last {days} days)[/bold]\n")

            # Group by indicator type
            from collections import defaultdict
            by_type = defaultdict(list)
            for stat in stats:
                by_type[stat['indicator_type']].append(stat)

            # Display by type
            icons = {
                "sleep": "😴",
                "exercise": "🏃",
                "diet": "🍽️",
                "body": "⚖️",
                "mental": "🧠",
                "medical": "💊",
            }

            for indicator_type, type_stats in by_type.items():
                icon = icons.get(indicator_type, "📊")
                console.print(f"{icon} [bold]{indicator_type.upper()}[/bold]")
                for stat in type_stats:
                    console.print(
                        f"  • {stat['indicator_name']}: "
                        f"Avg: [cyan]{stat['avg_value']:.1f}[/cyan], "
                        f"Min: {stat['min_value']:.1f}, "
                        f"Max: {stat['max_value']:.1f} "
                        f"({stat['count']} records)"
                    )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
