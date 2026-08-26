"""
Data models for BookMyShow Web Scraper & REST API.
"""

from typing import List, Optional, Generic, TypeVar, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class City(BaseModel):
    name: str = Field(..., description="Display name of the city/region")
    code: str = Field(..., description="Region code (e.g. MUMBAI, BANG, NCR)")
    slug: str = Field(..., description="URL slug for the region")
    state: Optional[str] = Field(None, description="State name")
    is_popular: bool = Field(False, description="Whether city is listed as a major popular region")

class MovieSummary(BaseModel):
    title: str = Field(..., description="Movie title")
    code: str = Field(..., description="BookMyShow Event/Movie Code (e.g. ET00378770)")
    slug: str = Field(..., description="Movie URL slug")
    rating_score: Optional[float] = Field(None, description="Average rating score out of 10 or percentage")
    rating_votes: Optional[str] = Field(None, description="Total vote count text")
    censor_rating: Optional[str] = Field(None, description="Censor certification (U, UA, A, UA13+, etc.)")
    languages: List[str] = Field(default_factory=list, description="Available audio languages")
    genres: List[str] = Field(default_factory=list, description="Genres (Action, Drama, Thriller, etc.)")
    poster_url: Optional[str] = Field(None, description="Movie poster image URL")
    detail_url: str = Field(..., description="Full URL to movie details page")
    buy_tickets_url: Optional[str] = Field(None, description="URL to book tickets for this movie")

class EventSummary(BaseModel):
    title: str = Field(..., description="Event title")
    code: str = Field(..., description="BookMyShow Event Code")
    category: Optional[str] = Field(None, description="Event category (Comedy, Music, Sports, etc.)")
    venue_name: Optional[str] = Field(None, description="Venue location name")
    date_display: Optional[str] = Field(None, description="Date text display")
    price_display: Optional[str] = Field(None, description="Price text range (e.g. ₹499 onwards)")
    image_url: Optional[str] = Field(None, description="Event banner/thumbnail URL")
    detail_url: str = Field(..., description="Full URL to event details page")

class CastMember(BaseModel):
    name: str = Field(..., description="Person name")
    role: Optional[str] = Field(None, description="Role / Character name or designation")
    image_url: Optional[str] = Field(None, description="Profile photo URL")

class MovieDetailsResponse(BaseModel):
    title: str = Field(..., description="Movie title")
    code: str = Field(..., description="Event/Movie code")
    synopsis: Optional[str] = Field(None, description="Plot overview / synopsis")
    duration: Optional[str] = Field(None, description="Runtime duration (e.g. 2h 45m)")
    release_date: Optional[str] = Field(None, description="Release date text")
    censor_rating: Optional[str] = Field(None, description="Censor certification")
    rating_score: Optional[float] = Field(None, description="Rating score")
    rating_votes: Optional[str] = Field(None, description="Rating vote count")
    languages: List[str] = Field(default_factory=list, description="Supported languages")
    genres: List[str] = Field(default_factory=list, description="Genres")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    banner_url: Optional[str] = Field(None, description="High-resolution banner background image URL")
    trailers: List[dict] = Field(default_factory=list, description="Trailer video links and titles")
    cast: List[CastMember] = Field(default_factory=list, description="Lead cast members")
    crew: List[CastMember] = Field(default_factory=list, description="Director and key crew")
    buy_tickets_url: Optional[str] = Field(None, description="Booking URL")

class ShowtimeItem(BaseModel):
    show_time: str = Field(..., description="Show time text (e.g. 04:30 PM)")
    show_time_category: Optional[str] = Field(None, description="Morning, Afternoon, Evening, Night")
    format: Optional[str] = Field(None, description="Screen format (2D, 3D, IMAX 3D, 4DX, ICE)")
    price_min: Optional[float] = Field(None, description="Starting ticket price in INR")
    price_max: Optional[float] = Field(None, description="Maximum ticket price in INR")
    availability: str = Field("AVAILABLE", description="Availability status: AVAILABLE, FAST_FILLING, ALMOST_FULL, SOLD_OUT")
    is_m_ticket_supported: bool = Field(True, description="Whether mobile ticket entry is supported")

class CinemaVenueShowtimes(BaseModel):
    venue_code: str = Field(..., description="BookMyShow venue code (e.g. CSWO)")
    venue_name: str = Field(..., description="Cinema hall / venue name")
    address_info: Optional[str] = Field(None, description="Sub-location / address excerpt")
    distance_km: Optional[float] = Field(None, description="Distance if geolocation was provided")
    is_m_ticket: bool = Field(True, description="M-ticket supported at venue")
    showtimes: List[ShowtimeItem] = Field(default_factory=list, description="List of available showtimes")

class VenueDetailsResponse(BaseModel):
    venue_code: str = Field(..., description="BookMyShow venue code (e.g. PCAN, CSWO)")
    venue_name: str = Field(..., description="Full cinema hall / venue name")
    address: Optional[str] = Field(None, description="Full street address, landmark, and postal code")
    latitude: Optional[float] = Field(None, description="Exact latitude coordinate")
    longitude: Optional[float] = Field(None, description="Exact longitude coordinate")
    facilities: List[str] = Field(default_factory=list, description="Available venue amenities & facilities")

class SearchResults(BaseModel):
    movies: List[MovieSummary] = Field(default_factory=list)
    events: List[EventSummary] = Field(default_factory=list)

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    count: int = 0
    data: Optional[T] = None
    error: Optional[str] = None

