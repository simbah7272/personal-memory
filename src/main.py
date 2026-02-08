"""Main CLI entry point for Personal Memory."""
import typer
from rich.console import Console

from src.cli import finance, health, work, leisure, report
from src.core.database import init_db

app = typer.Typer(help="Personal Memory - Track your life with AI")
console = Console()


@app.command()
def init():
    """Initialize the database"""
    try:
        init_db()
        console.print("[green]✓[/green] Database initialized successfully!")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize database: {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information"""
    console.print("Personal Memory v0.1.0")


# Register sub-commands
app.add_typer(finance.app, name="finance", help="Finance tracking")
app.add_typer(health.app, name="health", help="Health tracking")
app.add_typer(work.app, name="work", help="Work tracking")
app.add_typer(leisure.app, name="leisure", help="Leisure tracking")
app.add_typer(report.app, name="report", help="Generate reports")


if __name__ == "__main__":
    app()
