from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.base import Base
from app.db.database import engine
from app.routes import auth, projects, tasks, dashboard
from app.routes.ui import router as ui_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description=(
        "A full-stack team task manager with JWT auth, project management, "
        "task assignment, and a live dashboard. UI at [/ui/dashboard](/ui/dashboard)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)

app.include_router(ui_router)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/ui/dashboard")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
