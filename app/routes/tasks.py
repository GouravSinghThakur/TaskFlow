from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin_role, require_member_role
from app.crud.project import get_project_by_id
from app.crud.task import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks_by_assignee,
    get_tasks_by_project,
    is_project_member,
    update_task,
)
from app.crud.user import get_user_by_id
from app.db.session import get_db
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

def _get_task_or_404(db: Session, task_id: int) -> object:
    task = get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found.",
        )
    return task

def _get_project_or_404(db: Session, project_id: int) -> object:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found.",
        )
    return project

def _require_member(db: Session, project_id: int, user: User) -> None:
    if not is_project_member(db, project_id, user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project.",
        )

def _is_admin(project, user: User) -> bool:
    return project.created_by == user.id

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task (project admin only)",
    responses={
        201: {"description": "Task created successfully."},
        403: {"description": "Only the project admin can create tasks."},
        404: {"description": "Project or assigned user not found."},
        422: {"description": "Validation error."},
    },
)
def create_new_task(
    payload: TaskCreate,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    project = _get_project_or_404(db, payload.project_id)

    if not _is_admin(project, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project admin can create tasks.",
        )

    if payload.assigned_to is not None:
        if get_user_by_id(db, payload.assigned_to) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {payload.assigned_to} not found — cannot assign task.",
            )

    db_task = create_task(
        db,
        title=payload.title,
        project_id=payload.project_id,
        created_by=current_user.id,
        description=payload.description,
        assigned_to=payload.assigned_to,
        due_date=payload.due_date,
        priority=payload.priority,
    )
    return TaskResponse.from_orm_full(db_task)

@router.get(
    "/project/{project_id}",
    response_model=TaskListResponse,
    summary="List tasks in a project (project members only)",
    responses={
        403: {"description": "Not a project member."},
        404: {"description": "Project not found."},
    },
)
def list_project_tasks(
    project_id: int,
    current_user: Annotated[User, Depends(require_member_role)],
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Records to skip (offset)."),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return."),
    status_filter: Optional[TaskStatus] = Query(
        default=None, alias="status", description="Filter by task status."
    ),
    priority_filter: Optional[TaskPriority] = Query(
        default=None, alias="priority", description="Filter by task priority."
    ),
) -> TaskListResponse:
    project = _get_project_or_404(db, project_id)
    _require_member(db, project_id, current_user)

    assignee_filter = None
    if current_user.role != "admin" and project.created_by != current_user.id:
        assignee_filter = current_user.id

    tasks, total = get_tasks_by_project(
        db,
        project_id,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assignee_filter=assignee_filter,
    )
    return TaskListResponse(
        total=total,
        tasks=[TaskResponse.from_orm_full(t) for t in tasks],
    )

@router.get(
    "/user/assigned",
    response_model=TaskListResponse,
    summary="List tasks assigned to the current user",
    responses={401: {"description": "Not authenticated."}},
)
def list_my_assigned_tasks(
    current_user: Annotated[User, Depends(require_member_role)],
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> TaskListResponse:
    tasks, total = get_tasks_by_assignee(db, current_user.id, skip=skip, limit=limit)
    return TaskListResponse(
        total=total,
        tasks=[TaskResponse.from_orm_full(t) for t in tasks],
    )

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID (project members only)",
    responses={
        403: {"description": "Not a project member."},
        404: {"description": "Task not found."},
    },
)
def get_task(
    task_id: int,
    current_user: Annotated[User, Depends(require_member_role)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    task = _get_task_or_404(db, task_id)
    _require_member(db, task.project_id, current_user)
    
    if current_user.role != "admin" and task.project.created_by != current_user.id:
        if task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view tasks assigned to you.",
            )
            
    return TaskResponse.from_orm_full(task)

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task (admin: all fields | assignee: status only)",
    responses={
        403: {"description": "Insufficient permissions."},
        404: {"description": "Task not found."},
        422: {"description": "Validation error."},
    },
)
def patch_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> TaskResponse:
    task = _get_task_or_404(db, task_id)
    project = task.project
    is_admin = _is_admin(project, current_user)
    is_assignee = task.assigned_to == current_user.id

    if not is_admin and not is_assignee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task.",
        )

    if not is_admin and is_assignee:

        admin_only_fields = {"title", "description", "priority", "assigned_to", "due_date"}
        supplied = payload.model_fields_set
        disallowed = supplied & admin_only_fields
        if disallowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Assignees may only update 'status'. "
                    f"Disallowed field(s): {', '.join(sorted(disallowed))}."
                ),
            )
        if payload.status is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Assignees must supply a 'status' value.",
            )

    if is_admin and "assigned_to" in payload.model_fields_set:
        new_assignee = payload.assigned_to
        if new_assignee is not None and new_assignee != 0:
            if get_user_by_id(db, new_assignee) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {new_assignee} not found — cannot assign task.",
                )

    update_kwargs: dict = {}
    supplied = payload.model_fields_set

    if "title" in supplied and payload.title is not None:
        update_kwargs["title"] = payload.title
    if "description" in supplied:
        update_kwargs["description"] = payload.description
    if "status" in supplied and payload.status is not None:
        update_kwargs["status"] = payload.status
    if "priority" in supplied and payload.priority is not None:
        update_kwargs["priority"] = payload.priority
    if "assigned_to" in supplied:

        val = payload.assigned_to
        update_kwargs["assigned_to"] = None if (val is None or val == 0) else val
    if "due_date" in supplied:
        update_kwargs["due_date"] = payload.due_date

    updated = update_task(db, task_id, **update_kwargs)
    return TaskResponse.from_orm_full(updated)

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task (project admin only)",
    responses={
        403: {"description": "Only the project admin can delete tasks."},
        404: {"description": "Task not found."},
    },
)
def delete_existing_task(
    task_id: int,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
) -> None:
    task = _get_task_or_404(db, task_id)
    if not _is_admin(task.project, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project admin can delete tasks.",
        )
    delete_task(db, task_id)
