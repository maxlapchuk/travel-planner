from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from user.crud import get_current_user
import places.crud as places_crud
import projects.crud as projects_crud
from user.models import User
from .schemas import (
    PaginatedPlaces,
    ProjectPlaceCreate,
    ProjectPlaceOut,
    ProjectPlaceUpdate,
)
from projects.aic_service import validate_and_enrich

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


def _get_project_or_404(db, project_id, owner_id):
    project = projects_crud.get_project(db, project_id, owner_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.post("", response_model=ProjectPlaceOut, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: int,
    data: ProjectPlaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id, current_user.id)

    current_count = places_crud.count_places(db, project_id)
    if current_count >= places_crud.MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=409,
            detail=f"Project already has the maximum of {places_crud.MAX_PLACES_PER_PROJECT} places.",
        )

    if places_crud.get_place_by_external_id(db, project_id, data.external_id):
        raise HTTPException(status_code=409, detail="This place is already in the project.")

    try:
        enriched = await validate_and_enrich(data.external_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return places_crud.add_place(db, project, enriched)


@router.get("", response_model=PaginatedPlaces)
def list_places(
    project_id: int,
    visited: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    total, items = places_crud.list_places(db, project_id, visited=visited, page=page, page_size=page_size)
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{place_id}", response_model=ProjectPlaceOut)
def get_place(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    place = places_crud.get_place(db, project_id, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found.")
    return place


@router.patch("/{place_id}", response_model=ProjectPlaceOut)
def update_place(
    project_id: int,
    place_id: int,
    data: ProjectPlaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id, current_user.id)
    place = places_crud.get_place(db, project_id, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found.")

    updated = places_crud.update_place(db, place, data)

    projects_crud.sync_project_status(db, project)

    return updated
