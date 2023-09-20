import strawberry
import typing
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from fastapi import HTTPException
from app.db.config import get_database_connection
from app.models.tasks import Tasks
from app.utils.tasks_utils import Tasks, TasksResponse, TasksInputCreate, TasksUpdateInput
from app.security.token import verify_token
from psycopg2 import IntegrityError
from app.security.validation import is_user_admin

Info = _Info[BaseContext, RootValueType]


@strawberry.type
class TaskQuery:
    @strawberry.field
    def task(self, info: Info, task_id: int) -> Tasks:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT task_id, task_name, task_description, deadline, task_status,"
                           " project_id, responsible_id FROM tasks WHERE task_id = %s;", (task_id,))
            task_data = cursor.fetchone()

            if not task_data:
                raise HTTPException(status_code=404, detail="Task not found")

        task_dict = dict(zip(["task_id", "task_name", "task_description", "deadline", "task_status",
                              "project_id", "responsible_id"], task_data))
        if task_dict["deadline"] is None:
            task_dict["deadline"] = "None"

        return Tasks(**task_dict)

    @strawberry.field
    def tasks(self, info: Info) -> typing.List[Tasks]:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not a valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT task_id, task_name, task_description, deadline, task_status,"
                           " project_id, responsible_id FROM tasks;")
            tasks_data = cursor.fetchall()

        tasks = []
        for task in tasks_data:
            task_dict = dict(zip(["task_id", "task_name", "task_description", "deadline", "task_status",
                                  "project_id", "responsible_id"], task))
            if task_dict["deadline"] is None:
                task_dict["deadline"] = "None"
            tasks.append(Tasks(**task_dict))

        return tasks


@strawberry.type
class TaskMutation:
    @strawberry.mutation
    def create_task(self, info: Info, task_data: TasksInputCreate) -> TasksResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO tasks (task_name, task_description, deadline, task_status,"
                               " project_id, responsible_id) VALUES (%s, %s, %s, %s, %s, %s);",
                               (task_data.task_name, task_data.task_description, task_data.deadline,
                                task_data.task_status, task_data.project_id, task_data.responsible_id))
            except IntegrityError:
                raise HTTPException(status_code=400, detail="Invalid data")

        return TasksResponse(success=True, message="Task created successfully")

    @strawberry.mutation
    def update_task(self, info: Info, _input: TasksUpdateInput) -> TasksResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not a valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not any([_input.task_name, _input.task_description, _input.deadline, _input.task_status,
                    _input.project_id, _input.responsible_id]):
            raise HTTPException(status_code=400, detail="Invalid data")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                update_query = "UPDATE tasks SET "
                update_params = []

                if _input.task_name:
                    update_query += "task_name = %s, "
                    update_params.append(_input.task_name)
                if _input.task_description:
                    update_query += "task_description = %s, "
                    update_params.append(_input.task_description)
                if _input.deadline:
                    update_query += "deadline = %s, "
                    update_params.append(_input.deadline)
                if _input.task_status:
                    update_query += "task_status = %s, "
                    update_params.append(_input.task_status)
                if _input.project_id:
                    update_query += "project_id = %s, "
                    update_params.append(_input.project_id)
                if _input.responsible_id:
                    update_query += "responsible_id = %s, "
                    update_params.append(_input.responsible_id)

                update_query = update_query.rstrip(", ")
                update_query += " WHERE task_id = %s;"
                update_params.append(_input.task_id)

                cursor.execute(update_query, tuple(update_params))
                connection.commit()
                return TasksResponse(success=True, message=f"Task {_input.task_id} updated successfully")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Task already exists")
            else:
                raise HTTPException(status_code=500, detail="Error updating task")

    @strawberry.mutation
    def delete_task(self, info: Info, task_id: int) -> TasksResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE task_id = %s;", (task_id,))
                connection.commit()
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Task not found")
                return TasksResponse(success=True, message=f"Task {task_id} deleted")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Task already exists")
            else:
                raise HTTPException(status_code=500, detail="Error updating task")
