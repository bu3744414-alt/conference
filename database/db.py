import pymssql
import os
from dotenv import load_dotenv

load_dotenv()  # 👈 load .env file

def get_connection():
    server = os.getenv("DB_SERVER", "conference-sql-server.database.windows.net")
    database = os.getenv("DB_NAME", "conference_db")
    user = os.getenv("DB_USER", "sqladmin")
    password = os.getenv("DB_PASSWORD")

    if not password:
        raise Exception("DB_PASSWORD not set in Azure App Settings")

    conn = pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        port=1433
    )

    return conn