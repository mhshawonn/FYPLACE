"""
Pydantic schemas for search endpoints.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.config import DEFAULT_CATEGORIES


class SearchRequest(BaseModel):
    location: str = Field(..., description="Free-form location query (city, address, etc.)")
    radius_km: float = Field(5.0, gt=0, description="Search radius around the location in kilometres")
    categories: Optional[List[str]] = Field(None, description="Subset of categories to include")
    with_email_enrichment: bool = Field(False, description="Attempt to discover emails from websites")

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        invalid = [item for item in value if item not in DEFAULT_CATEGORIES]
        if invalid:
            raise ValueError(f"Unsupported categories: {', '.join(invalid)}")
        return value


class Place(BaseModel):
    osm_id: str
    category: str
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    address: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    source_tags: str


class SearchResponse(BaseModel):
    location_label: str
    radius_km: float
    categories: List[str]
    results: List[Place]
