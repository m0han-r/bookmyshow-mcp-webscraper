"""
Command Line Interface (CLI) for BookMyShow Web Scraper.
"""

import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .scraper import BookMyShowScraper
from .exporter import DataExporter

console = Console()


def main():
    parser = argparse.ArgumentParser(description="BookMyShow Scraper CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Cities Command
    cities_parser = subparsers.add_parser("cities", help="List supported cities")
    cities_parser.add_argument("--popular", action="store_true", help="List popular cities only")
    cities_parser.add_argument("--export", choices=["json", "csv", "xlsx"], help="Export output format")

    # Movies Command
    movies_parser = subparsers.add_parser("movies", help="Scrape movies in a city")
    movies_parser.add_argument("--city", default="mumbai", help="City slug (default: mumbai)")
    movies_parser.add_argument("--language", help="Filter by language")
    movies_parser.add_argument("--genre", help="Filter by genre")
    movies_parser.add_argument("--export", choices=["json", "csv", "xlsx"], help="Export output format")

    # Details Command
    details_parser = subparsers.add_parser("details", help="Scrape movie synopsis & cast details")
    details_parser.add_argument("--code", required=True, help="Movie Event Code (e.g. ET00378770) or URL")
    details_parser.add_argument("--city", default="mumbai", help="City slug")
    details_parser.add_argument("--export", choices=["json", "csv", "xlsx"], help="Export output format")

    # Showtimes Command
    showtimes_parser = subparsers.add_parser("showtimes", help="Scrape cinema venues & showtimes")
    showtimes_parser.add_argument("--code", required=True, help="Movie Code or Buy Tickets URL")
    showtimes_parser.add_argument("--city", default="mumbai", help="City slug")
    showtimes_parser.add_argument("--date", help="Date in YYYYMMDD format")
    showtimes_parser.add_argument("--export", choices=["json", "csv", "xlsx"], help="Export output format")

    # Search Command
    search_parser = subparsers.add_parser("search", help="Search movies and events")
    search_parser.add_argument("--query", required=True, help="Search term")
    search_parser.add_argument("--city", default="mumbai", help="City slug")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    scraper = BookMyShowScraper()

    if args.command == "cities":
        console.print("[bold cyan]Fetching BookMyShow Cities...[/bold cyan]")
        cities = scraper.get_cities()
        if args.popular:
            cities = [c for c in cities if c.is_popular]

        table = Table(title="BookMyShow Cities / Regions", show_header=True)
        table.add_column("City Name", style="bold green")
        table.add_column("Code", style="cyan")
        table.add_column("Slug", style="magenta")
        table.add_column("Popular", style="yellow")

        for c in cities:
            table.add_row(c.name, c.code, c.slug, "Yes" if c.is_popular else "No")
        console.print(table)

        if args.export:
            fn = f"cities.{args.export}"
            getattr(DataExporter, f"to_{args.export}")(cities, fn)
            console.print(f"[bold green]Saved data to {fn}[/bold green]")

    elif args.command == "movies":
        console.print(f"[bold cyan]Scraping movies for {args.city}...[/bold cyan]")
        movies = scraper.get_movies(city=args.city, language=args.language, genre=args.genre)

        table = Table(title=f"Movies in {args.city.capitalize()} ({len(movies)})")
        table.add_column("Title", style="bold white")
        table.add_column("Code", style="cyan")
        table.add_column("Rating", style="yellow")
        table.add_column("Censor", style="blue")
        table.add_column("Languages", style="green")

        for m in movies:
            table.add_row(
                m.title,
                m.code,
                str(m.rating_score or m.rating_votes or "N/A"),
                m.censor_rating or "N/A",
                ", ".join(m.languages) if m.languages else "N/A",
            )
        console.print(table)

        if args.export:
            fn = f"movies_{args.city}.{args.export}"
            getattr(DataExporter, f"to_{args.export}")(movies, fn)
            console.print(f"[bold green]Saved data to {fn}[/bold green]")

    elif args.command == "details":
        console.print(f"[bold cyan]Fetching details for movie {args.code}...[/bold cyan]")
        details = scraper.get_movie_details(args.code, city=args.city)

        console.print(f"[bold green]Title:[/bold green] {details.title}")
        console.print(f"[bold yellow]Code:[/bold yellow] {details.code}")
        if details.synopsis:
            console.print(f"[bold white]Synopsis:[/bold white] {details.synopsis}")

        if details.cast:
            console.print("\n[bold cyan]Cast:[/bold cyan]")
            for c in details.cast[:5]:
                console.print(f"  • {c.name} ({c.role or 'Actor'})")

        if args.export:
            fn = f"movie_details_{details.code}.{args.export}"
            getattr(DataExporter, f"to_{args.export}")([details], fn)
            console.print(f"[bold green]Saved data to {fn}[/bold green]")

    elif args.command == "showtimes":
        console.print(f"[bold cyan]Fetching showtimes for {args.code} in {args.city}...[/bold cyan]")
        showtimes = scraper.get_showtimes(args.code, city=args.city, date=args.date)

        for venue in showtimes:
            console.print(f"\n[bold green]📍 {venue.venue_name}[/bold green] ([cyan]{venue.venue_code}[/cyan])")
            for st in venue.showtimes:
                price_str = f"₹{st.price_min}-{st.price_max}" if st.price_min else "Price N/A"
                console.print(f"  🕒 [white]{st.show_time}[/white] | Format: [magenta]{st.format}[/magenta] | Price: [yellow]{price_str}[/yellow]")

        if args.export:
            fn = f"showtimes_{args.code}.{args.export}"
            getattr(DataExporter, f"to_{args.export}")(showtimes, fn)
            console.print(f"[bold green]Saved data to {fn}[/bold green]")


if __name__ == "__main__":
    main()
