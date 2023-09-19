from app.db.config import get_database_connection


def check_constraint(cursor, constraint_name):
    cursor.execute("""
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = %s
    """, (constraint_name,))
    return not cursor.fetchone()


def add_foreign_key(cursor, constraint_name, table_name, column_name, reference_table, reference_column):
    if check_constraint(cursor, constraint_name):
        cursor.execute(f"""
            ALTER TABLE IF EXISTS public.{table_name}
            ADD CONSTRAINT {constraint_name} FOREIGN KEY ({column_name})
            REFERENCES public.{reference_table} ({reference_column}) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)


def foreign_keys():
    connection = get_database_connection()
    cursor = connection.cursor()

    add_foreign_key(cursor, 'fk_user_role', 'users', 'role_id', 'roles', 'role_id')
    add_foreign_key(cursor, 'fk_responsible_user', 'projects', 'responsible_id', 'users', 'user_id')
    add_foreign_key(cursor, 'fk_project_task', 'tasks', 'project_id', 'projects', 'project_id')
    add_foreign_key(cursor, 'fk_responsible_task', 'tasks', 'responsible_id', 'users', 'user_id')
    add_foreign_key(cursor, 'fk_user_comment', 'comments', 'user_id', 'users', 'user_id')
    add_foreign_key(cursor, 'fk_project_comment', 'comments', 'project_id', 'projects', 'project_id')

    connection.commit()
    cursor.close()
    connection.close()
