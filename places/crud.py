from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from .models import ProjectPlace
from projects.models import TravelProject
from .schemas import ProjectPlaceUpdate

MAX_PLACES_PER_PROJECT = 10


def get_place(db: Session, project_id: int, place_id: int) -> Optional[ProjectPlace]:
    return (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id, ProjectPlace.id == place_id)
        .first()
    )


def get_place_by_external_id(db: Session, project_id: int, external_id: int) -> Optional[ProjectPlace]:
    return (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id, ProjectPlace.external_id == external_id)
        .first()
    )


def list_places(
    db: Session,
    project_id: int,
    visited: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[int, List[ProjectPlace]]:
    query = db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id)
    if visited is not None:
        query = query.filter(ProjectPlace.visited == visited)
    total = query.count()
    items = query.order_by(ProjectPlace.created_at.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def count_places(db: Session, project_id: int) -> int:
    return db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id).count()


def add_place(db: Session, project: TravelProject, enriched: dict) -> ProjectPlace:
    place = ProjectPlace(
        project_id=project.id,
        external_id=enriched["external_id"],
        title=enriched.get("title"),
        artist=enriched.get("artist"),
        image_url=enriched.get("image_url"),
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


def update_place(db: Session, place: ProjectPlace, data: ProjectPlaceUpdate) -> ProjectPlace:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(place, field, value)
    db.commit()
    db.refresh(place)
    return place