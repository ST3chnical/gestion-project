import strawberry
import typing
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from fastapi import HTTPException
from app.db.config import get_database_connection
from app.models.user import User
from app.utils.user_utils import User, UserResponse, UserUpdateInput, UserInputCreate
from app.security.hash import get_password_hash
from app.security.token import verify_token
from psycopg2 import IntegrityError
from app.security.validation import is_user_admin

Info = _Info[BaseContext, RootValueType]


@strawberry.type
class UserQuery:
    @strawberry.field
    def user(self, info: Info, user_id: int) -> User:
        token = info.context["request"].headers["authorization"]
        token_verified = verify_token(token)
        if not token_verified:
            raise HTTPException(status_code=401, detail="Not valid token or token expired")
        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            with get_database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id, username, password,"
                                   " email, name, role_id FROM users WHERE user_id = %s;", (user_id,))
                    user_data = cursor.fetchone()

                    if not user_data:
                        raise HTTPException(status_code=404, detail="User not found")

                    user_dict = dict(zip(["user_id", "username", "password", "email", "name", "role_id"], user_data))
                    return User(**user_dict)

    @strawberry.field
    def users(self, info: Info) -> typing.List[User]:
        token = info.context["request"].headers["authorization"]
        token_verified = verify_token(token)
        if not token_verified:
            raise HTTPException(status_code=401, detail="Not valid token or token expired")
        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            with get_database_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id, username, email, password, name, role_id FROM users;")
                    users_data = cursor.fetchall()

                    users = []
                    for user_data in users_data:
                        user_id, username, email, password, name, role_id = user_data
                        user = User(user_id=user_id, username=username, password=password, email=email, name=name,
                                    role_id=role_id)
                        users.append(user)
                    return users


@strawberry.type
class UserMutation:
    @strawberry.mutation
    def create_user(self, info: Info, user: UserInputCreate) -> UserResponse:
        hashed_password = get_password_hash(user.password)
        token = info.context["request"].headers["authorization"]
        token_verified = verify_token(token)
        if not token_verified:
            raise HTTPException(status_code=401, detail="Not valid token or token expired")
        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            try:
                with get_database_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO users (username, password, email, name, role_id) VALUES (%s, %s, %s, %s, %s);",
                            (user.username, hashed_password, user.email, user.name, user.role_id))
                        connection.commit()
                        return UserResponse(success=True, message=f"User created")

            except IntegrityError as e:
                if "unique constraint" in str(e):
                    raise HTTPException(status_code=400, detail="Username already exists")
                else:
                    raise HTTPException(status_code=500, detail="Error creating user")


    @strawberry.mutation
    def update_user(self, info: Info, _input: UserUpdateInput) -> UserResponse:
        if _input.password:
            hashed_password = get_password_hash(_input.password)
        else:
            hashed_password = None
        token = info.context["request"].headers["authorization"]
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Not valid token or token expired")
        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not any([_input.username, _input.password, _input.email, _input.name, _input.role_id]):
            raise HTTPException(status_code=400, detail="No data to update")

        try:
            with get_database_connection() as connection, connection.cursor() as cursor:
                update_query = "UPDATE users SET "
                update_params = []

                if _input.username:
                    update_query += "username = %s, "
                    update_params.append(_input.username)
                if _input.password:
                    update_query += "password = %s, "
                    update_params.append(hashed_password)
                if _input.email:
                    update_query += "email = %s, "
                    update_params.append(_input.email)
                if _input.name:
                    update_query += "name = %s, "
                    update_params.append(_input.name)
                if _input.role_id:
                    update_query += "role_id = %s, "
                    update_params.append(_input.role_id)

                update_query = update_query.rstrip(", ")
                update_query += " WHERE user_id = %s;"
                update_params.append(_input.user_id)

                cursor.execute(update_query, tuple(update_params))
                connection.commit()
                return UserResponse(success=True, message=f"User {_input.user_id} updated")
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=500, detail="Error updating user")

    @strawberry.mutation
    def delete_user(self, info: Info, user_id: int) -> UserResponse:
        token = info.context["request"].headers["authorization"]
        token_verified = verify_token(token)
        if not token_verified:
            raise HTTPException(status_code=401, detail="Not valid token or token expired")
        if not is_user_admin(token):
            raise HTTPException(status_code=401, detail="Unauthorized")
        else:
            try:
                with get_database_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
                        connection.commit()
                        if cursor.rowcount == 0:
                            raise HTTPException(status_code=404, detail="User not found")
                        return UserResponse(success=True, message=f"User {user_id} deleted")

            except IntegrityError as e:
                if "unique constraint" in str(e):
                    raise HTTPException(status_code=400, detail="Username already exists")
                else:
                    raise HTTPException(status_code=500, detail="Error deleting user")
