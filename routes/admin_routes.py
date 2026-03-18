from flask import Blueprint, request, jsonify, session, send_file
from datetime import datetime, date
from database.db import get_connection
import pandas as pd
admin = Blueprint("admin", __name__)



@admin.route("/admin_bookings")
def admin_bookings():

    if session.get("role") != "admin":
        return jsonify([])

    selected_date = request.args.get("date")

    if not selected_date:
        selected_date = date.today().isoformat()

    conn = get_connection()

    rows = conn.execute("""
SELECT 
t.booking_id,
m.conference_name,
t.department,
l.department AS user_department,

CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.rescheduled_date 
    ELSE t.trn_date 
END AS trn_date,

CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.re_start_time 
    ELSE t.start_time 
END AS start_time,

CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.re_end_time 
    ELSE t.end_time 
END AS end_time,

t.empname,
t.status,

CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.resch_reason 
    ELSE t.purpose 
END AS purpose,

t.admin_remarks,

ISNULL(t.rescheduled,0) AS rescheduled   

FROM booking_transactions t

JOIN conference_master m
ON t.conference_id = m.conference_id

JOIN Login_mas l
ON t.empno = l.employee_id

WHERE 
CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.rescheduled_date 
    ELSE t.trn_date 
END = %s

ORDER BY start_time
""",(selected_date,)).fetchall()

    conn.close()

    bookings = []

    for r in rows:
        bookings.append({
            "id": r[0],
            "hall": r[1],
            "department": r[2],
            "user_dept": r[3],
            "date": str(r[4]),
            "start": str(r[5])[:5],
            "end": str(r[6])[:5],
            "user": r[7],
            "status": r[8],
            "purpose": r[9],
            "cancel_reason": r[10],
            "rescheduled": r[11]
        })

    return jsonify(bookings)

# ---------------- ADMIN CANCEL ----------------
@admin.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel(booking_id):

    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    reason = request.form.get("reason")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE booking_transactions
        SET
            status='Cancelled',
            admin_id=%s,
            admin_name=%s,
            admin_status='Cancelled',
            admin_remarks=%s
        WHERE booking_id=%s
    """,(
        session['empno'],   # admin id
        session['user'],    # admin name
        reason,
        booking_id
    ))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Booking cancelled successfully")

# ---------------- MY BOOKINGS ----------------
#------Add new hall--------
'''@admin.route("/add_hall", methods=["POST"])
def add_hall():
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = get_connection()
    conn.execute("""INSERT INTO conference_master (conference_id, conference_name, status)
        VALUES (%s, %s, 'A')
    """,(name, name))
    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall added")

#-----delete hall--------
@admin.route("/delete_hall", methods=["POST"])
def delete_hall():

    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = get_connection()

    conn.execute("""
        UPDATE conference_master
        SET status='I'
        WHERE conference_id=%s
    """,(name,))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall deleted")

# ---------------- EXPORT BOOKINGS ----------------
@admin.route("/export_excel", methods=["POST"])
def export_excel():

    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    conn = get_connection()

    query = """
    SELECT
        empno,
        empname,
        conference_id,
        department,
        trn_date,
        start_time,
        end_time,
        booked_on,
        self_remarks,
        status,
        rescheduled
    FROM booking_transactions
    WHERE trn_date BETWEEN %s AND %s
    ORDER BY trn_date, start_time
    """

    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()

    file = "bookings_export.xlsx"
    df.to_excel(file, index=False, engine="openpyxl")

    return send_file(
        file,
        as_attachment=True,
        download_name="bookings.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )'''
#---hall floor grouping 

