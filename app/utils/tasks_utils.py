import strawberry
from typing import Optional


@strawberry.type
class Tasks:
    task_id: int
    task_name: str
    task_description: str
    deadline: str
    task_status: str
    project_id: int
    responsible_id: int


@strawberry.type
class TasksResponse:
    success: bool
    message: str

@strawberry.input
class TasksInputCreate:
    task_name: str
    task_description: str
    deadline: Optional[str] = None
    task_status: str
    project_id: int
    responsible_id: int

@strawberry.input
class TasksUpdateInput:
    task_id: int
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    deadline: Optional[str] = None
    task_status: Optional[str] = None
    project_id: Optional[int] = None
    responsible_id: Optional[int] = None
