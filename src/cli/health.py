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
    """Add a health record (e.g., '昨晚睡了8小时，睡得很好')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            record = loop.run_until_complete(service.add_health_from_text(text))
            loop.close()

            # Display result
            console.print(
                f"😴 [green]Successfully added health record[/green] for {record.record_date}"
            )
            if record.sleep_hours:
                console.print(f"  Sleep: {record.sleep_hours} hours")
            if record.sleep_quality:
                console.print(f"  Quality: {record.sleep_quality}")
            if record.mood:
                console.print(f"  Mood: {record.mood}")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_records(
    days: int = typer.Option(7, help="Number of days to look back"),
):
    """List recent health records"""
    try:
        with get_db() as db:
            service = RecordService(db)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

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
            table.add_column("Sleep", style="blue")
            table.add_column("Quality", style="green")
            table.add_column("Mood", style="yellow")
            table.add_column("Notes")

            for record in records:
                table.add_row(
                    str(record.record_date),
                    f"{record.sleep_hours}h" if record.sleep_hours else "-",
                    record.sleep_quality or "-",
                    record.mood or "-",
                    record.notes or "-",
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
