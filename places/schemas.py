from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


class PlaceImport(BaseModel):
    external_id: int = Field(..., gt=0, description="Artwork ID from Art Institute of Chicago API")


class ProjectPlaceCreate(BaseModel):
    external_id: int = Field(..., gt=0)


class ProjectPlaceUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=5000)
    visited: Optional[bool] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "ProjectPlaceUpdate":
        if self.notes is None and self.visited is None:
            raise ValueError("At least one of 'notes' or 'visited' must be provided.")
        return self


class ProjectPlaceOut(BaseModel):
    id: int
    project_id: int
    external_id: int
    title: Optional[str]
    artist: Optional[str]
    image_url: Optional[str]
    notes: Optional[str]
    visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPlaces(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ProjectPlaceOut]
