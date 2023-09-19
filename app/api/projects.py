import strawberry
import typing
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from fastapi import HTTPException
from app.db.config import get_database_connection
from app.models.projects import Project
from app.utils.projects_utils import Project, ProjectResponse, ProjectInputCreate, ProjectUpdateInput
from app.security.token import verify_token
from psycopg2 import IntegrityError
from app.security.validation import is_user_admin

Info = _Info[BaseContext, RootValueType]


@strawberry.type
class ProjectQuery:
    @strawberry.field
    def project(self, info: Info, project_id: int) -> Project:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT project_id, project_name, project_description, start_date,"
                           " end_date, responsible_id FROM projects WHERE project_id = %s;", (project_id,))
            project_data = cursor.fetchone()

            if not project_data:
                raise HTTPException(status_code=404, detail="Project not found")

        project_dict = dict(zip(["project_id", "project_name", "project_description", "start_date",
                                 "end_date", "responsible_id"], project_data))
        if project_dict["end_date"] is None:
            project_dict["end_date"] = "None"
        if project_dict["responsible_id"] is None:
            project_dict["responsible_id"] = "None"
        project_dict["responsible_id"] = str(project_dict["responsible_id"])

        return Project(**project_dict)

    @strawberry.field
    def projects(self, info: Info) -> typing.List[Project]:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not a valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        with get_database_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT project_id, project_name, project_description, start_date,"
                           " end_date, responsible_id FROM projects;")
            projects_data = cursor.fetchall()

        projects = []
        for project_data in projects_data:
            project_id, project_name, project_description, \
                start_date, end_date, responsible_id = project_data

            # Handle null values
            if end_date is None:
                end_date = "None"
            if responsible_id is None:
                responsible_id = "None"
            responsible_id = str(responsible_id)

            project = Project(project_id=project_id,
                              project_name=project_name,
                              project_description=project_description,
                              start_date=start_date,
                              end_date=end_date,
                              responsible_id=responsible_id)
            projects.append(project)

        return projects


@strawberry.type
class ProjectMutation:
    @strawberry.mutation
    def create_project(self, info: Info, project: ProjectInputCreate) -> ProjectResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                cursor.execute("INSERT INTO projects (project_name, project_description, start_date,"
                               " end_date, responsible_id) VALUES (%s, %s, %s, %s, %s);",
                               (project.project_name, project.project_description, project.start_date,
                                project.end_date, project.responsible_id))
                connection.commit()
                project_id = cursor.lastrowid
                return ProjectResponse(success=True, message=f"Project {project_id} created")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Project already exists")
            else:
                raise HTTPException(status_code=500, detail="Error creating project")

    @strawberry.mutation
    def update_project(self, info: Info, _input: ProjectUpdateInput) -> ProjectResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not a valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not any([_input.project_name, _input.project_description, _input.start_date, _input.end_date,
                    _input.responsible_id]):
            raise HTTPException(status_code=400, detail="No valid fields provided for update")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                # Construir la consulta de actualización dinámica
                update_query = "UPDATE projects SET "
                update_params = []

                if _input.project_name:
                    update_query += "project_name = %s, "
                    update_params.append(_input.project_name)
                if _input.project_description:
                    update_query += "project_description = %s, "
                    update_params.append(_input.project_description)
                if _input.start_date:
                    update_query += "start_date = %s, "
                    update_params.append(_input.start_date)
                if _input.end_date:
                    update_query += "end_date = %s, "
                    update_params.append(_input.end_date)
                if _input.responsible_id:
                    update_query += "responsible_id = %s, "
                    update_params.append(_input.responsible_id)

                update_query = update_query.rstrip(", ")  # Eliminar la coma final
                update_query += " WHERE project_id = %s;"
                update_params.append(_input.project_id)

                cursor.execute(update_query, tuple(update_params))
                connection.commit()
                return ProjectResponse(success=True, message=f"Project {_input.project_id} updated")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Project already exists")
            else:
                raise HTTPException(status_code=500, detail="Error updating project")

    @strawberry.mutation
    def delete_project(self, info: Info, project_id: int) -> ProjectResponse:
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")

        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                cursor.execute("DELETE FROM projects WHERE project_id = %s;", (project_id,))
                connection.commit()
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Project not found")
                return ProjectResponse(success=True, message=f"Project {project_id} deleted")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=409, detail="Project already exists")
            else:
                raise HTTPException(status_code=500, detail="Error deleting project")
