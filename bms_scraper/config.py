"""
Configuration settings for BookMyShow Web Scraper.
"""

from typing import Dict, Any

class Config:
    BASE_URL: str = "https://in.bookmyshow.com"
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
    }
    
    REQUEST_TIMEOUT: int = 12
    CACHE_TTL_SECONDS: int = 300  # 5 minutes in-memory caching for scraper calls
    
    POPULAR_CITIES = [
        {"name": "Mumbai", "code": "MUMBAI", "slug": "mumbai", "state": "Maharashtra", "is_popular": True},
        {"name": "Delhi-NCR", "code": "NCR", "slug": "national-capital-region-ncr", "state": "Delhi", "is_popular": True},
        {"name": "Bengaluru", "code": "BANG", "slug": "bengaluru", "state": "Karnataka", "is_popular": True},
        {"name": "Hyderabad", "code": "HYD", "slug": "hyderabad", "state": "Telangana", "is_popular": True},
        {"name": "Ahmedabad", "code": "AHD", "slug": "ahmedabad", "state": "Gujarat", "is_popular": True},
        {"name": "Chandigarh", "code": "CHD", "slug": "chandigarh", "state": "Punjab/Haryana", "is_popular": True},
        {"name": "Chennai", "code": "CHEN", "slug": "chennai", "state": "Tamil Nadu", "is_popular": True},
        {"name": "Pune", "code": "PUNE", "slug": "pune", "state": "Maharashtra", "is_popular": True},
        {"name": "Kolkata", "code": "KOLK", "slug": "kolkata", "state": "West Bengal", "is_popular": True},
        {"name": "Kochi", "code": "KOCHI", "slug": "kochi", "state": "Kerala", "is_popular": True},
    ]

CONFIG = Config()
