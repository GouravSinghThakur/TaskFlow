from datetime import datetime
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.task import Task, TaskPriority, TaskStatus

def _base_query(db: Session):
    return db.query(Task).options(
        joinedload(Task.assigned_to_user),
        joinedload(Task.created_by_user),
        joinedload(Task.project),
    )

def is_project_member(db: Session, project_id: int, user_id: int) -> bool:
    from app.models.project import Project

    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        return False

    if project.created_by == user_id:
        return True

    assigned = (
        db.query(Task)
        .filter(Task.project_id == project_id, Task.assigned_to == user_id)
        .first()
    )
    return assigned is not None

def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    return _base_query(db).filter(Task.id == task_id).first()

def get_tasks_by_project(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[TaskStatus] = None,
    priority_filter: Optional[TaskPriority] = None,
) -> tuple[list[Task], int]:
    query = _base_query(db).filter(Task.project_id == project_id)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter)
    if priority_filter is not None:
        query = query.filter(Task.priority == priority_filter)

    total = query.count()
    tasks = (
        query.order_by(Task.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )
    return tasks, total

def get_tasks_by_assignee(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Task], int]:
    query = _base_query(db).filter(Task.assigned_to == user_id)
    total = query.count()
    tasks = (
        query.order_by(Task.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )
    return tasks, total

def create_task(
    db: Session,
    title: str,
    project_id: int,
    created_by: int,
    description: Optional[str] = None,
    assigned_to: Optional[int] = None,
    due_date: Optional[datetime] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> Task:
    db_task = Task(
        title=title,
        description=description,
        project_id=project_id,
        created_by=created_by,
        assigned_to=assigned_to,
        due_date=due_date,
        priority=priority,
        status=TaskStatus.TODO,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return get_task_by_id(db, db_task.id)

_UNSET = object()

def update_task(
    db: Session,
    task_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = _UNSET,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assigned_to: Optional[int] = _UNSET,
    due_date: Optional[datetime] = _UNSET,
) -> Optional[Task]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        return None

    if title is not None:
        task.title = title
    if description is not _UNSET:
        task.description = description
    if status is not None:
        task.status = status
    if priority is not None:
        task.priority = priority
    if assigned_to is not _UNSET:
        task.assigned_to = assigned_to
    if due_date is not _UNSET:
        task.due_date = due_date

    db.commit()
    db.refresh(task)
    return get_task_by_id(db, task_id)

def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        return False
    db.delete(task)
    db.commit()
    return True
