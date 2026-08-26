"""
BookMyShow Scraper Client.
Handles network fetching (via requests Session + asyncio.to_thread) with headers, retries, and caching.
"""

import time
import asyncio
from typing import List, Optional, Dict, Any
import requests

from .config import CONFIG
from .models import (
    City,
    MovieSummary,
    EventSummary,
    MovieDetailsResponse,
    CinemaVenueShowtimes,
    VenueDetailsResponse,
    SearchResults,
)
from .parser import BMSParser



class BookMyShowScraper:
    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = CONFIG.REQUEST_TIMEOUT):
        self.headers = headers or CONFIG.DEFAULT_HEADERS
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(self.headers)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < CONFIG.CACHE_TTL_SECONDS:
                return entry["data"]
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Any):
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data,
        }

    def _fetch_html_sync(self, url: str) -> str:
        cache_key = f"html:{url}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        resp = self._session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        html = resp.text
        self._set_cache(cache_key, html)
        return html

    async def _fetch_html_async(self, url: str) -> str:
        return await asyncio.to_thread(self._fetch_html_sync, url)

    # --- Cities / Regions ---

    async def async_get_cities(self) -> List[City]:
        """Gets supported cities/regions."""
        try:
            html = await self._fetch_html_async(f"{CONFIG.BASE_URL}/explore/movies-mumbai")
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_cities(state)
        except Exception:
            return BMSParser.parse_cities(None)

    def get_cities(self) -> List[City]:
        try:
            html = self._fetch_html_sync(f"{CONFIG.BASE_URL}/explore/movies-mumbai")
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_cities(state)
        except Exception:
            return BMSParser.parse_cities(None)

    # --- Movies ---

    async def async_get_movies(
        self, city: str = "mumbai", language: Optional[str] = None, genre: Optional[str] = None
    ) -> List[MovieSummary]:
        """Scrapes list of movies showing or coming soon in a city."""
        city_slug = city.lower().strip()
        url = f"{CONFIG.BASE_URL}/explore/movies-{city_slug}"
        try:
            html = await self._fetch_html_async(url)
            state = BMSParser.extract_initial_state(html)
            movies = BMSParser.parse_movies(state, city_slug, html=html)
        except Exception:
            movies = []

        if language:
            lang_low = language.lower()
            movies = [m for m in movies if any(lang_low in l.lower() for l in m.languages)]
        if genre:
            genre_low = genre.lower()
            movies = [m for m in movies if any(genre_low in g.lower() for g in m.genres)]

        return movies

    def get_movies(
        self, city: str = "mumbai", language: Optional[str] = None, genre: Optional[str] = None
    ) -> List[MovieSummary]:
        city_slug = city.lower().strip()
        url = f"{CONFIG.BASE_URL}/explore/movies-{city_slug}"
        try:
            html = self._fetch_html_sync(url)
            state = BMSParser.extract_initial_state(html)
            movies = BMSParser.parse_movies(state, city_slug, html=html)
        except Exception:
            movies = []

        if language:
            lang_low = language.lower()
            movies = [m for m in movies if any(lang_low in l.lower() for l in m.languages)]
        if genre:
            genre_low = genre.lower()
            movies = [m for m in movies if any(genre_low in g.lower() for g in m.genres)]

        return movies

    # --- Events ---

    async def async_get_events(
        self, city: str = "mumbai", category: Optional[str] = None
    ) -> List[EventSummary]:
        """Scrapes events (comedy, concerts, sports, workshops) in a city."""
        city_slug = city.lower().strip()
        cat_slug = category.lower().strip() if category else "events"
        url = f"{CONFIG.BASE_URL}/explore/{cat_slug}-{city_slug}"
        try:
            html = await self._fetch_html_async(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_events(state, city_slug, html=html)
        except Exception:
            return []

    def get_events(
        self, city: str = "mumbai", category: Optional[str] = None
    ) -> List[EventSummary]:
        city_slug = city.lower().strip()
        cat_slug = category.lower().strip() if category else "events"
        url = f"{CONFIG.BASE_URL}/explore/{cat_slug}-{city_slug}"
        try:
            html = self._fetch_html_sync(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_events(state, city_slug, html=html)
        except Exception:
            return []


    # --- Movie Details ---

    async def async_get_movie_details(
        self, movie_code_or_url: str, city: str = "mumbai"
    ) -> MovieDetailsResponse:
        """Scrapes rich movie metadata, cast, crew, synopsis, and trailers."""
        city_slug = city.lower().strip()

        if movie_code_or_url.startswith("http"):
            url = movie_code_or_url
            import re
            code_match = re.search(r'(ET\d+)', url)
            movie_code = code_match.group(1) if code_match else "UNKNOWN"
        else:
            movie_code = movie_code_or_url
            url = f"{CONFIG.BASE_URL}/movies/{city_slug}/movie/{movie_code}"

        try:
            html = await self._fetch_html_async(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_movie_details(state, movie_code)
        except Exception:
            return MovieDetailsResponse(title="Unknown", code=movie_code)

    def get_movie_details(
        self, movie_code_or_url: str, city: str = "mumbai"
    ) -> MovieDetailsResponse:
        city_slug = city.lower().strip()

        if movie_code_or_url.startswith("http"):
            url = movie_code_or_url
            import re
            code_match = re.search(r'(ET\d+)', url)
            movie_code = code_match.group(1) if code_match else "UNKNOWN"
        else:
            movie_code = movie_code_or_url
            url = f"{CONFIG.BASE_URL}/movies/{city_slug}/movie/{movie_code}"

        try:
            html = self._fetch_html_sync(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_movie_details(state, movie_code)
        except Exception:
            return MovieDetailsResponse(title="Unknown", code=movie_code)

    # --- Showtimes ---

    async def async_get_showtimes(
        self, movie_code_or_url: str, city: str = "mumbai", date: Optional[str] = None
    ) -> List[CinemaVenueShowtimes]:
        """Scrapes cinema venues, formats, pricing, and showtimes for a movie."""
        city_slug = city.lower().strip()
        import re

        if "buytickets" in movie_code_or_url and movie_code_or_url.startswith("http"):
            url = movie_code_or_url
            code_match = re.search(r'(ET\d+)', url)
            movie_code = code_match.group(1) if code_match else "UNKNOWN"
        elif movie_code_or_url.startswith("http"):
            code_match = re.search(r'(ET\d+)', movie_code_or_url)
            movie_code = code_match.group(1) if code_match else "UNKNOWN"
            url = f"{CONFIG.BASE_URL}/buytickets/showtimes-{city_slug}/movie-{city_slug}-{movie_code}-MT"
        else:
            movie_code = movie_code_or_url.strip()
            url = f"{CONFIG.BASE_URL}/buytickets/showtimes-{city_slug}/movie-{city_slug}-{movie_code}-MT"

        if date:
            if not url.rstrip("/").endswith(str(date)):
                url = f"{url.rstrip('/')}/{date}"

        try:
            html = await self._fetch_html_async(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_showtimes(state, movie_code)
        except Exception:
            return []

    def get_showtimes(
        self, movie_code_or_url: str, city: str = "mumbai", date: Optional[str] = None
    ) -> List[CinemaVenueShowtimes]:
        city_slug = city.lower().strip()
        import re

        if "buytickets" in movie_code_or_url and movie_code_or_url.startswith("http"):
            url = movie_code_or_url
            code_match = re.search(r'(ET\d+)', url)
            movie_code = code_match.group(1) if code_match else "UNKNOWN"
        elif movie_code_or_url.startswith("http"):
            code_match = re.search(r'(ET\d+)', movie_code_or_url)
            movie_code = code_match.group(1) if code_match else "UNKNOWN"
            url = f"{CONFIG.BASE_URL}/buytickets/showtimes-{city_slug}/movie-{city_slug}-{movie_code}-MT"
        else:
            movie_code = movie_code_or_url.strip()
            url = f"{CONFIG.BASE_URL}/buytickets/showtimes-{city_slug}/movie-{city_slug}-{movie_code}-MT"

        if date:
            if not url.rstrip("/").endswith(str(date)):
                url = f"{url.rstrip('/')}/{date}"

        try:
            html = self._fetch_html_sync(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_showtimes(state, movie_code)
        except Exception:
            return []


    # --- Search ---

    async def async_search(self, query: str, city: str = "mumbai") -> SearchResults:
        """Searches across movies and events in a city for matching titles."""
        q_low = query.lower().strip()
        movies = await self.async_get_movies(city)
        events = await self.async_get_events(city)

        matched_movies = [m for m in movies if q_low in m.title.lower() or q_low in m.code.lower()]
        matched_events = [e for e in events if q_low in e.title.lower() or q_low in e.code.lower()]

        return SearchResults(movies=matched_movies, events=matched_events)

    # --- Venue Details ---

    async def async_get_venue_details(
        self, venue_code_or_url: str, city: str = "mumbai"
    ) -> Optional[VenueDetailsResponse]:
        """Scrapes cinema venue metadata including full street address, latitude, longitude, and facilities."""
        city_slug = city.lower().strip()
        import re

        if "buytickets" in venue_code_or_url and venue_code_or_url.startswith("http"):
            url = venue_code_or_url
            code_match = re.search(r'([A-Z0-9]{3,6})', url)
            venue_code = code_match.group(1) if code_match else "UNKNOWN"
        elif venue_code_or_url.startswith("http"):
            url = venue_code_or_url
            code_match = re.search(r'([A-Z0-9]{3,6})', venue_code_or_url)
            venue_code = code_match.group(1) if code_match else "UNKNOWN"
        else:
            venue_code = venue_code_or_url.strip().upper()
            url = f"{CONFIG.BASE_URL}/buytickets/a-{city_slug}/cinema-{city_slug}-{venue_code}-MT"

        try:
            html = await self._fetch_html_async(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_venue_details(state, venue_code)
        except Exception:
            return None

    def get_venue_details(
        self, venue_code_or_url: str, city: str = "mumbai"
    ) -> Optional[VenueDetailsResponse]:
        city_slug = city.lower().strip()
        import re

        if "buytickets" in venue_code_or_url and venue_code_or_url.startswith("http"):
            url = venue_code_or_url
            code_match = re.search(r'([A-Z0-9]{3,6})', url)
            venue_code = code_match.group(1) if code_match else "UNKNOWN"
        elif venue_code_or_url.startswith("http"):
            url = venue_code_or_url
            code_match = re.search(r'([A-Z0-9]{3,6})', venue_code_or_url)
            venue_code = code_match.group(1) if code_match else "UNKNOWN"
        else:
            venue_code = venue_code_or_url.strip().upper()
            url = f"{CONFIG.BASE_URL}/buytickets/a-{city_slug}/cinema-{city_slug}-{venue_code}-MT"

        try:
            html = self._fetch_html_sync(url)
            state = BMSParser.extract_initial_state(html)
            return BMSParser.parse_venue_details(state, venue_code)
        except Exception:
            return None

