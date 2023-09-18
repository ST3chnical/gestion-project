from app.db.config import get_database_connection


def create_tables():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.users (
            user_id serial,
            username character varying(50) NOT NULL,
            password character varying(100) NOT NULL,
            email character varying(50) NOT NULL,
            name character varying(50) NOT NULL,
            role_id integer NOT NULL,
            CONSTRAINT pk_user PRIMARY KEY (user_id)
        );

        ALTER TABLE IF EXISTS public.users
        OWNER to postgres;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.roles (
            role_id serial,
            role character varying(50) NOT NULL,
            role_description character varying(255) NOT NULL,
            CONSTRAINT pk_role PRIMARY KEY (role_id)
        );

        ALTER TABLE IF EXISTS public.roles
        OWNER to postgres;   
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.projects (
            project_id serial,
            project_name character varying(100) NOT NULL,
            project_description character varying(255) NOT NULL,
            start_date date NOT NULL,
            end_date date,
            responsible_id integer,
            CONSTRAINT pk_project PRIMARY KEY (project_id)
        );

        ALTER TABLE IF EXISTS public.projects
        OWNER to postgres;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.tasks (
            task_id serial,
            task_name character varying(50) NOT NULL,
            task_description character varying(255) NOT NULL,
            deadline date NOT NULL,
            task_status character varying(50) NOT NULL,
            project_id integer NOT NULL,
            responsible_id integer NOT NULL,
            CONSTRAINT pk_task PRIMARY KEY (task_id)
        );

        ALTER TABLE IF EXISTS public.tasks
        OWNER to postgres;
    """)

    cursor.execute("""
         CREATE TABLE IF NOT EXISTS public.comments (
            comment_id serial,
            comment_content character varying(255) NOT NULL,
            creation_date date NOT NULL,
            user_id integer NOT NULL,
            project_id integer NOT NULL,
            CONSTRAINT pk_comment PRIMARY KEY (comment_id)
        );

        ALTER TABLE IF EXISTS public.comments
        OWNER to postgres;
    """)

    connection.commit()
    cursor.close()
    connection.close()
