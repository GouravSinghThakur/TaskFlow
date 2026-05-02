from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/ui", tags=["UI"])

@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse, include_in_schema=False)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/projects", response_class=HTMLResponse, include_in_schema=False)
def projects_page(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request})

@router.get("/tasks", response_class=HTMLResponse, include_in_schema=False)
def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})

@router.get("", response_class=RedirectResponse, include_in_schema=False)
def ui_root():
    return RedirectResponse(url="/ui/dashboard")
