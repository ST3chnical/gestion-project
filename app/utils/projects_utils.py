import strawberry
from typing import Optional
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d")


@strawberry.type
class Project:
    project_id: int
    project_name: str
    project_description: str
    start_date: str
    end_date: str
    responsible_id: str


@strawberry.type
class ProjectResponse:
    success: bool
    message: str


@strawberry.input
class ProjectInputCreate:
    project_name: str
    project_description: str
    start_date: Optional[str] = current_time
    end_date: Optional[str] = None
    responsible_id: Optional[int] = None


@strawberry.input
class ProjectUpdateInput:
    project_id: int
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsible_id: Optional[int] = None
