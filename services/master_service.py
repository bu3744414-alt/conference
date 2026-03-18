from database.db import get_connection


def get_halls():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT conference_id, conference_name
        FROM conference_master
        WHERE status='A'
        ORDER BY conference_id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# --- GET ACTIVE DEPARTMENTS ---
def get_departments():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT department
        FROM Login_mas
        WHERE status_flg='A'
        ORDER BY department
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [r[0] for r in rows]