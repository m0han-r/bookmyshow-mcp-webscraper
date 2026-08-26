# 🎬 BookMyShow MCP Webscraper

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-supported-purple.svg)](#-mcp-server-setup)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#-running-tests)

A Python scraper and API wrapper for [BookMyShow](https://in.bookmyshow.com) that extracts movie listings, theater showtimes, ticket prices, and venue location details (including GPS latitude and longitude).

It packages everything into a **FastAPI REST server**, **MCP tools** (for AI assistants like Claude or Cursor), a **CLI tool**, and a **built-in web dashboard**.

---

## ✨ Features

- **Lists Movies & Events**: Gets active or upcoming movie listings across Indian cities (Mumbai, Delhi-NCR, Bengaluru, Chennai, etc.), with filters for language and genre.
- **Fetches Showtimes & Pricing**: Pulls cinema showtimes, screen formats (2D, 3D, IMAX, 4DX), ticket price ranges (in ₹), and seat availability.
- **Extracts Venue Locations & Lat/Long**: Pulls theater street addresses, exact latitude and longitude coordinates, and venue amenities (parking, food court, M-ticket entry).
- **Gets Movie Synopsis & Trailers**: Retrieves plot summaries, cast and crew info, ratings, posters, and YouTube trailer links.
- **Runs as an MCP Server**: Works out-of-the-box with AI tools (Claude Desktop, Cursor, Antigravity) via `mcp_server.py` or `uvx`.
- **FastAPI REST Server**: Interactive Swagger API docs (`/docs`).
- **Terminal CLI**: Terminal interface for search, listings, and exports.
- **Exports to Files**: Exports scraped data to JSON, CSV, or Excel (`.xlsx`).
- **Web Dashboard**: Simple light-theme dashboard to browse movies and test endpoints.

---

## 🚀 Quickstart & Installation

```bash
git clone https://github.com/m0han-r/bookmyshow-mcp-webscraper.git
cd bookmyshow-mcp-webscraper
pip install -r requirements.txt
```

---

## 🔌 API & MCP Tools

| REST Endpoint | MCP Tool Name | Parameters | Description |
| :--- | :--- | :--- | :--- |
| `GET /api/v1/cities` | `bms_get_cities` | `popular_only` | Supported Indian regions & popular cities |
| `GET /api/v1/movies` | `bms_get_movies` | `city, language, genre` | Active movie listings with language/genre filters |
| `GET /api/v1/events` | `bms_get_events` | `city, category` | Live events, comedy shows, music concerts, and sports |
| `GET /api/v1/movies/{code}` | `bms_get_movie_details` | `movie_code, city` | Synopsis, cast, crew, ratings, poster & trailer links |
| `GET /api/v1/showtimes` | `bms_get_showtimes` | `movie_code, city, date` | Showtimes, screen formats (IMAX/3D/4DX), prices & seats |
| `GET /api/v1/venues/{code}` | `bms_get_venue_details` | `venue_code, city` | Cinema street address, exact latitude, longitude & facilities |
| `GET /api/v1/search` | `bms_search` | `query, city` | Cross-search movies and live events |

#### Sample Venue Response (`GET /api/v1/venues/PCAN?city=chennai`):
```json
{
  "success": true,
  "count": 1,
  "data": {
    "venue_code": "PCAN",
    "venue_name": "PVR: VR Chennai, Anna Nagar",
    "address": "3rd Floor, VR Mall, Metro Zone, Jawaharlal Nehru Road, Anna Nagar, Chennai, Tamil Nadu 600040",
    "latitude": 13.082561,
    "longitude": 80.194803,
    "facilities": ["Ticket Cancellation", "F&B", "MTicket", "Parking Facility", "Food Court"]
  }
}
```

---

## 🌐 Running the REST API Server

Start the server:

```bash
python main.py
```

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)

---

## 🤖 MCP Server Setup

Connect your AI assistant (Claude Desktop, Cursor, Antigravity) using `uvx`:

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

Or run locally over stdio:
```bash
python mcp_server.py
```

---

## 🐍 Python Usage

```python
from bms_scraper import BookMyShowScraper

scraper = BookMyShowScraper()

# Get active movies
movies = scraper.get_movies(city="mumbai", language="Hindi")

# Get venue coordinates
venue = scraper.get_venue_details(venue_code_or_url="PCAN", city="chennai")
print(f"📍 {venue.venue_name} - Lat: {venue.latitude}, Lon: {venue.longitude}")

# Get showtimes
showtimes = scraper.get_showtimes(movie_code_or_url="ET00378770", city="mumbai")
```

---

## 💻 CLI Usage

```bash
# List popular cities
python -m bms_scraper.cli cities --popular

# Scrape movies in Bengaluru and export to Excel
python -m bms_scraper.cli movies --city bengaluru --language Hindi --export xlsx
```

---

## 📊 Exporting Data

```python
from bms_scraper import BookMyShowScraper, DataExporter

scraper = BookMyShowScraper()
movies = scraper.get_movies(city="mumbai")

DataExporter.to_csv(movies, "movies.csv")
DataExporter.to_excel(movies, "movies.xlsx")
DataExporter.to_json(movies, "movies.json")
```

---

## 🧪 Running Tests

```bash
python -m pytest
```

---

## ⚖️ License

Distributed under the MIT License.
