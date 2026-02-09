"""Report CLI commands."""
from datetime import date, timedelta
from decimal import Decimal

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.database import get_db
from src.services.record_service import RecordService

app = typer.Typer(help="Report commands")
console = Console()


@app.command()
def daily(report_date: str = typer.Argument(None, help="Date in YYYY-MM-DD format (default: today)")):
    """Show daily report"""
    try:
        if report_date:
            from datetime import datetime
            report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        else:
            report_date = date.today()

        with get_db() as db:
            service = RecordService(db)

            # Get all records for the day
            finance_records = service.finance_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=report_date,
                end_date=report_date,
            )

            work_records = service.work_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=report_date,
                end_date=report_date,
            )

            leisure_records = service.leisure_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=report_date,
                end_date=report_date,
            )

            # Build report
            console.print()
            console.print(
                Panel(
                    f"[bold cyan]Daily Report - {report_date}[/bold cyan]",
                    expand=False,
                )
            )
            console.print()

            # Finance section
            if finance_records:
                total_income = sum(r.amount for r in finance_records if r.type == "income")
                total_expense = sum(r.amount for r in finance_records if r.type == "expense")

                console.print("[bold yellow]💰 Finance[/bold yellow]")
                for record in finance_records[:5]:
                    icon = "💰" if record.type == "income" else "💸"
                    console.print(f"  {icon} {record.description or record.category}: {record.amount}元")
                console.print(f"  Total Income: ¥{total_income:.2f}")
                console.print(f"  Total Expense: ¥{total_expense:.2f}")
                console.print()

            # Health section - get all health records for the day
            health_records = service.health_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=report_date,
                end_date=report_date,
            )
            if health_records:
                console.print("[bold blue]😴 Health[/bold blue]")
                for hr in health_records:
                    value_str = f"{hr.value} {hr.unit}" if hr.value else "N/A"
                    notes_str = f" - {hr.notes}" if hr.notes else ""
                    console.print(f"  {hr.indicator_name}: {value_str}{notes_str}")
                console.print()

            # Work section
            if work_records:
                total_work_hours = sum(r.duration_hours for r in work_records)
                console.print("[bold green]💼 Work[/bold green]")
                for record in work_records:
                    console.print(f"  • {record.task_name} ({record.duration_hours}h)")
                console.print(f"  Total: {total_work_hours}h")
                console.print()

            # Leisure section
            if leisure_records:
                total_leisure_hours = sum(r.duration_hours for r in leisure_records)
                console.print("[bold magenta]🎮 Leisure[/bold magenta]")
                for record in leisure_records:
                    enjoyment = f" ({record.enjoyment_score}/5)" if record.enjoyment_score else ""
                    console.print(f"  • {record.record.activity}{enjoyment} ({record.duration_hours}h)")
                console.print(f"  Total: {total_leisure_hours}h")
                console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def weekly():
    """Show weekly report"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # Last 7 days including today

        with get_db() as db:
            service = RecordService(db)

            # Get work hours
            work_hours = service.work_repo.get_total_hours(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )

            # Get finance summary
            finance_records = service.finance_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )
            total_income = sum(r.amount for r in finance_records if r.type == "income")
            total_expense = sum(r.amount for r in finance_records if r.type == "expense")

            # Display
            console.print()
            console.print(
                Panel(
                    f"[bold cyan]Weekly Report[/bold cyan]\n{start_date} to {end_date}",
                    expand=False,
                )
            )
            console.print()
            console.print(f"[green]Work Hours:[/green] {work_hours}h (avg: {work_hours/7:.1f}h/day)")
            console.print(f"[yellow]Finance:[/yellow] Income ¥{total_income:.2f} | Expense ¥{total_expense:.2f}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def monthly():
    """Show monthly report"""
    try:
        from datetime import datetime
        end_date = date.today()
        start_date = end_date.replace(day=1)

        with get_db() as db:
            service = RecordService(db)

            # Get work hours
            work_hours = service.work_repo.get_total_hours(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )

            # Get finance summary
            finance_records = service.finance_repo.get_by_date_range(
                user_id=service.user_id,
                start_date=start_date,
                end_date=end_date,
            )
            total_income = sum(r.amount for r in finance_records if r.type == "income")
            total_expense = sum(r.amount for r in finance_records if r.type == "expense")

            # Calculate days in month so far
            days_so_far = end_date.day
            avg_work_hours = work_hours / days_so_far if days_so_far > 0 else 0

            # Display
            console.print()
            console.print(
                Panel(
                    f"[bold cyan]Monthly Report - {end_date.strftime('%Y %B')}[/bold cyan]",
                    expand=False,
                )
            )
            console.print()
            console.print(f"[green]Work Hours:[/green] {work_hours}h (avg: {avg_work_hours:.1f}h/day)")
            console.print(f"[yellow]Finance:[/yellow] Income ¥{total_income:.2f} | Expense ¥{total_expense:.2f}")
            console.print()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
