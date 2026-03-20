from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from user.crud import get_current_user
import projects.crud as projects_crud
from user.models import User
from .schemas import (
    PaginatedProjects,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
)
from .aic_service import validate_and_enrich

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enriched_places = None
    if data.places:
        enriched_places = []
        for place_ref in data.places:
            try:
                enriched = await validate_and_enrich(place_ref.external_id)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            enriched_places.append(enriched)

    return projects_crud.create_project(db, data, owner_id=current_user.id, enriched_places=enriched_places)


@router.get("", response_model=PaginatedProjects)
def list_projects(
    status: Optional[str] = Query(None, pattern="^(active|completed)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, items = projects_crud.list_projects(db, current_user.id, status=status, page=page, page_size=page_size)
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = projects_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = projects_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return projects_crud.update_project(db, project, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = projects_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if any(p.visited for p in project.places):
        raise HTTPException(
            status_code=409,
            detail="Project cannot be deleted because one or more places are already marked as visited.",
        )

    projects_crud.delete_project(db, project)
