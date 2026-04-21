#!/usr/bin/env python3
"""
URL Shortener CLI v2
  python -m src.main serve
  python -m src.main shorten <url> [--alias x] [--expires 2025-12-31]
  python -m src.main list
  python -m src.main delete <code>
  python -m src.main stats
  python -m src.main qr <code>
"""
import click
from rich.console import Console
from . import db
from .models import ShortURL, generate_code, is_valid_url, make_qr_base64
from .utils import print_short_url, print_url_table

console = Console()
BASE = "http://localhost:5000"


@click.group()
@click.version_option("2.0.0")
def cli():
    """🔗 URL Shortener — kürzen, verwalten, QR-Codes."""
    db.init_db()


@cli.command()
@click.argument("url")
@click.option("--alias",   "-a", default=None, help="Eigener Kurzcode")
@click.option("--expires", "-e", default=None, help="Ablaufdatum ISO (2025-12-31)")
def shorten(url: str, alias, expires):
    """Eine URL kürzen."""
    if not is_valid_url(url):
        console.print("[bold red]Fehler:[/bold red] Ungültige URL")
        raise SystemExit(1)
    code = alias or generate_code()
    if db.code_exists(code):
        console.print(f"[red]Fehler:[/red] Code '[cyan]{code}[/cyan]' bereits vergeben.")
        raise SystemExit(1)
    db.insert(code, url, alias, expires)
    su = ShortURL.from_row(db.get_by_code(code))
    print_short_url(su, BASE)


@cli.command("list")
def list_urls():
    """Alle gespeicherten URLs anzeigen."""
    rows = [ShortURL.from_row(r) for r in db.list_all()]
    print_url_table(rows, BASE)
    console.print(f"\n[dim]{len(rows)} URL(s)[/dim]")


@cli.command()
@click.argument("code")
def delete(code: str):
    """URL löschen."""
    if db.delete(code):
        console.print(f"[green]✓[/green] '[cyan]{code}[/cyan]' gelöscht.")
    else:
        console.print(f"[red]✗[/red] '[cyan]{code}[/cyan]' nicht gefunden.")


@cli.command()
def stats():
    """Statistik anzeigen."""
    s = db.stats()
    console.print(f"[bold]URLs:[/bold]   [cyan]{s['total_urls']}[/cyan]")
    console.print(f"[bold]Klicks:[/bold] [yellow]{s['total_clicks']}[/yellow]")
    top = db.top_urls(3)
    if top:
        console.print("\n[bold]Top 3:[/bold]")
        for r in top:
            console.print(f"  [purple]{r['code']}[/purple]  {r['clicks']} Klicks  {r['long_url'][:50]}")


@cli.command()
@click.argument("code")
def qr(code: str):
    """QR-Code als PNG-Datei speichern."""
    row = db.get_by_code(code)
    if row is None:
        console.print(f"[red]'{code}' nicht gefunden.[/red]")
        raise SystemExit(1)
    su   = ShortURL.from_row(row)
    b64  = make_qr_base64(su.short_link(BASE))
    if b64:
        import base64, os
        os.makedirs("data", exist_ok=True)
        path = f"data/qr_{code}.png"
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        console.print(f"[green]✓[/green] QR-Code → [cyan]{path}[/cyan]")
    else:
        console.print("[yellow]qrcode nicht installiert — pip install 'qrcode[pil]'[/yellow]")


@cli.command()
@click.option("--host",  default="127.0.0.1", show_default=True)
@click.option("--port",  default=5000, type=int, show_default=True)
@click.option("--debug", is_flag=True)
def serve(host: str, port: int, debug: bool):
    """Flask-Webserver starten."""
    from .app import app
    console.print(f"[bold green]URL Shortener v2 — http://{host}:{port}[/bold green]")
    console.print("[dim]QR-Codes · Löschen im Browser · Vorschau · Ablaufdaten · Klick-Log[/dim]\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    cli()
