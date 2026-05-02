# Team Task Manager - Development Guide

## Getting Started with Development

### Prerequisites
- Python 3.8+
- pip or conda package manager
- Git (optional)

### Quick Start

1. **Set up the environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Access the API**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - API Root: http://localhost:8000

## Project Structure Explained

### `app/core/`
- **config.py**: Centralized configuration using Pydantic Settings
- **security.py**: JWT token creation/validation and password hashing

### `app/db/`
- **base.py**: SQLAlchemy declarative base
- **database.py**: Database engine and session factory
- **session.py**: Dependency injection for database sessions

### `app/models/`
ORM models using SQLAlchemy:
- **user.py**: User model with relationships
- **project.py**: Project model linked to users
- **task.py**: Task model with status enum

### `app/schemas/`
Pydantic models for request/response validation:
- **user.py**: User schemas (Create, Login, Response)
- **project.py**: Project schemas
- **task.py**: Task schemas

### `app/crud/`
Create, Read, Update, Delete operations for each model:
- **user.py**: User CRUD + authentication
- **project.py**: Project CRUD
- **task.py**: Task CRUD

### `app/routes/`
FastAPI route handlers:
- **auth.py**: Sign up and login endpoints
- **projects.py**: Project management endpoints
- **tasks.py**: Task management endpoints
- **dashboard.py**: Dashboard statistics endpoint

### `app/main.py`
FastAPI application initialization with:
- Database table creation
- CORS middleware
- Route registration
- Static files & templates setup

## Environment Configuration

Edit `.env` file or set environment variables:

```
DATABASE_URL=sqlite:///./task_manager.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
APP_NAME=Team Task Manager
APP_VERSION=0.1.0
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Projects Table
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    owner_id INTEGER NOT NULL,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR DEFAULT 'Todo',
    project_id INTEGER NOT NULL,
    assigned_to_id INTEGER,
    due_date DATETIME,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assigned_to_id) REFERENCES users(id)
);
```

## Adding New Features

### Example: Add a Comment Feature

1. **Create model** (`app/models/comment.py`):
   ```python
   class Comment(Base):
       __tablename__ = "comments"
       
       id = Column(Integer, primary_key=True)
       text = Column(String)
       task_id = Column(Integer, ForeignKey("tasks.id"))
       user_id = Column(Integer, ForeignKey("users.id"))
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

2. **Create schema** (`app/schemas/comment.py`):
   ```python
   class CommentCreate(BaseModel):
       text: str
       task_id: int
   
   class CommentResponse(BaseModel):
       id: int
       text: str
       user_id: int
       created_at: datetime
   ```

3. **Create CRUD** (`app/crud/comment.py`):
   ```python
   def create_comment(db: Session, text: str, task_id: int, user_id: int):
       comment = Comment(text=text, task_id=task_id, user_id=user_id)
       db.add(comment)
       db.commit()
       db.refresh(comment)
       return comment
   ```

4. **Add route** (in `app/routes/tasks.py`):
   ```python
   @router.post("/tasks/{task_id}/comments")
   def add_comment(task_id: int, comment: CommentCreate, ...):
       # Implementation
       pass
   ```

## Testing Endpoints with cURL

### Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Create Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer {YOUR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Description here"
  }'
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer {YOUR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Task",
    "description": "Task description",
    "project_id": 1,
    "assigned_to_id": 1,
    "due_date": "2026-05-15T10:00:00"
  }'
```

### Update Task Status
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer {YOUR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Progress"
  }'
```

### Get Dashboard Stats
```bash
curl -X GET http://localhost:8000/api/dashboard \
  -H "Authorization: Bearer {YOUR_TOKEN}"
```

## Troubleshooting

### Database Issues
- Delete `task_manager.db` to reset the database
- Ensure database file path in `DATABASE_URL` is correct

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python path: `python -m site`

### Port Already in Use
- Change port in `run.py`: `uvicorn.run(..., port=8001)`
- Or kill process on port 8000: `lsof -ti:8000 | xargs kill -9`

## Performance Tips

1. **Database Indexing**: Add indexes to frequently queried columns
2. **Query Optimization**: Use SQLAlchemy eager loading (joinedload)
3. **Caching**: Implement Redis for dashboard stats
4. **Background Tasks**: Use Celery for async operations
5. **Pagination**: Implement for list endpoints

## Security Best Practices

1. ✅ Use strong `SECRET_KEY` in production
2. ✅ Enable HTTPS in production
3. ✅ Set `DEBUG=False` in production
4. ✅ Use environment variables for sensitive data
5. ✅ Implement rate limiting
6. ✅ Add input validation (already using Pydantic)
7. ✅ Use CORS carefully
8. ✅ Keep dependencies updated: `pip list --outdated`

## Useful Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Pydantic Documentation: https://docs.pydantic.dev/
- JWT Documentation: https://tools.ietf.org/html/rfc7519

## Common Git Workflow

```bash
# Create a feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to repository
git push origin feature/new-feature

# Create pull request and merge
```

## Deployment Checklist

- [ ] Update `SECRET_KEY` to secure random value
- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper logging
- [ ] Configure CORS appropriately
- [ ] Add environment-specific configuration
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring and alerts
- [ ] Set up automated backups
- [ ] Enable HTTPS/SSL
