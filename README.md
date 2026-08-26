# 🎬 BookMyShow MCP Webscraper

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-supported-purple.svg)](#-model-context-protocol-mcp-server)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#-running-tests)

A high-performance Python web scraper, RESTful API server, Model Context Protocol (MCP) server, CLI tool, and interactive web dashboard for [BookMyShow](https://in.bookmyshow.com). Effortlessly extract real-time movie listings, cinema showtimes, ticket pricing, seating availability, event schedules, and rich movie metadata into structured JSON, CSV, or Excel formats.

---

## ✨ Features

- 🤖 **Model Context Protocol (MCP) Integration**: Native MCP server over stdio, enabling AI assistants (Claude, Antigravity, Cursor) to inspect movies, showtimes, and book seats seamlessly.
- 🏙️ **Multi-City & Region Support**: Fetch movies, events, and venues across all supported Indian cities (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune, etc.).
- 🎟️ **Real-Time Showtimes & Pricing**: Extract cinema venues, showtimes, screen formats (2D, 3D, IMAX, 4DX), ticket price ranges, and seat availability status (`AVAILABLE`, `FAST_FILLING`, `SOLD_OUT`).
- 🎬 **Comprehensive Movie Metadata**: Detailed synopsis, cast & crew profiles, censor ratings, languages, genres, poster/banner images, and trailer video links.
- 📍 **Venue Geo Coordinates**: Extract cinema hall street addresses, exact latitude, longitude, and available amenities.
- ⚡ **Sync & Async Python API**: Built-in support for both synchronous and asynchronous Python code (`asyncio`) with response caching (5-minute default TTL).
- 🚀 **FastAPI REST API**: Fully interactive Swagger (`/docs`) API endpoints for seamless web and mobile backend integration.
- 💻 **Rich CLI Interface**: Sleek terminal UI powered by `rich` supporting search, listings, details, and automatic exports.
- 📊 **Multi-Format Data Exporter**: Export scraped data directly to **JSON**, **CSV**, or **Excel (`.xlsx`)** files.
- 🌐 **Web Dashboard UI**: Embedded frontend dashboard to visually explore active movies, events, and showtimes.

---

## 🚀 Quickstart & Installation


### 1. Clone Repository

```bash
git clone https://github.com/m0han-r/bookmyshow-mcp-webscraper.git
cd bookmyshow-mcp-webscraper
```

### 2. Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

---

## 🤖 Model Context Protocol (MCP) Server

Connect your AI assistant (Claude Desktop, Antigravity IDE, Cursor, etc.) directly to BookMyShow web scraping tools using the Model Context Protocol.

### Registered MCP Tools Summary

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `bms_get_cities` | `popular_only: bool` | Returns supported Indian regions & popular tier-1 cities |
| `bms_get_movies` | `city, language, genre` | Fetches active movie listings with language/genre filters |
| `bms_get_events` | `city, category` | Fetches live events, comedy shows, music concerts, and sports |
| `bms_get_movie_details` | `movie_code, city` | Returns plot synopsis, cast, crew, ratings, poster & trailer video links |
| `bms_get_showtimes` | `movie_code, city, date` | Returns cinema halls, showtimes, screen formats (IMAX/3D/4DX), prices & seat availability |
| `bms_get_venue_details` | `venue_code, city` | Returns cinema venue street address, exact latitude, longitude, and facilities |
| `bms_search` | `query, city` | Searches active movies and live events matching search query |

### Test MCP Server Directly

Run the server over stdio:

```bash
# Using standard Python:
python mcp_server.py

# Or using uvx directly from Git repository:
uvx --from git+https://github.com/m0han-r/bookmyshow-mcp-webscraper.git mcp_server.py
```

### Recommended MCP Client Configuration (`uvx`)

Add Option A to your MCP client configuration file (`claude_desktop_config.json`, `mcp_config.json`, or Antigravity MCP settings) for direct execution from Git without pre-installing dependencies:

```json
{
  "mcpServers": {
    "bookmyshow": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/m0han-r/bookmyshow-mcp-webscraper.git",
        "mcp_server.py"
      ]
    }
  }
}
```

<details>
<summary><b>Alternative: Local Development Configuration (Click to expand)</b></summary>

```json
{
  "mcpServers": {
    "bookmyshow-local": {
      "command": "uv",
      "args": [
        "--directory",
        "d:/Workspace/MyProjects/bookmyshow-webscraper",
        "run",
        "mcp_server.py"
      ]
    },
    "bookmyshow-python": {
      "command": "python",
      "args": [
        "d:/Workspace/MyProjects/bookmyshow-webscraper/mcp_server.py"
      ]
    }
  }
}
```
</details>

---

## 🌐 Running the REST API Server

Start the FastAPI development server:

```bash
python main.py
```

Or using `uvicorn` directly:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔌 Complete API & MCP Tools Detailed Reference

---

### 1. Get Supported Cities & Regions
- **Title**: Get Supported Cities & Regions
- **Description**: Returns all supported regions and major popular cities across India on BookMyShow (Mumbai, Delhi-NCR, Bengaluru, Hyderabad, Chennai, Pune, Kolkata, etc.) with region codes and URL slugs.
- **REST API**: `GET /api/v1/cities`
- **MCP Tool**: `bms_get_cities(popular_only: bool = False)`
- **Parameters**: `popular_only` *(boolean, optional)*: Filter for top popular cities.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/cities?popular_only=true"`
  - MCP: `{"tool": "bms_get_cities", "arguments": {"popular_only": true}}`

---

### 2. Get Active Movie Listings
- **Title**: Get Active Movie Listings in a City
- **Description**: Retrieves clean, structured movie listings currently showing or coming soon in a selected city, with optional filtering by audio language and genre.
- **REST API**: `GET /api/v1/movies`
- **MCP Tool**: `bms_get_movies(city: str = "mumbai", language: Optional[str] = None, genre: Optional[str] = None)`
- **Parameters**: `city` *(string)*, `language` *(string, optional)*, `genre` *(string, optional)*.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/movies?city=chennai&language=Tamil"`
  - MCP: `{"tool": "bms_get_movies", "arguments": {"city": "chennai", "language": "Tamil"}}`

---

### 3. Get Live Events & Shows
- **Title**: Get Live Events & Shows in a City
- **Description**: Retrieves active live events, comedy standup shows, music concerts, sports matches, exhibitions, and workshops in a target city.
- **REST API**: `GET /api/v1/events`
- **MCP Tool**: `bms_get_events(city: str = "mumbai", category: Optional[str] = None)`
- **Parameters**: `city` *(string)*, `category` *(events, comedy-shows, music-shows, sports)*.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/events?city=bengaluru&category=comedy-shows"`
  - MCP: `{"tool": "bms_get_events", "arguments": {"city": "bengaluru", "category": "comedy-shows"}}`

---

### 4. Get Movie Synopsis & Metadata
- **Title**: Get Movie Synopsis & Metadata
- **Description**: Retrieves comprehensive movie metadata including full plot synopsis, duration, censor certification, ratings, audio languages, poster and banner URLs, cast/crew profiles, and YouTube trailer links.
- **REST API**: `GET /api/v1/movies/{movie_code}`
- **MCP Tool**: `bms_get_movie_details(movie_code: str, city: str = "mumbai")`
- **Parameters**: `movie_code` *(string, e.g. ET00378770)*, `city` *(string)*.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/movies/ET00378770?city=mumbai"`
  - MCP: `{"tool": "bms_get_movie_details", "arguments": {"movie_code": "ET00378770", "city": "mumbai"}}`

---

### 5. Get Cinema Venues & Showtimes
- **Title**: Get Cinema Venues & Showtimes
- **Description**: Retrieves all cinema halls showing a specific movie in a city, including showtimes, screen formats (2D, 3D, IMAX 3D, 4DX), price ranges in ₹, M-ticket support, and seat availability.
- **REST API**: `GET /api/v1/showtimes`
- **MCP Tool**: `bms_get_showtimes(movie_code: str, city: str = "mumbai", date: Optional[str] = None)`
- **Parameters**: `movie_code` *(string)*, `city` *(string)*, `date` *(YYYYMMDD, optional)*.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/showtimes?movie_code=ET00378770&city=chennai"`
  - MCP: `{"tool": "bms_get_showtimes", "arguments": {"movie_code": "ET00378770", "city": "chennai"}}`

---

### 6. Get Cinema Venue Location & Geo Coordinates
- **Title**: Get Cinema Venue Location & Geo Coordinates
- **Description**: Retrieves detailed cinema hall metadata including full street address, landmark, postal code, exact latitude and longitude coordinates, and available venue amenities.
- **REST API**: `GET /api/v1/venues/{venue_code}`
- **MCP Tool**: `bms_get_venue_details(venue_code: str, city: str = "mumbai")`
- **Parameters**: `venue_code` *(string, e.g. PCAN, CSWO)*, `city` *(string)*.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/venues/PCAN?city=chennai"`
  - MCP: `{"tool": "bms_get_venue_details", "arguments": {"venue_code": "PCAN", "city": "chennai"}}`

#### Example Response
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
    "facilities": ["Ticket Cancellation", "F&B", "MTicket", "Parking Facility", "Food Court"]
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
- **Parameters**: `query` *(string)*, `city` *(string)*.
- **Examples**:
  - cURL: `curl -X GET "http://127.0.0.1:8000/api/v1/search?q=Toxic&city=mumbai"`
  - MCP: `{"tool": "bms_search", "arguments": {"query": "Toxic", "city": "mumbai"}}`

---

## 🐍 Python Library Usage

### Synchronous Usage

```python
from bms_scraper import BookMyShowScraper

scraper = BookMyShowScraper()

# 1. Fetch popular cities
cities = scraper.get_cities(popular_only=True)
print(f"Found {len(cities)} popular cities.")

# 2. Get active movies in Mumbai
movies = scraper.get_movies(city="mumbai", language="Hindi")
for m in movies:
    print(f"{m.title} ({m.code}) - Rating: {m.rating_score}/10")

# 3. Get venue location & exact lat/long coordinates
venue = scraper.get_venue_details(venue_code_or_url="PCAN", city="chennai")
print(f"📍 {venue.venue_name}")
print(f"   Address: {venue.address}")
print(f"   Coords:  Lat {venue.latitude}, Lon {venue.longitude}")
print(f"   Amenities: {', '.join(venue.facilities)}")

# 4. Get showtimes for a specific movie code
showtimes = scraper.get_showtimes(movie_code_or_url="ET00378770", city="mumbai")
for venue in showtimes:
    print(f"📍 {venue.venue_name}")
    for st in venue.showtimes:
        print(f"   🕒 {st.show_time} | Format: {st.format} | Price: ₹{st.price_min}-{st.price_max}")
```

### Asynchronous Usage (`asyncio`)

```python
import asyncio
from bms_scraper import BookMyShowScraper

async def main():
    scraper = BookMyShowScraper()
    
    # Asynchronous movie & venue details scraping call
    details = await scraper.async_get_movie_details("ET00378770", city="mumbai")
    venue = await scraper.async_get_venue_details("CSWO", city="mumbai")
    
    print(f"Movie Title: {details.title}")
    print(f"Venue Coords: Lat {venue.latitude}, Lon {venue.longitude}")

asyncio.run(main())
```

---

## 💻 Command Line Interface (CLI)

```bash
python -m bms_scraper.cli <subcommand> [options]
```

### Examples

```bash
# List popular cities
python -m bms_scraper.cli cities --popular

# Scrape movies in Bengaluru and export to Excel
python -m bms_scraper.cli movies --city bengaluru --language Hindi --export xlsx

# Fetch cinema showtimes and export to JSON
python -m bms_scraper.cli showtimes --code ET00378770 --city mumbai --export json
```

---

## 📊 Data Export Utilities

```python
from bms_scraper import BookMyShowScraper, DataExporter

scraper = BookMyShowScraper()
movies = scraper.get_movies(city="mumbai")

# Export options
DataExporter.to_csv(movies, "mumbai_movies.csv")
DataExporter.to_excel(movies, "mumbai_movies.xlsx")
DataExporter.to_json(movies, "mumbai_movies.json")
```

---

## 🧪 Running Tests

Run the full test suite using `pytest`:

```bash
python -m pytest
```

Expected output:
```text
============================= test session starts =============================
collected 17 items

tests\test_api.py .........                                              [ 52%]
tests\test_mcp.py ....                                                   [ 76%]
tests\test_scraper.py ....                                               [100%]

============================= 17 passed in 8.15s ==============================
```

---

## ⚖️ Disclaimer & License

This project is intended strictly for personal research and educational purposes. Ensure compliance with BookMyShow's Terms of Service when scraping public web data.

Distributed under the MIT License.
