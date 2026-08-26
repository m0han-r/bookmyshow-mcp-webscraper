"""
Unit tests for BookMyShow Scraper and Parser.
"""

import unittest
from bms_scraper.models import (
    City,
    MovieSummary,
    MovieDetailsResponse,
    ShowtimeItem,
    CinemaVenueShowtimes,
)
from bms_scraper.parser import BMSParser
from bms_scraper.scraper import BookMyShowScraper


class TestBMSScraper(unittest.TestCase):

    def test_city_parsing(self):
        cities = BMSParser.parse_cities(None)
        self.assertGreater(len(cities), 0)
        names = [c.name for c in cities]
        self.assertIn("Mumbai", names)
        self.assertIn("Bengaluru", names)

    def test_movie_summary_model(self):
        m = MovieSummary(
            title="Toxic",
            code="ET00378770",
            slug="toxic-a-fairy-tale-for-grownups",
            languages=["Kannada", "Hindi"],
            detail_url="https://in.bookmyshow.com/movies/mumbai/toxic/ET00378770",
        )
        self.assertEqual(m.title, "Toxic")
        self.assertEqual(m.code, "ET00378770")
        self.assertEqual(len(m.languages), 2)

    def test_showtime_model(self):
        s = ShowtimeItem(
            show_time="07:30 PM",
            format="IMAX 3D",
            price_min=350.0,
            price_max=600.0,
            availability="AVAILABLE",
        )
        self.assertEqual(s.show_time, "07:30 PM")
        self.assertEqual(s.format, "IMAX 3D")
        self.assertEqual(s.price_min, 350.0)

    def test_venue_model(self):
        v = CinemaVenueShowtimes(
            venue_code="CSWO",
            venue_name="Cinepolis: Nexus Seawoods",
            showtimes=[
                ShowtimeItem(show_time="10:00 AM", format="2D")
            ],
        )
        self.assertEqual(v.venue_code, "CSWO")
        self.assertEqual(len(v.showtimes), 1)


if __name__ == "__main__":
    unittest.main()
