from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin_role, require_member_role
from app.crud.project import (
    create_project,
    delete_project,
    get_all_projects,
    get_project_by_id,
    update_project,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/api/projects", tags=["Projects"])

def _require_admin(project, current_user: User) -> None:
    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator can perform this action.",
        )

def _get_project_or_404(db: Session, project_id: int):
    project = get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found.",
        )
    return project

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    responses={
        201: {"description": "Project created; the current user becomes its admin."},
        422: {"description": "Validation error"},
    },
)
def create_new_project(
    payload: ProjectCreate,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
) -> ProjectResponse:
    db_project = create_project(
        db,
        name=payload.name,
        created_by=current_user.id,
        description=payload.description,
    )
    return ProjectResponse.from_orm_with_creator(db_project)

@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List all projects",
    responses={401: {"description": "Not authenticated"}},
)
def list_projects(
    current_user: Annotated[User, Depends(require_member_role)],
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0, description="Records to skip (offset)."),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return."),
    mine_only: bool = Query(
        default=False,
        description="When true, return only projects created by the current user.",
    ),
) -> ProjectListResponse:
    if mine_only:
        from app.crud.project import get_projects_by_creator
        projects, total = get_projects_by_creator(db, current_user.id, skip=skip, limit=limit)
    else:
        if current_user.role == "admin":
            projects, total = get_all_projects(db, skip=skip, limit=limit)
        else:
            from app.crud.project import get_projects_by_assigned_user
            projects, total = get_projects_by_assigned_user(db, current_user.id, skip=skip, limit=limit)

    return ProjectListResponse(
        total=total,
        projects=[ProjectResponse.from_orm_with_creator(p) for p in projects],
    )

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project by ID",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Project not found"},
    },
)
def get_project(
    project_id: int,
    current_user: Annotated[User, Depends(require_member_role)],
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = _get_project_or_404(db, project_id)
    return ProjectResponse.from_orm_with_creator(project)

@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project (admin only)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Only the project creator can update it"},
        404: {"description": "Project not found"},
    },
)
def update_existing_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = _get_project_or_404(db, project_id)
    _require_admin(project, current_user)

    updated = update_project(db, project_id, name=payload.name, description=payload.description)
    return ProjectResponse.from_orm_with_creator(updated)

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project (admin only)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Only the project creator can delete it"},
        404: {"description": "Project not found"},
    },
)
def delete_existing_project(
    project_id: int,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
) -> None:
    project = _get_project_or_404(db, project_id)
    _require_admin(project, current_user)
    delete_project(db, project_id)
