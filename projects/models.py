import enum
from sqlalchemy import (
    Column, Date, DateTime, Enum, ForeignKey,
    Integer, String, Text, func
)
from sqlalchemy.orm import relationship
from database import Base


class ProjectStatus(str, enum.Enum):
    active = "active"
    completed = "completed"


class TravelProject(Base):
    __tablename__ = "travel_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")

    places = relationship("ProjectPlace", back_populates="project", cascade="all, delete-orphan")
