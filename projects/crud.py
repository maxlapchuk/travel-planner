from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from .models import ProjectStatus, TravelProject
from .schemas import ProjectCreate, ProjectUpdate
from places.models import ProjectPlace


def get_project(db: Session, project_id: int, owner_id: int) -> Optional[TravelProject]:
    return (
        db.query(TravelProject)
        .filter(TravelProject.id == project_id, TravelProject.owner_id == owner_id)
        .first()
    )


def list_projects(
    db: Session,
    owner_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[int, List[TravelProject]]:
    query = db.query(TravelProject).filter(TravelProject.owner_id == owner_id)
    if status:
        query = query.filter(TravelProject.status == status)
    total = query.count()
    items = query.order_by(TravelProject.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def create_project(
    db: Session,
    data: ProjectCreate,
    owner_id: int,
    enriched_places: Optional[List[dict]] = None,
) -> TravelProject:
    project = TravelProject(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
        owner_id=owner_id,
    )
    db.add(project)
    db.flush()

    if enriched_places:
        for ep in enriched_places:
            place = ProjectPlace(
                project_id=project.id,
                external_id=ep["external_id"],
                title=ep.get("title"),
                artist=ep.get("artist"),
                image_url=ep.get("image_url"),
            )
            db.add(place)

    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: TravelProject, data: ProjectUpdate) -> TravelProject:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: TravelProject) -> None:
    db.delete(project)
    db.commit()


def sync_project_status(db: Session, project: TravelProject) -> None:
    if not project.places:
        return
    all_visited = all(p.visited for p in project.places)
    new_status = ProjectStatus.completed if all_visited else ProjectStatus.active
    if project.status != new_status:
        project.status = new_status
        db.commit()
