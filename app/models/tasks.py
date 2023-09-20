from pydantic import BaseModel


class Tasks(BaseModel):
    task_id: int
    task_name: str
    task_description: str
    deadline: str
    task_status: str
    project_id: int
    responsible_id: int
