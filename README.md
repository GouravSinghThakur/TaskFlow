# 📋 Team Task Manager

> A production-ready REST API for managing team projects and tasks — built with FastAPI, SQLAlchemy, and JWT authentication. Includes a Jinja2 web UI, role-based access control, and one-click deployment to Railway.

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure signup/login with `passlib` bcrypt hashing and `python-jose` tokens
- 👥 **Role-Based Access Control** — `Admin` and `Member` roles with reusable FastAPI dependency guards
- 📁 **Project Management** — Create, list, update, and delete projects; creator becomes project admin
- ✅ **Task Management** — Full task lifecycle with status (`TODO` → `IN_PROGRESS` → `DONE`), priority, due dates, and assignment
- 📊 **Dashboard** — Per-user statistics computed with DB-level aggregation (zero Python loops)
- 🌐 **Web UI** — Five Jinja2/Tailwind pages: Login, Signup, Dashboard, Projects, Tasks
- 🚀 **Railway-ready** — `Procfile`, `runtime.txt`, pinned `requirements.txt`, and PostgreSQL support

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) 0.115 |
| **ORM / DB** | [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 + SQLite (dev) / PostgreSQL (prod) |
| **Auth** | `python-jose` (JWT) + `passlib[bcrypt]` (password hashing) |
| **Validation** | [Pydantic](https://docs.pydantic.dev/) v2 |
| **Templating** | Jinja2 + Tailwind CSS (CDN) |
| **Server** | Uvicorn (ASGI) |
| **Deployment** | [Railway](https://railway.app) |

---

## 📁 Project Structure

```
Live Task Manager/
├── app/
│   ├── core/
│   │   ├── config.py         # Pydantic settings (env vars)
│   │   ├── security.py       # Password hashing + JWT helpers
│   │   └── dependencies.py   # Reusable FastAPI dependencies (RBAC)
│   ├── crud/
│   │   ├── user.py           # User CRUD + role update
│   │   ├── project.py        # Project CRUD + pagination
│   │   └── task.py           # Task CRUD + membership check
│   ├── db/
│   │   ├── base.py           # SQLAlchemy declarative base
│   │   ├── database.py       # Engine + session factory
│   │   └── session.py        # get_db dependency
│   ├── models/               # SQLAlchemy ORM models
│   ├── routes/               # FastAPI routers
│   │   ├── auth.py           # /api/auth/*
│   │   ├── projects.py       # /api/projects/*
│   │   ├── tasks.py          # /api/tasks/*
│   │   ├── dashboard.py      # /api/dashboard
│   │   └── ui.py             # /ui/* (HTML pages)
│   ├── schemas/              # Pydantic request/response models
│   ├── static/               # Static assets
│   ├── templates/            # Jinja2 HTML templates
│   └── main.py               # App factory + router registration
├── Procfile                  # Railway start command
├── runtime.txt               # Python version pin
├── requirements.txt          # Pinned dependencies
├── run.py                    # Local dev entry point
└── .env.example              # Environment variable template
```

---

## 🚀 Local Installation

### Prerequisites

- Python 3.11+
- `pip`

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USER/team-task-manager.git
cd team-task-manager

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum, set a real SECRET_KEY (see below)

# 5. Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Paste the output as SECRET_KEY in your .env

# 6. Start the development server
python run.py
```

The app will be running at **http://localhost:8000**

| URL | Description |
|---|---|
| `http://localhost:8000/` | → Redirects to Web UI |
| `http://localhost:8000/ui/login` | Login page |
| `http://localhost:8000/docs` | Interactive Swagger docs |
| `http://localhost:8000/redoc` | ReDoc API reference |
| `http://localhost:8000/health` | Health check |

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```dotenv
# Database
DATABASE_URL=sqlite:///./task_manager.db   # local dev
# DATABASE_URL=postgresql://user:pass@host:5432/railway  # production

# JWT — REQUIRED: generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=REPLACE_WITH_A_STRONG_RANDOM_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
DEBUG=False
APP_NAME=Team Task Manager
APP_VERSION=0.1.0
```

> **Never commit your `.env` file.** It is already in `.gitignore`.

---

## 📡 API Reference

All API endpoints are prefixed with `/api`. Protected endpoints require:
```
Authorization: Bearer <your_jwt_token>
```

### Authentication — `/api/auth`

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/auth/signup` | ❌ | — | Register a new account (role: `member`) |
| `POST` | `/api/auth/login` | ❌ | — | Login; returns JWT token |
| `GET` | `/api/auth/me` | ✅ | Any | Get current user profile |
| `POST` | `/api/auth/refresh` | ✅ | Any | Issue a fresh token |
| `POST` | `/api/auth/logout` | ✅ | Any | Client-side logout signal |
| `GET` | `/api/auth/admin/users` | ✅ | **Admin** | List all users |
| `PATCH` | `/api/auth/admin/users/{user_id}/role` | ✅ | **Admin** | Promote / demote a user |

### Projects — `/api/projects`

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/projects` | ✅ | **Admin** | Create a project (caller becomes creator) |
| `GET` | `/api/projects` | ✅ | Member+ | List all projects (`?mine_only=true` to filter) |
| `GET` | `/api/projects/{id}` | ✅ | Member+ | Get project details + creator info |
| `PUT` | `/api/projects/{id}` | ✅ | **Admin** + creator | Update name / description |
| `DELETE` | `/api/projects/{id}` | ✅ | **Admin** + creator | Delete project and all its tasks |

### Tasks — `/api/tasks`

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/tasks` | ✅ | **Admin** | Create a task inside a project |
| `GET` | `/api/tasks/project/{id}` | ✅ | Member+ | List project tasks (`?status=` `?priority=`) |
| `GET` | `/api/tasks/user/assigned` | ✅ | Member+ | Tasks assigned to current user |
| `GET` | `/api/tasks/{id}` | ✅ | Member+ | Get single task + assignee info |
| `PATCH` | `/api/tasks/{id}` | ✅ | Tiered* | Partial update |
| `DELETE` | `/api/tasks/{id}` | ✅ | **Admin** | Delete a task |

\* **PATCH permission tiers:**
- **Admin** (project creator) → all fields
- **Assignee** (task assigned to them) → `status` only
- Other members → `403 Forbidden`

### Dashboard — `/api/dashboard`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/dashboard` | ✅ | Stats: projects, tasks by status/priority, overdue, assigned |

<details>
<summary>Sample dashboard response</summary>

```json
{
  "user_id": 1,
  "user_name": "Jane Doe",
  "projects_as_admin": 3,
  "projects_as_member": 2,
  "total_tasks_in_my_projects": 15,
  "tasks_by_status": { "todo": 6, "in_progress": 5, "done": 4 },
  "tasks_by_priority": { "low": 3, "medium": 8, "high": 4 },
  "overdue_tasks": 2,
  "assigned_to_me": {
    "total": 5, "todo": 2, "in_progress": 2, "done": 1, "overdue": 1
  },
  "completion_rate_pct": 26.7
}
```
</details>

---

## 🔐 Role-Based Access Control

| Permission | Admin | Member |
|---|:---:|:---:|
| Create projects | ✅ | ❌ |
| View projects (member of) | ✅ | ✅ |
| Update / delete own project | ✅ | ❌ |
| Create tasks | ✅ | ❌ |
| View tasks in member projects | ✅ | ✅ |
| Update any task field | ✅ | ❌ |
| Update status of assigned task | ✅ | ✅ |
| Delete tasks | ✅ | ❌ |
| List all users | ✅ | ❌ |
| Promote / demote users | ✅ | ❌ |

All roles are enforced by three reusable FastAPI dependencies in `app/core/dependencies.py`:

```python
# Use in any route:
from app.core.dependencies import require_admin_role, require_member_role, require_roles

@router.post("/projects")
def create_project(user: Annotated[User, Depends(require_admin_role)], ...):
    ...
```

---

## 🌐 Web UI

Five Jinja2-rendered pages served under `/ui/*`:

| URL | Page |
|---|---|
| `/ui/login` | Login form |
| `/ui/signup` | Registration form |
| `/ui/dashboard` | Stats dashboard |
| `/ui/projects` | Project list + create modal |
| `/ui/tasks` | Task table + status update modal |

All pages store the JWT in `localStorage` and call the REST API via `fetch()`. No page reloads — state is managed client-side.

---

## 🚢 Railway Deployment

### Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

### Manual Steps

**1. Push to GitHub**
```bash
git add .
git commit -m "chore: deploy to Railway"
git push origin main
```

**2. Create Railway project**
- New Project → Deploy from GitHub Repo → select your repo
- Railway auto-detects the `Procfile`

**3. Add PostgreSQL**
- **+ New** → Database → PostgreSQL
- `DATABASE_URL` is injected automatically

**4. Set environment variables** in Railway dashboard → Variables:

| Variable | Value |
|---|---|
| `SECRET_KEY` | Run `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `DEBUG` | `False` |

> `DATABASE_URL` and `PORT` are injected by Railway — do **not** set them manually.

**5. Bootstrap first Admin user**
```bash
# Sign up
curl -X POST https://YOUR-APP.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin","email":"admin@example.com","password":"S3cur3P@ss!"}'

# Login and grab token
TOKEN=$(curl -s -X POST https://YOUR-APP.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"S3cur3P@ss!"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Promote to Admin (user id=1)
curl -X PATCH https://YOUR-APP.railway.app/api/auth/admin/users/1/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"admin"}'
```

**Start command** (handled by Procfile automatically):
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎮 Demo Usage

### 1. Sign Up and Log In

```bash
# Create account
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","email":"jane@example.com","password":"S3cur3P@ss!"}'

# Login — save the token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"S3cur3P@ss!"}'
```

### 2. Create a Project (Admin only)

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Website Redesign","description":"Full rebrand of the marketing site"}'
```

### 3. Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design hero section",
    "description": "New brand colours and typography",
    "project_id": 1,
    "priority": "High",
    "assigned_to": 2,
    "due_date": "2025-12-31T23:59:00"
  }'
```

### 4. Update Task Status (Assignee)

```bash
curl -X PATCH http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer ASSIGNEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"IN_PROGRESS"}'
```

### 5. View Dashboard

```bash
curl http://localhost:8000/api/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🛠️ Development

```bash
# Run tests (smoke test the full import + route chain)
python -c "from app.main import app; print('OK')"

# Regenerate DB schema (drops all data)
python -c "
from app.db.base import Base
from app.db.database import engine
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print('Schema recreated.')
"

# Interactive API docs
open http://localhost:8000/docs
```

---

## 📄 License

MIT © 2025 Team Task Manager Contributors
