import pyodbc
import os

def get_connection():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=conference-sql-server.database.windows.net;"
        "Database=conference_db;"
        "UID=sqladmin;"
        "PWD=" + os.environ.get("Neekshay642") + ";"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return conn