from pathlib import Path

from app.database.connection import get_connection


SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def initialize_database():

    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema = schema_file.read()

    connection = get_connection()

    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")