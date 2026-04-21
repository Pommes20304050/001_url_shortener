"""Utility functions for URL Shortener."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .models import ShortURL

console = Console()


def print_short_url(su: ShortURL, base: str = "http://localhost:5000"):
    link = su.short_link(base)
    console.print(Panel(
        f"[bold green]{link}[/bold green]\n[dim]→ {su.long_url}[/dim]",
        title="[bold]Kurzlink erstellt[/bold]",
        border_style="green",
    ))


def print_url_table(rows: list[ShortURL], base: str = "http://localhost:5000"):
    if not rows:
        console.print("[dim]Keine URLs gespeichert.[/dim]")
        return

    t = Table(box=box.ROUNDED, show_lines=True)
    t.add_column("Code",      style="bold cyan",  no_wrap=True)
    t.add_column("Kurzlink",  style="green",       no_wrap=True)
    t.add_column("Ziel-URL",  style="white",       max_width=50)
    t.add_column("Klicks",    style="yellow",      justify="right")
    t.add_column("Erstellt",  style="dim")

    for s in rows:
        t.add_row(
            s.display_code,
            s.short_link(base),
            s.long_url,
            str(s.clicks),
            s.created_at[:16],
        )
    console.print(t)
