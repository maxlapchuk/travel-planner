from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from places.schemas import PlaceImport, ProjectPlaceOut


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[date] = None
    places: Optional[List[PlaceImport]] = Field(
        default=None,
        description="Optional list of places to import from the Art Institute API (max 10)"
    )

    @field_validator("places")
    @classmethod
    def validate_places_count(cls, v):
        if v is not None:
            if len(v) < 1:
                raise ValueError("If provided, at least 1 place must be included.")
            if len(v) > 10:
                raise ValueError("A project cannot have more than 10 places.")
            ids = [p.external_id for p in v]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate external_id values in places list.")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[date] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    status: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    places: List[ProjectPlaceOut] = []

    model_config = {"from_attributes": True}


class ProjectListOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    status: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedProjects(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ProjectListOut]
