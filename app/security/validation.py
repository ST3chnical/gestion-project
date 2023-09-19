import psycopg2
from app.db.config import get_database_connection
from app.models.user import User
from app.security.token import get_id_by_token


def is_user_admin(token: str) -> bool:
    user_id = get_id_by_token(token)
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT role_id FROM users WHERE user_id = %s;", (user_id,))
                user_data = cursor.fetchone()

                if not user_data:
                    return False
                role_id = user_data[0]

                return role_id == 1

    except psycopg2.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return False


def get_user_by_email(email: str) -> User:
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id, username, password, email,"
                               " name, role_id FROM users WHERE email = %s;", (email,))
                user_data = cursor.fetchone()

                if not user_data:
                    raise Exception("User not found")

                user_id, username, password, email, name, role_id = user_data
                return User(
                    user_id=user_id,
                    username=username,
                    password=password,
                    email=email,
                    name=name,
                    role_id=role_id
                )

    except psycopg2.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        raise Exception(e)
