import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=192.168.128.12;"      # change if main server is different
        "DATABASE=Conference;"
        "UID=confuser;"          # 🔑 add SQL username
        "PWD=conf#123;"          # 🔑 add SQL password
    )
    return conn