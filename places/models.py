from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, String, Text, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from database import Base


class ProjectPlace(Base):
    __tablename__ = "project_places"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("travel_projects.id"), nullable=False)
    external_id = Column(Integer, nullable=False)
    title = Column(String(512), nullable=True)
    artist = Column(String(512), nullable=True)
    image_url = Column(String(1024), nullable=True)
    notes = Column(Text, nullable=True)
    visited = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("TravelProject", back_populates="places")

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_project_external"),
    )
