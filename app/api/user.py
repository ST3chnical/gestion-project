import strawberry
import typing
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from fastapi import HTTPException
from app.db.config import get_database_connection
from app.models.user import User
from app.utils.user_utils import User, UserResponse, UserInput, UserInputCreate
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

                    user_dict = dict(zip(["user_id", "username", "password", "email", "name", "rol_id"], user_data))
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
                        user_id, username, email, password, name, rol_id = user_data
                        user = User(user_id=user_id, username=username, password=password, email=email, name=name,
                                    rol_id=rol_id)
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
                            (user.username, hashed_password, user.email, user.name, user.rol_id))
                        connection.commit()
                        user_id = cursor.lastrowid
                        return UserResponse(success=True, message=f"User {user_id} created")

            except IntegrityError as e:
                if "unique constraint" in str(e):
                    raise HTTPException(status_code=400, detail="Username already exists")
                else:
                    raise HTTPException(status_code=500, detail="Error creating user")

    @strawberry.mutation
    def update_user(self, info: Info, user: UserInput) -> UserResponse:
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
                            "UPDATE users SET username = %s,"
                            " password = %s, email = %s, name = %s, role_id = %s WHERE user_id = %s;",
                            (user.username, hashed_password, user.email, user.name, user.rol_id, user.user_id))
                        connection.commit()
                        if cursor.rowcount == 0:
                            raise HTTPException(status_code=404, detail="User not found")
                        return UserResponse(success=True, message=f"User {user.user_id} updated")

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
