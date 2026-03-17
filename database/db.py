import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=tcp:conference-sql-server.database.windows.net,1433;"
        "Database=conference_db;"
        "Uid=sqladmin;"
        "Pwd=Neekshay642;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return conn