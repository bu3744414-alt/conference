import pymssql
import os

def get_connection():
    password = os.environ.get("DB_PASSWORD")

    if not password:
        raise Exception("DB_PASSWORD not set")

    conn = pymssql.connect(
        server="conference-sql-server.database.windows.net",
        user="sqladmin",
        password=password,
        database="conference_db"
    )

    return conn