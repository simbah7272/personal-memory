"""Work CLI commands."""
from datetime import date, timedelta
from decimal import Decimal

import typer
from rich.console import Console
from rich.table import Table

from src.core.database import get_db
from src.core.exceptions import PersonalMemoryError
from src.services.record_service import RecordService

app = typer.Typer(help="Work tracking commands")
console = Console()


@app.command()
def add(text: str = typer.Argument(..., help="Natural language description of work done")):
    """Add a work record (e.g., '今天工作8小时，完成了用户认证模块')"""
    try:
        with get_db() as db:
            import asyncio
            service = RecordService(db)

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            record = loop.run_until_complete(service.add_work_from_text(text))
            loop.close()

            # Display result
            console.print(
                f"💼 [green]Successfully added work record[/green]: {record.task_name}"
            )
            console.print(f"  Type: {record.task_type} | Priority: {record.priority}")
            console.print(f"  Duration: {record.duration_hours} hours")
            if record.value_description:
                console.print(f"  Value: {record.value_description}")
            if record.tags:
                tags_display = ", ".join(record.tags)
                console.print(f"  Tags: {tags_display}")

    except PersonalMemoryError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_records(
    days: int = typer.Option(7, help="Number of days to look back"),
):
    """List recent work records"""
    try:
        with get_db() as db:
            service = RecordService(db)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            records = service.work_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )

            if not records:
                console.print("[yellow]No records found.[/yellow]")
                return

            # Create table
            table = Table(title=f"Work Records (Last {days} days)")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Task", style="green")
            table.add_column("Duration", justify="right", style="yellow")
            table.add_column("Priority", justify="center")
            table.add_column("Tags")
            table.add_column("Value")

            total_hours = Decimal("0")
            for record in records:
                # Convert tags list to string
                tags_display = ", ".join(record.tags) if record.tags else "-"

                table.add_row(
                    str(record.record_date),
                    record.task_type,
                    record.task_name[:30] + "..." if len(record.task_name) > 30 else record.task_name,
                    f"{record.duration_hours}h",
                    record.priority,
                    tags_display,
                    record.value_description or "-",
                )
                total_hours += record.duration_hours

            console.print(table)
            console.print()
            console.print(f"[cyan]Total Hours: [bold]{total_hours}[/bold]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def summary(
    days: int = typer.Option(7, help="Number of days to analyze"),
):
    """Show work summary"""
    try:
        with get_db() as db:
            service = RecordService(db)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            total_hours = service.work_repo.get_total_hours(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )

            console.print(f"[cyan]Work Summary (Last {days} days):[/cyan]")
            console.print(f"  Total Hours: [bold]{total_hours}h[/bold]")
            console.print(f"  Average per day: [bold]{total_hours / days:.1f}h[/bold]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
