from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

class TasksByStatus(BaseModel):
    todo: int
    in_progress: int
    done: int

class TasksByPriority(BaseModel):
    low: int
    medium: int
    high: int

class AssignedTaskSummary(BaseModel):
    total: int
    todo: int
    in_progress: int
    done: int
    overdue: int

class DashboardStats(BaseModel):

    user_id: int
    user_name: str

    projects_as_admin: int        # projects the user created
    projects_as_member: int       # projects where user is assigned to a task

    total_tasks_in_my_projects: int
    tasks_by_status: TasksByStatus
    tasks_by_priority: TasksByPriority
    overdue_tasks: int            # non-DONE tasks past their due_date

    assigned_to_me: AssignedTaskSummary

    completion_rate_pct: float    # % of tasks DONE out of total_tasks_in_my_projects

def _query_dashboard(db: Session, user: User) -> DashboardStats:
    now = datetime.now(timezone.utc)
    user_id = user.id

    projects_as_admin: int = (
        db.query(func.count(Project.id))
        .filter(Project.created_by == user_id)
        .scalar() or 0
    )

    projects_as_member: int = (
        db.query(func.count(func.distinct(Task.project_id)))
        .join(Project, Project.id == Task.project_id)
        .filter(
            Task.assigned_to == user_id,
            Project.created_by != user_id,   # exclude own projects
        )
        .scalar() or 0
    )

    task_agg_query = db.query(
        func.count(Task.id).label("total"),
        func.sum(
            case((Task.status == TaskStatus.TODO, 1), else_=0)
        ).label("todo"),
        func.sum(
            case((Task.status == TaskStatus.IN_PROGRESS, 1), else_=0)
        ).label("in_progress"),
        func.sum(
            case((Task.status == TaskStatus.DONE, 1), else_=0)
        ).label("done"),
        func.sum(
            case((Task.priority == TaskPriority.LOW, 1), else_=0)
        ).label("low"),
        func.sum(
            case((Task.priority == TaskPriority.MEDIUM, 1), else_=0)
        ).label("medium"),
        func.sum(
            case((Task.priority == TaskPriority.HIGH, 1), else_=0)
        ).label("high"),
        func.sum(
            case(
                (
                    (Task.due_date < now) & (Task.status != TaskStatus.DONE),
                    1,
                ),
                else_=0,
            )
        ).label("overdue"),
    )

    from app.models.user import UserRole
    if user.role == UserRole.ADMIN:
        admin_task_agg = (
            task_agg_query
            .join(Project, Project.id == Task.project_id)
            .filter(Project.created_by == user_id)
            .one()
        )
    else:
        admin_task_agg = (
            task_agg_query
            .filter(Task.assigned_to == user_id)
            .one()
        )

    total_tasks      = int(admin_task_agg.total      or 0)
    todo_count       = int(admin_task_agg.todo       or 0)
    in_progress_count= int(admin_task_agg.in_progress or 0)
    done_count       = int(admin_task_agg.done       or 0)
    low_count        = int(admin_task_agg.low        or 0)
    medium_count     = int(admin_task_agg.medium     or 0)
    high_count       = int(admin_task_agg.high       or 0)
    overdue_count    = int(admin_task_agg.overdue    or 0)

    assigned_agg = (
        db.query(
            func.count(Task.id).label("total"),
            func.sum(
                case((Task.status == TaskStatus.TODO, 1), else_=0)
            ).label("todo"),
            func.sum(
                case((Task.status == TaskStatus.IN_PROGRESS, 1), else_=0)
            ).label("in_progress"),
            func.sum(
                case((Task.status == TaskStatus.DONE, 1), else_=0)
            ).label("done"),
            func.sum(
                case(
                    (
                        (Task.due_date < now) & (Task.status != TaskStatus.DONE),
                        1,
                    ),
                    else_=0,
                )
            ).label("overdue"),
        )
        .filter(Task.assigned_to == user_id)
        .one()
    )

    assigned_total       = int(assigned_agg.total       or 0)
    assigned_todo        = int(assigned_agg.todo        or 0)
    assigned_in_progress = int(assigned_agg.in_progress or 0)
    assigned_done        = int(assigned_agg.done        or 0)
    assigned_overdue     = int(assigned_agg.overdue     or 0)

    completion_rate = round(done_count / total_tasks * 100, 1) if total_tasks else 0.0

    return DashboardStats(
        user_id=user_id,
        user_name="",          # filled by the route after user is resolved
        projects_as_admin=projects_as_admin,
        projects_as_member=projects_as_member,
        total_tasks_in_my_projects=total_tasks,
        tasks_by_status=TasksByStatus(
            todo=todo_count,
            in_progress=in_progress_count,
            done=done_count,
        ),
        tasks_by_priority=TasksByPriority(
            low=low_count,
            medium=medium_count,
            high=high_count,
        ),
        overdue_tasks=overdue_count,
        assigned_to_me=AssignedTaskSummary(
            total=assigned_total,
            todo=assigned_todo,
            in_progress=assigned_in_progress,
            done=assigned_done,
            overdue=assigned_overdue,
        ),
        completion_rate_pct=completion_rate,
    )

@router.get(
    "",
    response_model=DashboardStats,
    summary="Get dashboard statistics for the current user",
    responses={401: {"description": "Not authenticated"}},
)
def get_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> DashboardStats:
    stats = _query_dashboard(db, current_user)
    stats.user_name = current_user.name
    return stats
