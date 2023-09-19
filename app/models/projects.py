from pydantic import BaseModel


class Project(BaseModel):
    project_id: int
    project_name: str
    project_description: str
    start_date: str
    end_date: str
    responsible_id: str
