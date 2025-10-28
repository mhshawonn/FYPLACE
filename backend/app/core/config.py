"""
Application configuration constants and helpers.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables where possible."""

    overpass_urls: List[str] = Field(
        default_factory=lambda: [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.openstreetmap.ru/api/interpreter",
        ]
    )
    http_timeout: int = 45
    crawl_sleep_seconds: float = 1.0
    enable_website_email_discovery: bool = False
    overpass_retry_attempts: int = 3
    user_agent: str = "FindYourPlace/1.0 (+https://example.com)"
    max_parallel_category_requests: int = Field(
        4,
        description="Upper bound for parallel Overpass category calls.",
    )
    distance_tolerance_factor: float = Field(
        1.05,
        description="Multiplier applied to the requested radius when filtering results by distance.",
    )
    search_cache_ttl_seconds: int = Field(
        120,
        ge=0,
        description="TTL for in-memory search cache backing repeated export requests.",
    )
    search_cache_max_entries: int = Field(
        128,
        ge=1,
        description="Maximum number of cached search responses to retain in memory.",
    )
    mock_places_path: Optional[str] = Field(
        default=str((Path(__file__).resolve().parent.parent / "data" / "sample_places.json")),
        description="Optional path to static places data used when Overpass is unavailable.",
    )

    class Config:
        env_prefix = "FYP_"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


DEFAULT_CATEGORIES = {
    "school": {"key": "amenity", "values": ["school"]},
    "college": {"key": "amenity", "values": ["college", "university"]},
    "hospital": {"key": "amenity", "values": ["hospital", "clinic"]},
    "hotel": {
        "key": "tourism",
        "values": ["hotel", "motel", "hostel", "guest_house"],
    },
}
