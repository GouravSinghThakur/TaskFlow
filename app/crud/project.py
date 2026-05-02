from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.project import Project

def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
    return (
        db.query(Project)
        .options(joinedload(Project.created_by_user))
        .filter(Project.id == project_id)
        .first()
    )

def get_all_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Project], int]:
    query = db.query(Project).options(joinedload(Project.created_by_user))
    total = query.count()
    projects = (
        query.order_by(Project.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )
    return projects, total

def get_projects_by_creator(
    db: Session,
    created_by: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Project], int]:
    query = (
        db.query(Project)
        .options(joinedload(Project.created_by_user))
        .filter(Project.created_by == created_by)
    )
    total = query.count()
    projects = (
        query.order_by(Project.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )
    return projects, total

def get_projects_by_assigned_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Project], int]:
    from app.models.task import Task
    query = (
        db.query(Project)
        .options(joinedload(Project.created_by_user))
        .join(Task, Task.project_id == Project.id)
        .filter(Task.assigned_to == user_id)
        .distinct()
    )
    total = query.count()
    projects = (
        query.order_by(Project.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )
    return projects, total

def create_project(
    db: Session,
    name: str,
    created_by: int,
    description: Optional[str] = None,
) -> Project:
    db_project = Project(name=name, description=description, created_by=created_by)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return get_project_by_id(db, db_project.id)

def update_project(
    db: Session,
    project_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[Project]:
    project = get_project_by_id(db, project_id)
    if project is None:
        return None
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    db.commit()
    db.refresh(project)
    return get_project_by_id(db, project_id)

def delete_project(db: Session, project_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        return False
    db.delete(project)
    db.commit()
    return True
