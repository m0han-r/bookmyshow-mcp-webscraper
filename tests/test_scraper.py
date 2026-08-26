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
            date="20260828",
            showtimes=[
                ShowtimeItem(show_time="10:00 AM", format="2D")
            ],
        )
        self.assertEqual(v.venue_code, "CSWO")
        self.assertEqual(v.date, "20260828")
        self.assertEqual(len(v.showtimes), 1)

    def test_normalize_date(self):
        scraper = BookMyShowScraper()
        self.assertEqual(scraper._normalize_date("2026-08-28"), "20260828")
        self.assertEqual(scraper._normalize_date("20260828"), "20260828")
        self.assertEqual(scraper._normalize_date("2026/08/28"), "20260828")
        self.assertIsNone(scraper._normalize_date("invalid-date"))
        self.assertIsNone(scraper._normalize_date(None))

    def test_build_showtimes_url_with_code(self):
        scraper = BookMyShowScraper()
        url, code, dt = scraper._build_showtimes_url("ET00379308", city="chennai", date="2026-08-28")
        self.assertEqual(code, "ET00379308")
        self.assertEqual(dt, "20260828")
        self.assertTrue(url.endswith("/20260828"))

    def test_build_showtimes_url_with_full_url_and_query(self):
        scraper = BookMyShowScraper()
        full_url = "https://in.bookmyshow.com/movies/chennai/toxic/buytickets/ET00379308/20260828?etCodes=ET00379308&language=tamil"
        url, code, dt = scraper._build_showtimes_url(full_url, date="2026-08-28")
        self.assertEqual(code, "ET00379308")
        self.assertEqual(dt, "20260828")
        self.assertIn("/20260828?", url)
        self.assertIn("language=tamil", url)

    def test_build_showtimes_url_date_override(self):
        scraper = BookMyShowScraper()
        full_url = "https://in.bookmyshow.com/movies/chennai/toxic/buytickets/ET00379308/20260828?etCodes=ET00379308"
        url, code, dt = scraper._build_showtimes_url(full_url, date="20260829")
        self.assertEqual(code, "ET00379308")
        self.assertEqual(dt, "20260829")
        self.assertIn("/20260829?", url)
        self.assertNotIn("/20260828", url)

    def test_extract_language_event_codes(self):
        sample_state = {
            "showtimesFunctionalApi": {
                "queries": {
                    "fetchPrimaryDynamic-ET00378770---20260827-CHEN": {
                        "data": {
                            "data": {
                                "bottomSheetData": {
                                    "format-selector": {
                                        "widgets": [
                                            {
                                                "text": "Tamil",
                                                "data": [
                                                    {
                                                        "title": "2D",
                                                        "cta": {
                                                            "additionalData": {
                                                                "eventCode": "ET00379308",
                                                                "language": "Tamil",
                                                            }
                                                        },
                                                    }
                                                ],
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        lang_map = BMSParser.extract_language_event_codes(sample_state)
        self.assertIn("tamil", lang_map)
        self.assertEqual(lang_map["tamil"], ["ET00379308"])


if __name__ == "__main__":
    unittest.main()
