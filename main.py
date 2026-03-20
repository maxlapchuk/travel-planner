from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from database import Base
import places.router as places
import projects.router as projects
import user.router as user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
    description="Manage travel projects and places powered by the Art Institute of Chicago.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router)
app.include_router(projects.router)
app.include_router(user.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "travel-planner"}
