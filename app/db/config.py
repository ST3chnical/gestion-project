import psycopg2


def get_database_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5433"
    )


def config_database():
    try:
        from app.db.create_tables import create_tables
        from app.db.config_tables import foreign_keys

        create_tables()
        foreign_keys()
    except ImportError as import_error:
        print(f"Error de importación: {import_error}")
    except Exception as e:
        print(f"Error no especificado: {e}")

