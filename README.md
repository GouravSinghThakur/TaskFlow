<div align="center">
  <h1>🚀 TaskFlow</h1>
  <p><b>A Production-Ready Team & Task Management REST API</b></p>
<href>taskflow-production-9bbb.up.railway.app\<href>
  <!-- Badges -->
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="TailwindCSS" />
  <img src="https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white" alt="Railway" />
</div>

<br />

> **TaskFlow** is a comprehensive, full-stack task management platform designed to demonstrate best practices in backend API design. Built with **FastAPI** and **SQLAlchemy**, it features a secure JWT authentication system, strict Role-Based Access Control (RBAC), and a responsive web interface powered by Jinja2 and Tailwind CSS.

---

## 🌟 Key Technical Achievements

- **Advanced Security & Authentication**: Implemented enterprise-grade security using `passlib` bcrypt hashing and `python-jose` for state-less JWT (JSON Web Token) authentication.
- **Role-Based Access Control (RBAC)**: Developed a tiered permission system utilizing FastAPI dependency injection. Admins can manage projects and users, while members are restricted to specific task-level interactions.
- **Optimized Database Aggregations**: Designed complex SQL queries (via SQLAlchemy) to compute real-time user statistics and dashboard metrics at the database level, avoiding costly Python loops.
- **Production-Ready Deployment**: Configured for seamless deployment on Railway, utilizing a robust PostgreSQL database, environment variable management, and WSGI/ASGI configurations via Uvicorn.
- **Clean Architecture**: Strictly adheres to MVC/layered architecture separating routes, CRUD operations, database models, and Pydantic schemas.

---

## 🏗️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend Framework** | FastAPI, Uvicorn |
| **Database & ORM** | PostgreSQL (Prod), SQLite (Dev), SQLAlchemy 2.0 |
| **Data Validation** | Pydantic v2 |
| **Security** | JWT Tokens, Bcrypt |
| **Frontend UI** | HTML5, Jinja2 Templates, Tailwind CSS |
| **Deployment** | Railway, Git |

---

## 📁 Project Architecture

The codebase follows a modular structure designed for scalability:

```text
app/
├── core/         # Core settings, security logic, and RBAC dependencies
├── crud/         # Database query logic (Separation of Concerns)
├── db/           # Database session management and base models
├── models/       # SQLAlchemy ORM definitions (User, Project, Task)
├── routes/       # FastAPI endpoints categorized by domain
├── schemas/      # Pydantic models for request/response validation
├── templates/    # Frontend UI (Jinja2 + TailwindCSS)
└── main.py       # Application factory
```

---

## 🔐 Role-Based Access Control (RBAC) Overview

| Action | Admin | Member | Assignee |
|--------|:---:|:---:|:---:|
| Create/Delete Projects | ✅ | ❌ | - |
| Create/Delete Tasks | ✅ | ❌ | - |
| View Assigned Projects/Tasks | ✅ | ✅ | ✅ |
| Update All Task Details | ✅ | ❌ | ❌ |
| Update Task Status Only | ✅ | ❌ | ✅ |
| Manage User Roles | ✅ | ❌ | - |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Setup
```bash
git clone https://github.com/GouravSinghThakur/TaskFlow.git
cd TaskFlow

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Open `.env` and configure your `SECRET_KEY`. You can generate a secure key using:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run the Application
```bash
python run.py
```
- **Web UI**: `http://localhost:8000/ui/login`
- **Interactive API Docs (Swagger)**: `http://localhost:8000/docs`

---

## 🌐 Live Deployment (Railway)

This application is fully configured for deployment on Railway.

1. Connect your GitHub repository to a new Railway project.
2. Provision a **PostgreSQL** database service.
3. Add the required Environment Variables in Railway (`SECRET_KEY`, `ALGORITHM=HS256`).
4. Railway will automatically detect the `Procfile` and `requirements.txt` to build and serve the app via Uvicorn.

---

## 📡 API Reference Snapshot

The API includes fully documented OpenAPI schemas (accessible at `/docs` when running).

- **`POST /api/auth/signup`**: Register new users
- **`POST /api/auth/login`**: Authenticate and retrieve JWT
- **`POST /api/projects`**: Create new team projects
- **`PATCH /api/tasks/{id}`**: Update task statuses
- **`GET /api/dashboard`**: Fetch real-time aggregated project/task metrics

---

<div align="center">
  <i>Developed by Gourav Singh Thakur</i>
</div>
