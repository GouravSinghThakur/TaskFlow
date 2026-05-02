# Changelog

## Version 0.1.0 (Initial Release)

### Features Implemented
- User authentication (signup/login) with JWT tokens
- Password hashing with bcrypt
- Project creation and management
- Task creation, assignment, and status tracking
- Task status: Todo, In Progress, Done
- Dashboard with statistics:
  - Total projects
  - Total tasks
  - Completed tasks
  - In-progress tasks
  - Todo tasks
  - Overdue tasks
- SQLite database with SQLAlchemy ORM
- RESTful API endpoints
- Pydantic data validation
- CORS middleware support
- Jinja2 template support
- Static files support

### Project Structure
- Production-ready folder organization
- Separation of concerns (models, schemas, crud, routes)
- Centralized configuration management
- Security utilities module
- Database abstraction layer

### Technologies
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- SQLite
- PyJWT with bcrypt
- Pydantic 2.5.0
- Uvicorn 0.24.0
