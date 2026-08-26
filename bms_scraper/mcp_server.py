"""
Model Context Protocol (MCP) Server for BookMyShow Web Scraper.
Exposes BookMyShow scraping capabilities as standardized tools over stdio transport.
"""

from typing import List, Optional, Dict, Any

try:
    from mcp.server import FastMCP
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.fastmcp import FastMCP
    except (ImportError, ModuleNotFoundError):
        from mcp.server import MCPServer as FastMCP

from .scraper import BookMyShowScraper

# Initialize FastMCP / MCPServer Instance
mcp = FastMCP("BookMyShow Scraper")
scraper = BookMyShowScraper()


@mcp.tool()
async def bms_get_cities(popular_only: bool = False) -> List[Dict[str, Any]]:
    """
    Get Supported Cities & Regions

    Returns all supported regions and major popular cities across India on BookMyShow
    (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune, Kolkata, etc.) with region codes and URL slugs.

    Args:
        popular_only: If True, returns only major popular tier-1 metropolitan cities.
    """
    cities = await scraper.async_get_cities()
    if popular_only:
        cities = [c for c in cities if c.is_popular]
    return [c.model_dump() for c in cities]


@mcp.tool()
async def bms_get_movies(
    city: str = "mumbai",
    language: Optional[str] = None,
    genre: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get Active Movie Listings in a City

    Retrieves clean, structured movie listings currently showing or coming soon in a selected city,
    with optional filtering by audio language (Hindi, English, Tamil, Telugu, Kannada) and genre (Action, Comedy, Drama, Thriller).

    Args:
        city: City slug (e.g. 'mumbai', 'bengaluru', 'national-capital-region-ncr', 'hyderabad', 'chennai').
        language: Filter by language (e.g. 'Hindi', 'English', 'Tamil', 'Telugu').
        genre: Filter by genre (e.g. 'Action', 'Drama', 'Comedy', 'Thriller').
    """
    movies = await scraper.async_get_movies(city=city, language=language, genre=genre)
    return [m.model_dump() for m in movies]


@mcp.tool()
async def bms_get_events(
    city: str = "mumbai",
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get Live Events & Shows in a City

    Retrieves active live events, comedy standup shows, music concerts, sports matches, exhibitions,
    and workshops in a target city with venue names, event dates, and category tags.

    Args:
        city: City slug (e.g. 'mumbai', 'bengaluru', 'delhi').
        category: Event category filter ('events', 'comedy-shows', 'music-shows', 'sports').
    """
    events = await scraper.async_get_events(city=city, category=category)
    return [e.model_dump() for e in events]


@mcp.tool()
async def bms_get_movie_details(
    movie_code: str,
    city: str = "mumbai",
) -> Dict[str, Any]:
    """
    Get Movie Synopsis & Metadata

    Retrieves comprehensive movie metadata including full plot synopsis, duration, censor certification,
    ratings, audio languages, high-res poster and banner background URLs, cast and crew profiles, and official video trailer links.

    Args:
        movie_code: BookMyShow movie event code (e.g. 'ET00378770') or full movie page URL.
        city: City slug (default 'mumbai').
    """
    details = await scraper.async_get_movie_details(movie_code_or_url=movie_code, city=city)
    return details.model_dump() if details else {}


@mcp.tool()
async def bms_get_showtimes(
    movie_code: str,
    city: str = "mumbai",
    date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get Cinema Venues & Showtimes

    Retrieves all cinema halls/theaters showing a specific movie in a city, including showtimes, screen formats
    (2D, 3D, IMAX 3D, 4DX, ICE), ticket price ranges in INR, mobile ticket entry support (is_m_ticket), and seat availability status.

    Args:
        movie_code: Movie event code (e.g. 'ET00378770') or full BookMyShow buy tickets URL.
        city: City slug (e.g. 'mumbai', 'bengaluru').
        date: Show date in YYYYMMDD format (e.g. '20260826'). Defaults to current date.
    """
    venues = await scraper.async_get_showtimes(movie_code_or_url=movie_code, city=city, date=date)
    return [v.model_dump() for v in venues]


@mcp.tool()
async def bms_search(
    query: str,
    city: str = "mumbai",
) -> Dict[str, Any]:
    """
    Search Movies & Live Events

    Performs a cross-search across active movie titles and live event listings in a selected city matching a query search term.

    Args:
        query: Search query keyword (e.g. 'Toxic', 'Standup Comedy').
        city: City slug (e.g. 'mumbai', 'bengaluru').
    """
    results = await scraper.async_search(query=query, city=city)
    return results.model_dump()


@mcp.tool()
async def bms_get_venue_details(
    venue_code: str,
    city: str = "mumbai",
) -> Dict[str, Any]:
    """
    Get Cinema Venue Location & Geo Coordinates

    Retrieves detailed cinema hall/theater metadata including full street address, landmark, postal code,
    exact latitude and longitude coordinates, and available venue facilities/amenities (Parking, F&B, M-Ticket, Ticket Cancellation, Food Court).

    Args:
        venue_code: BookMyShow venue code (e.g. 'PCAN', 'CSWO') or full venue URL.
        city: City slug (e.g. 'chennai', 'mumbai').
    """
    venue = await scraper.async_get_venue_details(venue_code_or_url=venue_code, city=city)
    return venue.model_dump() if venue else {}



def run_server():
    """Starts the MCP stdio server loop."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()

