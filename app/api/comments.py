import strawberry
import typing
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from fastapi import HTTPException
from app.db.config import get_database_connection
from app.models.comments import Comment
from app.utils.comments_utils import Comment, CommentResponse, CommentInputCreate, CommentUpdateInput
from app.security.token import verify_token
from psycopg2 import IntegrityError
from app.security.validation import is_user_admin

Info = _Info[BaseContext, RootValueType]


@strawberry.type
class CommentQuery:
    @strawberry.field
    def comment(self, info: Info, comment_id: int) -> Comment:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT comment_id, comment_content, user_id,"
                           " project_id FROM comments WHERE comment_id = %s;", (comment_id,))
            comment_data = cursor.fetchone()

            if not comment_data:
                raise HTTPException(status_code=404, detail="Comment not found")

        comment_dict = dict(zip(["comment_id", "comment_content", "user_id",
                                 "project_id"], comment_data))
        return Comment(**comment_dict)

    @strawberry.field
    def comments(self, info: Info) -> typing.List[Comment]:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not a valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT comment_id, comment_content, user_id,"
                           " project_id FROM comments;")
            comments_data = cursor.fetchall()

        comments = []
        for comment in comments_data:
            comment_dict = dict(zip(["comment_id", "comment_content", "user_id",
                                     "project_id"], comment))
            comments.append(Comment(**comment_dict))

        return comments


@strawberry.type
class CommentMutation:
    @strawberry.mutation
    def create_comment(self, info: Info, comment_data: CommentInputCreate) -> CommentResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                cursor.execute("INSERT INTO comments (comment_content, creation_date, user_id, project_id)"
                               " VALUES (%s, %s, %s, %s);",
                               (comment_data.comment_content, comment_data.creation_date,
                                comment_data.user_id, comment_data.project_id))
                connection.commit()
                return CommentResponse(success=True, message=f"Comment created successfully")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Comment already exists")
            else:
                raise HTTPException(status_code=500, detail="Error creating comment")

    @strawberry.mutation
    def update_comment(self, info: Info, _input: CommentUpdateInput) -> CommentResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not any([_input.comment_content, _input.creation_date, _input.user_id, _input.project_id]):
            raise HTTPException(status_code=400, detail="No data to update")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                update_query = "UPDATE comments SET "
                update_params = []

                if _input.comment_content:
                    update_query += "comment_content = %s, "
                    update_params.append(_input.comment_content)
                if _input.creation_date:
                    update_query += "creation_date = %s, "
                    update_params.append(_input.creation_date)
                if _input.user_id:
                    update_query += "user_id = %s, "
                    update_params.append(_input.user_id)
                if _input.project_id:
                    update_query += "project_id = %s, "
                    update_params.append(_input.project_id)

                update_query = update_query.rstrip(", ")
                update_query += " WHERE comment_id = %s;"
                update_params.append(_input.comment_id)

                cursor.execute(update_query, tuple(update_params))
                connection.commit()
                return CommentResponse(success=True, message=f"Comment {_input.comment_id} updated successfully")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Comment already exists")
            else:
                raise HTTPException(status_code=500, detail="Error updating comment")

    @strawberry.mutation
    def delete_comment(self, info: Info, comment_id: int) -> CommentResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                cursor.execute("DELETE FROM comments WHERE comment_id = %s;", (comment_id,))
                connection.commit()
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Comment not found")
                return CommentResponse(success=True, message=f"Comment {comment_id} deleted successfully")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Comment already exists")
            else:
                raise HTTPException(status_code=500, detail="Error deleting comment")
