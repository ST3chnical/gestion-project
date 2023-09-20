from pydantic import BaseModel


class Comment(BaseModel):
    comment_id: int
    comment_content: str
    creation_date: str
    user_id: int
    project_id: int
