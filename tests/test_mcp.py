"""
Tests for BookMyShow MCP Server tools.
"""

import asyncio
from bms_scraper.mcp_server import (
    bms_get_cities,
    bms_get_movies,
    bms_get_events,
    bms_get_movie_details,
    bms_get_showtimes,
    bms_get_venue_details,
    bms_search,
    mcp,
)


def test_mcp_tool_registration():
    """Test that all 7 tools are registered on the FastMCP/MCPServer instance."""
    tools = asyncio.run(mcp.list_tools())
    tool_names = [tool.name for tool in tools]
    assert "bms_get_cities" in tool_names
    assert "bms_get_movies" in tool_names
    assert "bms_get_events" in tool_names
    assert "bms_get_movie_details" in tool_names
    assert "bms_get_showtimes" in tool_names
    assert "bms_get_venue_details" in tool_names
    assert "bms_search" in tool_names


def test_bms_get_cities_tool():
    """Test bms_get_cities MCP tool handler."""
    cities = asyncio.run(bms_get_cities(popular_only=True))
    assert isinstance(cities, list)
    assert len(cities) > 0
    first_city = cities[0]
    assert "name" in first_city
    assert "code" in first_city
    assert "slug" in first_city


def test_bms_get_venue_details_tool():
    """Test bms_get_venue_details MCP tool handler."""
    venue = asyncio.run(bms_get_venue_details(venue_code="PCAN", city="chennai"))
    assert isinstance(venue, dict)
    assert venue.get("venue_code") == "PCAN"
    assert "latitude" in venue
    assert "longitude" in venue


def test_bms_search_tool():
    """Test bms_search MCP tool handler."""
    results = asyncio.run(bms_search(query="Kalki", city="mumbai"))
    assert isinstance(results, dict)
    assert "movies" in results
    assert "events" in results
