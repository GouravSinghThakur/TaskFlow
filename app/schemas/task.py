from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.task import TaskPriority, TaskStatus

class TaskUserRef(BaseModel):

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}

class TaskCreate(BaseModel):

    title: str = Field(
        ...,
        min_length=1,
        max_length=300,
        examples=["Design landing page"],
        description="Task title (1–300 characters).",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=4000,
        examples=["Redesign the hero section with new brand colours."],
        description="Optional description (max 4 000 characters).",
    )
    project_id: int = Field(..., description="ID of the project this task belongs to.")
    assigned_to: Optional[int] = Field(
        default=None,
        description="User ID to assign the task to (optional).",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority: Low | Medium | High.",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date (ISO-8601 datetime).",
    )

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank or whitespace only.")
        return v.strip()

    model_config = {"str_strip_whitespace": True}

class TaskStatusUpdate(BaseModel):

    status: TaskStatus = Field(..., description="New status: TODO | IN_PROGRESS | DONE.")

class TaskUpdate(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=300,
    )
    description: Optional[str] = Field(default=None, max_length=4000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = Field(
        default=None,
        description=(
            "User ID of the new assignee, or ``0`` / ``null`` to un-assign. "
            "Admin only."
        ),
    )
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be blank or whitespace only.")
        return v.strip() if v else v

    model_config = {"str_strip_whitespace": True}

class TaskResponse(BaseModel):

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    project_id: int
    assigned_to: Optional[int]
    assignee: Optional[TaskUserRef] = None    # populated from relationship
    created_by: Optional[int]
    creator: Optional[TaskUserRef] = None     # populated from relationship
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_full(cls, task) -> "TaskResponse":
        obj = cls.model_validate(task)
        if task.assigned_to_user:
            obj.assignee = TaskUserRef.model_validate(task.assigned_to_user)
        if task.created_by_user:
            obj.creator = TaskUserRef.model_validate(task.created_by_user)
        return obj

class TaskListResponse(BaseModel):

    total: int
    tasks: list[TaskResponse]
