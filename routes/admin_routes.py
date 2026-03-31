from flask import Blueprint, request, jsonify, session, send_file
from datetime import datetime, date
from database.db import get_connection
import pandas as pd
from utils.email_service import send_email, build_email_template

COMMON_EMAIL = "your_common_email@example.com"

admin = Blueprint("admin", __name__)



@admin.route("/admin_bookings")
def admin_bookings():

    if session.get("role") != "admin":
        return jsonify([])

    selected_date = request.args.get("date")

    if not selected_date:
        selected_date = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
SELECT 
t.booking_id,

m.conference_name AS old_hall,

m2.conference_name AS new_hall,   -- 🔥 NEW

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

CASE 
    WHEN ISNULL(t.reassign_flag,0)=1 THEN 'Reassigned'
    WHEN ISNULL(t.rescheduled,0)=1 THEN 'Rescheduled'
    ELSE t.status
END AS status,

CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.resch_reason 
    ELSE t.purpose 
END AS purpose,

t.admin_remarks,
t.admin_name,                      -- 🔥 NEW
t.reassign_reason,
ISNULL(t.rescheduled,0) AS rescheduled,
ISNULL(t.reassign_flag,0) AS reassign   -- 🔥 NEW

FROM booking_transactions t

JOIN conference_master m
ON t.conference_id = m.conference_id

LEFT JOIN conference_master m2
ON t.re_conference_id = m2.conference_id   -- 🔥 NEW JOIN

JOIN Login_mas l
ON t.empno = l.employee_id

WHERE 
CASE 
    WHEN ISNULL(t.rescheduled,0)=1 THEN t.rescheduled_date 
    ELSE t.trn_date 
END = ?

ORDER BY start_time
""",(selected_date,))
    rows = cursor.fetchall()

    conn.close()

    bookings = []

    for r in rows:
        bookings.append({
        "id": r[0],
        "old_hall": r[1],
        "new_hall": r[2],
        "department": r[3],
        "user_dept": r[4],
        "date": str(r[5]),
        "start": str(r[6])[:5],
        "end": str(r[7])[:5],
        "user": r[8],
        "status": r[9],
        "purpose": r[10],
        "cancel_reason": r[11],
        "admin_name": r[12],
        "reassign_reason": r[13],   # ✅ ADD THIS
        "rescheduled": r[14],
        "reassign": r[15]
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

    # 🔥 GET BOOKING DETAILS
    cursor.execute("""
    SELECT 
        m.conference_name,
        t.trn_date,
        t.start_time,
        t.end_time,
        t.empno
    FROM booking_transactions t
    JOIN conference_master m ON t.conference_id = m.conference_id
    WHERE t.booking_id=?
    """, (booking_id,))

    row = cursor.fetchone()

    hall = row[0]
    date = row[1]
    start = str(row[2])[:5]
    end = str(row[3])[:5]
    empno = row[4]

    # 🔥 GET USER EMAIL
    cursor.execute("SELECT email FROM login_mas WHERE employee_id=?", (empno,))
    email_row = cursor.fetchone()
    user_email = email_row[0] if email_row and email_row[0] else None

    # 🔥 UPDATE STATUS
    cursor.execute("""
        UPDATE booking_transactions
        SET
            status='Cancelled',
            admin_id=?,
            admin_name=?,
            admin_status='Cancelled',
            admin_remarks=?
        WHERE booking_id=?
    """,(
        session['empno'],
        session['user'],
        reason,
        booking_id
    ))

    conn.commit()
    conn.close()

    # 🔥 SEND EMAIL
    body = build_email_template(
        "Booking Cancelled",
        session['user'],
        hall,
        date,
        start,
        end,
        reason   # ✅ FIXED
    )

    
    # 🔥 SEND EMAIL TO BOTH

    # send to user
    if user_email:
        send_email(user_email, "Booking Cancelled", body)

    # send to common mail
    send_email(COMMON_EMAIL, "Booking Cancelled", body)

    return jsonify(status="success", message="Booking cancelled successfully")

# ---------------- MY BOOKINGS ----------------
#------Add new hall--------
'''@admin.route("/add_hall", methods=["POST"])
def add_hall():
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO conference_master (conference_id, conference_name, status)
        VALUES (?, ?, 'A')
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
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE conference_master
        SET status='I'
        WHERE conference_id=?
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
    WHERE trn_date BETWEEN ? AND ?
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

