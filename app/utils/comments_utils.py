import strawberry
from typing import Optional
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d")

@strawberry.type
class Comment:
    comment_id: int
    comment_content: str
    creation_date: str
    user_id: int
    project_id: int

@strawberry.type
class CommentResponse:
    success: bool
    message: str


@strawberry.input
class CommentInputCreate:
    comment_content: str
    creation_date: Optional[str] = current_time
    user_id: int
    project_id: int

@strawberry.input
class CommentUpdateInput:
    comment_id: int
    comment_content: Optional[str] = None
    creation_date: Optional[str] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None
