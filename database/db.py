import pyodbc
# ---------------- DATABASE INIT ----------------
# ---------------- SQL CONNECTIONS ----------------
def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=INHYD-L-5004;"
        "DATABASE=Conference;"
        "Trusted_Connection=yes;"
    )
    return conn