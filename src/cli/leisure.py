"""Leisure CLI commands."""
from datetime import date, timedelta
from decimal import Decimal

import typer
from rich.console import Console
from rich.table import Table

from src.core.database import get_db
from src.core.exceptions import PersonalMemoryError
from src.services.record_service import RecordService

app = typer.Typer(help="Leisure tracking commands")
console = Console()


@app.command()
def add(text: str = typer.Argument(..., help="Natural language description of leisure activity")):
    """Add a leisure record (e.g., '看了2小时电影')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            record = loop.run_until_complete(service.add_leisure_from_text(text))
            loop.close()

            # Display result
            enjoyment = f" ({record.enjoyment_score}/5)" if record.enjoyment_score else ""
            console.print(
                f"🎮 [green]Successfully added leisure record[/green]: {record.activity}{enjoyment}"
            )
            console.print(f"  Duration: {record.duration_hours} hours")
            if record.notes:
                console.print(f"  Notes: {record.notes}")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_records(
    days: int = typer.Option(7, help="Number of days to look back"),
):
    """List recent leisure records"""
    try:
        with get_db() as db:
            service = RecordService(db)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            records = service.leisure_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )

            if not records:
                console.print("[yellow]No records found.[/yellow]")
                return

            # Create table
            table = Table(title=f"Leisure Records (Last {days} days)")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Activity", style="green")
            table.add_column("Duration", justify="right", style="yellow")
            table.add_column("Enjoyment", justify="center")
            table.add_column("Cost", justify="right", style="blue")
            table.add_column("Details")

            total_hours = Decimal("0")
            total_cost = Decimal("0")
            for record in records:
                enjoyment = f"{record.enjoyment_score}/5" if record.enjoyment_score else "-"
                cost_display = f"¥{record.cost}" if record.cost else "-"

                # Build details column
                details = []
                if record.location:
                    details.append(f"📍{record.location}")
                if record.participants:
                    details.append(f"👥{', '.join(record.participants)}")
                details_str = " | ".join(details) if details else "-"

                table.add_row(
                    str(record.record_date),
                    record.activity_type,
                    record.activity[:20] + "..." if len(record.activity) > 20 else record.activity,
                    f"{record.duration_hours}h",
                    enjoyment,
                    cost_display,
                    details_str,
                )
                total_hours += record.duration_hours
                if record.cost:
                    total_cost += record.cost

            console.print(table)
            console.print()
            console.print(f"[cyan]Total Leisure Hours: [bold]{total_hours}[/bold]")
            if total_cost > 0:
                console.print(f"[cyan]Total Cost: [bold blue]¥{total_cost}[/bold blue]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
