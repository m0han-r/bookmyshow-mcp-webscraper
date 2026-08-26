"""
Integration tests for FastAPI REST API endpoints.
"""

import unittest
from fastapi.testclient import TestClient
from main import app


class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")

    def test_cities_endpoint(self):
        response = self.client.get("/api/v1/cities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count"), 0)
        first_city = data["data"][0]
        self.assertIn("name", first_city)
        self.assertIn("code", first_city)

    def test_popular_cities_filter(self):
        response = self.client.get("/api/v1/cities?popular_only=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(all(c["is_popular"] for c in data["data"]))

    def test_movies_endpoint_mumbai(self):
        response = self.client.get("/api/v1/movies?city=mumbai")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count"), 0)

    def test_movies_endpoint_chennai(self):
        response = self.client.get("/api/v1/movies?city=chennai")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count"), 0)

    def test_events_endpoint_chennai(self):
        response = self.client.get("/api/v1/events?city=chennai")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count"), 0)

    def test_showtimes_endpoint(self):
        response = self.client.get("/api/v1/showtimes?movie_code=ET00378770&city=chennai")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count"), 0)

    def test_search_endpoint(self):
        response = self.client.get("/api/v1/search?q=Toxic&city=chennai")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("count"), 0)

    def test_venue_details_endpoint(self):
        response = self.client.get("/api/v1/venues/PCAN?city=chennai")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        venue_data = data.get("data")
        self.assertIsNotNone(venue_data)
        self.assertEqual(venue_data.get("venue_code"), "PCAN")
        self.assertIsNotNone(venue_data.get("latitude"))
        self.assertIsNotNone(venue_data.get("longitude"))


if __name__ == "__main__":
    unittest.main()
