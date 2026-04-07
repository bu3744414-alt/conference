import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=192.168.128.12;"
        "DATABASE=Conference;"
        "UID=your_username;"
        "PWD=your_password;"
    )
    return conn