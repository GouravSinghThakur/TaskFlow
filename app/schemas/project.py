from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

class ProjectCreator(BaseModel):

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}

class ProjectCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        examples=["Website Redesign"],
        description="Project name (1–200 characters).",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        examples=["A full redesign of the marketing site."],
        description="Optional description (max 2 000 characters).",
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Project name cannot be blank or whitespace only.")
        return v.strip()

    model_config = {"str_strip_whitespace": True}

class ProjectUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        examples=["Website Redesign v2"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Project name cannot be blank or whitespace only.")
        return v.strip() if v else v

    model_config = {"str_strip_whitespace": True}

class ProjectResponse(BaseModel):

    id: int
    name: str
    description: Optional[str]
    created_by: int
    creator: Optional[ProjectCreator] = None   # populated from the relationship
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_creator(cls, project) -> "ProjectResponse":
        obj = cls.model_validate(project)
        if project.created_by_user:
            obj.creator = ProjectCreator.model_validate(project.created_by_user)
        return obj

class ProjectListResponse(BaseModel):

    total: int
    projects: list[ProjectResponse]
