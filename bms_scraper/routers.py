"""
FastAPI Router handlers for BookMyShow RESTful Scraper API.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from .models import (
    City,
    MovieSummary,
    EventSummary,
    MovieDetailsResponse,
    CinemaVenueShowtimes,
    VenueDetailsResponse,
    SearchResults,
    ApiResponse,
)
from .scraper import BookMyShowScraper

router = APIRouter(prefix="/api/v1", tags=["BookMyShow Scraper API"])
scraper = BookMyShowScraper()



@router.get(
    "/cities",
    response_model=ApiResponse[List[City]],
    summary="Get Supported Cities & Regions",
    description="Returns all supported regions and major popular cities across India on BookMyShow (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune, Kolkata, etc.) with region codes and URL slugs.",
)
async def get_cities(popular_only: bool = Query(False, description="Filter for major popular tier-1 metropolitan cities only")):
    try:
        cities = await scraper.async_get_cities()
        if popular_only:
            cities = [c for c in cities if c.is_popular]
        return ApiResponse(success=True, count=len(cities), data=cities)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=[], error=str(e))


@router.get(
    "/movies",
    response_model=ApiResponse[List[MovieSummary]],
    summary="Get Active Movie Listings in a City",
    description="Retrieves clean, structured movie listings currently showing or coming soon in a selected city, with optional filtering by audio language (Hindi, English, Tamil, Telugu, Kannada) and genre (Action, Comedy, Drama, Thriller).",
)
async def get_movies(
    city: str = Query("mumbai", description="Target city slug (e.g. mumbai, chennai, bengaluru, national-capital-region-ncr, hyderabad)"),
    language: Optional[str] = Query(None, description="Filter by language (e.g. Hindi, English, Tamil, Telugu)"),
    genre: Optional[str] = Query(None, description="Filter by genre (e.g. Action, Drama, Comedy, Thriller)"),
):
    try:
        movies = await scraper.async_get_movies(city=city, language=language, genre=genre)
        return ApiResponse(success=True, count=len(movies), data=movies)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=[], error=str(e))


@router.get(
    "/events",
    response_model=ApiResponse[List[EventSummary]],
    summary="Get Live Events & Shows in a City",
    description="Retrieves active live events, comedy standup shows, music concerts, sports matches, exhibitions, and workshops in a target city with venue names, event dates, and category tags.",
)
async def get_events(
    city: str = Query("mumbai", description="Target city slug (e.g. mumbai, bengaluru, delhi)"),
    category: Optional[str] = Query(None, description="Event category filter (events, comedy-shows, music-shows, sports)"),
):
    try:
        events = await scraper.async_get_events(city=city, category=category)
        return ApiResponse(success=True, count=len(events), data=events)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=[], error=str(e))


@router.get(
    "/movies/{movie_code}",
    response_model=ApiResponse[MovieDetailsResponse],
    summary="Get Movie Synopsis & Metadata",
    description="Retrieves comprehensive movie metadata including full plot synopsis, duration, censor certification, ratings, audio languages, high-res poster and banner background URLs, cast and crew profiles, and official video trailer links.",
)
async def get_movie_details(
    movie_code: str,
    city: str = Query("mumbai", description="Target city slug"),
):
    try:
        details = await scraper.async_get_movie_details(movie_code_or_url=movie_code, city=city)
        return ApiResponse(success=True, count=1 if details else 0, data=details)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=None, error=str(e))


@router.get(
    "/showtimes",
    response_model=ApiResponse[List[CinemaVenueShowtimes]],
    summary="Get Cinema Venues & Showtimes",
    description="Retrieves all cinema halls/theaters showing a specific movie in a city, including showtimes, screen formats (2D, 3D, IMAX 3D, 4DX, ICE), ticket price ranges in INR, mobile ticket entry support (is_m_ticket), and seat availability status (AVAILABLE, FAST_FILLING, SOLD_OUT).",
)
async def get_showtimes(
    movie_code: str = Query(..., description="BookMyShow movie code (e.g. ET00378770) or full buy tickets URL"),
    city: str = Query("mumbai", description="Target city slug"),
    date: Optional[str] = Query(None, description="Show date in YYYYMMDD format (e.g. 20260826). Defaults to today."),
):
    try:
        showtimes = await scraper.async_get_showtimes(movie_code_or_url=movie_code, city=city, date=date)
        return ApiResponse(success=True, count=len(showtimes), data=showtimes)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=[], error=str(e))


@router.get(
    "/search",
    response_model=ApiResponse[SearchResults],
    summary="Search Movies & Live Events",
    description="Performs a cross-search across active movie titles and live event listings in a selected city matching a query search term.",
)
async def search(
    q: str = Query(..., description="Search query keyword (e.g. Toxic, Standup Comedy)"),
    city: str = Query("mumbai", description="Target city slug"),
):
    try:
        results = await scraper.async_search(query=q, city=city)
        total_count = len(results.movies) + len(results.events)
        return ApiResponse(success=True, count=total_count, data=results)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=SearchResults(), error=str(e))


@router.get(
    "/venues/{venue_code}",
    response_model=ApiResponse[VenueDetailsResponse],
    summary="Get Cinema Venue Location & Geo Coordinates",
    description="Retrieves detailed cinema hall/theater metadata including full street address, landmark, postal code, exact latitude and longitude coordinates, and available venue facilities/amenities (Parking, F&B, M-Ticket, Ticket Cancellation, Food Court).",
)
async def get_venue_details(
    venue_code: str,
    city: str = Query("mumbai", description="Target city slug (e.g. chennai, mumbai)"),
):
    try:
        venue = await scraper.async_get_venue_details(venue_code_or_url=venue_code, city=city)
        return ApiResponse(success=True, count=1 if venue else 0, data=venue)
    except Exception as e:
        return ApiResponse(success=False, count=0, data=None, error=str(e))


