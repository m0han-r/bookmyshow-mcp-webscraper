# BookMyShow Scraper — REST API & MCP Tools Reference

This document provides reusable, clear titles, detailed descriptions, parameter specifications, and sample payloads for all 7 REST API Endpoints and Model Context Protocol (MCP) Tools.

---

## 📌 Summary Overview

| # | Endpoint / Tool Title | REST API Endpoint | MCP Tool Name | Primary Purpose |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Get Supported Cities & Regions** | `GET /api/v1/cities` | `bms_get_cities` | List active Indian cities and region codes |
| **2** | **Get Active Movie Listings** | `GET /api/v1/movies` | `bms_get_movies` | Fetch movies showing/coming soon by city, language & genre |
| **3** | **Get Live Events & Shows** | `GET /api/v1/events` | `bms_get_events` | Fetch concerts, standup comedy, sports & workshops |
| **4** | **Get Movie Synopsis & Metadata** | `GET /api/v1/movies/{code}` | `bms_get_movie_details` | Full plot synopsis, cast, crew, ratings & trailer URLs |
| **5** | **Get Cinema Venues & Showtimes** | `GET /api/v1/showtimes` | `bms_get_showtimes` | Theater showtimes, screen formats (IMAX/3D), pricing & seats |
| **6** | **Get Venue Location & Geo Coordinates** | `GET /api/v1/venues/{code}` | `bms_get_venue_details` | Full street address, exact latitude, longitude & facilities |
| **7** | **Search Movies & Events** | `GET /api/v1/search` | `bms_search` | Global search matching movies and events by query term |

---

## 🛠️ Detailed Specifications

---

### 1. Get Supported Cities & Regions

- **Title**: Get Supported Cities & Regions
- **Description**: Returns all supported regions and major popular cities across India on BookMyShow (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune, Kolkata, etc.) with region codes and URL slugs.
- **REST API**: `GET /api/v1/cities`
- **MCP Tool**: `bms_get_cities(popular_only: bool = False)`

#### Input Parameters
- `popular_only` *(boolean, optional, default: false)*: Filter and return only top tier-1 popular metropolitan regions.

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/cities?popular_only=true"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_get_cities",
    "arguments": { "popular_only": true }
  }
  ```

---

### 2. Get Active Movie Listings

- **Title**: Get Active Movie Listings in a City
- **Description**: Retrieves clean, structured movie listings currently showing or coming soon in a selected city, with optional filtering by audio language (Hindi, English, Tamil, Telugu, Kannada, etc.) and genre (Action, Comedy, Drama, Thriller).
- **REST API**: `GET /api/v1/movies`
- **MCP Tool**: `bms_get_movies(city: str = "mumbai", language: Optional[str] = None, genre: Optional[str] = None)`

#### Input Parameters
- `city` *(string, default: "mumbai")*: Target city slug (e.g. `mumbai`, `chennai`, `bengaluru`, `national-capital-region-ncr`, `hyderabad`).
- `language` *(string, optional)*: Filter by language (e.g. `Hindi`, `English`, `Tamil`, `Telugu`).
- `genre` *(string, optional)*: Filter by genre (e.g. `Action`, `Comedy`, `Drama`).

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/movies?city=chennai&language=Tamil"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_get_movies",
    "arguments": { "city": "chennai", "language": "Tamil" }
  }
  ```

---

### 3. Get Live Events & Shows

- **Title**: Get Live Events & Shows in a City
- **Description**: Retrieves active live events, comedy standup shows, music concerts, sports matches, exhibitions, and workshops in a target city with venue names, event dates, and category tags.
- **REST API**: `GET /api/v1/events`
- **MCP Tool**: `bms_get_events(city: str = "mumbai", category: Optional[str] = None)`

#### Input Parameters
- `city` *(string, default: "mumbai")*: Target city slug.
- `category` *(string, optional)*: Category filter (`events`, `comedy-shows`, `music-shows`, `sports`).

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/events?city=bengaluru&category=comedy-shows"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_get_events",
    "arguments": { "city": "bengaluru", "category": "comedy-shows" }
  }
  ```

---

### 4. Get Movie Synopsis & Metadata

- **Title**: Get Movie Synopsis & Metadata
- **Description**: Retrieves comprehensive movie metadata including full plot synopsis, duration, censor certification, ratings, audio languages, high-res poster and banner background URLs, cast and crew profiles, and official video trailer links.
- **REST API**: `GET /api/v1/movies/{movie_code}`
- **MCP Tool**: `bms_get_movie_details(movie_code: str, city: str = "mumbai")`

#### Input Parameters
- `movie_code` *(string, required)*: BookMyShow movie event code (e.g. `ET00378770`) or full BookMyShow movie URL.
- `city` *(string, default: "mumbai")*: Target city slug.

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/movies/ET00378770?city=mumbai"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_get_movie_details",
    "arguments": { "movie_code": "ET00378770", "city": "mumbai" }
  }
  ```

---

### 5. Get Cinema Venues & Showtimes

- **Title**: Get Cinema Venues & Showtimes
- **Description**: Retrieves all cinema halls/theaters showing a specific movie in a city, including showtimes, screen formats (2D, 3D, IMAX 3D, 4DX, ICE, AUROMAX), ticket price ranges in INR, mobile ticket entry support (`is_m_ticket`), and seat availability status (`AVAILABLE`, `FAST_FILLING`, `SOLD_OUT`).
- **REST API**: `GET /api/v1/showtimes`
- **MCP Tool**: `bms_get_showtimes(movie_code: str, city: str = "mumbai", date: Optional[str] = None)`

#### Input Parameters
- `movie_code` *(string, required)*: Movie event code (e.g. `ET00378770`) or full buy tickets URL.
- `city` *(string, default: "mumbai")*: Target city slug.
- `date` *(string, optional)*: Show date in `YYYYMMDD` format (e.g. `20260826`). Defaults to current date.

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/showtimes?movie_code=ET00378770&city=chennai"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_get_showtimes",
    "arguments": { "movie_code": "ET00378770", "city": "chennai" }
  }
  ```

---

### 6. Get Cinema Venue Location & Geo Coordinates

- **Title**: Get Cinema Venue Location & Geo Coordinates
- **Description**: Retrieves detailed cinema hall/theater metadata including full street address, landmark, postal code, exact latitude and longitude coordinates, and available venue facilities/amenities (Parking, F&B, M-Ticket, Ticket Cancellation, Food Court).
- **REST API**: `GET /api/v1/venues/{venue_code}`
- **MCP Tool**: `bms_get_venue_details(venue_code: str, city: str = "mumbai")`

#### Input Parameters
- `venue_code` *(string, required)*: Theater venue code (e.g. `PCAN` for PVR VR Chennai, `CSWO` for Cinepolis Seawoods) or full venue URL.
- `city` *(string, default: "mumbai")*: Target city slug.

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/venues/PCAN?city=chennai"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_get_venue_details",
    "arguments": { "venue_code": "PCAN", "city": "chennai" }
  }
  ```

#### Example Output
```json
{
  "success": true,
  "count": 1,
  "data": {
    "venue_code": "PCAN",
    "venue_name": "PVR: VR Chennai, Anna Nagar",
    "address": "3rd Floor, VR Mall, Metro Zone, No 44, Pillaiyar Koil Street, Jawaharlal Nehru Road, Anna Nagar, Chennai, Tamil Nadu 600040, India",
    "latitude": 13.082561,
    "longitude": 80.194803,
    "facilities": [
      "Ticket Cancellation",
      "F&B",
      "MTicket",
      "Parking Facility",
      "Food Court"
    ]
  },
  "error": null
}
```

---

### 7. Search Movies & Live Events

- **Title**: Search Movies & Live Events
- **Description**: Performs a cross-search across active movie titles and live event listings in a selected city matching a query search term.
- **REST API**: `GET /api/v1/search`
- **MCP Tool**: `bms_search(query: str, city: str = "mumbai")`

#### Input Parameters
- `query` *(string, required)*: Search query keyword (e.g. `Toxic`, `Standup Comedy`).
- `city` *(string, default: "mumbai")*: Target city slug.

#### Example Usage
- **cURL**: `curl -X GET "http://127.0.0.1:8000/api/v1/search?q=Toxic&city=mumbai"`
- **MCP Call**:
  ```json
  {
    "tool": "bms_search",
    "arguments": { "query": "Toxic", "city": "mumbai" }
  }
  ```
