from app.db.config import get_database_connection


def create_roles():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO public.roles (role_id, role, role_description)
        VALUES (1, 'admin', 'Puede crear, modificar y eliminar tanto usuarios como proyectos.')
        ON CONFLICT (role_id) DO NOTHING;
    """)

    cursor.execute("""
            INSERT INTO public.roles (role_id, role, role_description)
            VALUES (2, 'user', 'Puede crear, modificar y eliminar comentarios, ser parte de proyectos y de sus tareas.')
            ON CONFLICT (role_id) DO NOTHING;
        """)

    connection.commit()
    cursor.close()
    connection.close()
