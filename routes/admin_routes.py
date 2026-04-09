from flask import Blueprint, request, jsonify, session, send_file
from datetime import datetime, date
from database.db import get_connection
import pandas as pd
from utils.email_service import send_email, build_email_template

COMMON_EMAIL = "conference.room@vslp.in"

admin = Blueprint("admin", __name__)


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

    recipients = []

    if user_email:
        recipients.append(user_email)

    recipients.append(COMMON_EMAIL)

    send_email(recipients, "Booking Cancelled", body)

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

