"""
BookMyShow Web Scraper & RESTful API Package.
"""

from .config import CONFIG
from .models import (
    City,
    MovieSummary,
    MovieDetailsResponse,
    ShowtimeItem,
    CinemaVenueShowtimes,
    VenueDetailsResponse,
    ApiResponse,
)
from .scraper import BookMyShowScraper
from .mcp_server import mcp as mcp_server

__version__ = "1.0.0"
__all__ = [
    "CONFIG",
    "City",
    "MovieSummary",
    "MovieDetailsResponse",
    "ShowtimeItem",
    "CinemaVenueShowtimes",
    "VenueDetailsResponse",
    "ApiResponse",
    "BookMyShowScraper",
    "mcp_server",
]


