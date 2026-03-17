from flask import Blueprint, request, jsonify, session, render_template, redirect
from database.db import get_connection
from datetime import datetime, date
booking = Blueprint("booking", __name__)



# ---------------- AVAILABILITY ----------------
@booking.route('/availability')
def availability():
    hall = request.args.get('hall')
    date_val = request.args.get('date')

    conn = get_connection()

    rows = conn.execute("""
        SELECT
        CASE WHEN rescheduled = 1 THEN re_start_time ELSE start_time END,
        CASE WHEN rescheduled = 1 THEN re_end_time ELSE end_time END,
        department,
        empname
        FROM booking_transactions
        WHERE conference_id=? 
        AND (CASE WHEN rescheduled = 1 THEN rescheduled_date ELSE trn_date END)=?
        AND status='Booked'
    """,(hall,date_val)).fetchall()

    conn.close()

    data = []

    for r in rows:
        start = datetime.strptime(str(r[0])[:8], "%H:%M:%S").strftime("%I:%M %p")
        end = datetime.strptime(str(r[1])[:8], "%H:%M:%S").strftime("%I:%M %p")

        data.append([
            start,
            end,
            r[2],
            r[3]
        ])

    return jsonify(data)


#--------Checking-------------

# ---------------- BOOK ----------------
@booking.route('/book', methods=['POST'])
def book():
    if not session.get('user'):
        return jsonify(status="error", message="Login expired")

    hall = request.form['hall']
    meeting_date = request.form['date']
    start = request.form['start_time']
    end = request.form['end_time']
    department = request.form.get('department')

    # If admin selects department use it
    if session.get('role') == 'admin' and department:
        dept_to_book = department
    else:
        dept_to_book = session['dept']

    purpose = request.form.get('purpose')

    conn = get_connection()
    cursor = conn.cursor()

    # 🔍 Check for time conflict
    cursor.execute("""
    SELECT start_time, end_time, department, empname
    FROM booking_transactions
    WHERE conference_id=? 
    AND trn_date=?
    AND status='Booked'
    AND (? < end_time AND ? > start_time)
    """,(hall, meeting_date, start, end))

    # office hours validation
    if end <= start:
        conn.close()
        return jsonify(status="error",
                       message="End time must be after start time")

    if start < "09:00" or end > "20:00":
        conn.close()
        return jsonify(status="error",
                       message="Booking allowed only between 9 AM and 8 PM")

    conflict = cursor.fetchone()

    if conflict:
        s, e, d, u = conflict

        s = datetime.strptime(str(s)[:8], "%H:%M:%S").strftime("%I:%M %p")
        e = datetime.strptime(str(e)[:8], "%H:%M:%S").strftime("%I:%M %p")

        conn.close()
        return jsonify(
            status="error",
            message=f"Hall already booked by {d} ({u}) from {s} to {e}"
        )

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ✅ Insert booking
    cursor.execute("""
    INSERT INTO booking_transactions
    (empno, empname, conference_id, department, trn_date,
    start_time, end_time, booked_on, purpose, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,(
    session['empno'],
    session['user'],
    hall,
    dept_to_book,
    meeting_date,
    start,
    end,
    now,
    purpose,
    "Booked"
))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Booking successful")



#-------HALL STATS

@booking.route("/hall_stats")
def hall_stats():

    conn = get_connection()

    halls = [row[0] for row in conn.execute("""
        SELECT conference_id
        FROM conference_master
        WHERE status='A'
    """)]

    counts = dict(conn.execute("""
        SELECT conference_id, COUNT(*)
        FROM booking_transactions
        GROUP BY conference_id
    """).fetchall())

    conn.close()

    data = {hall: counts.get(hall, 0) for hall in halls}
    return jsonify(data)



@booking.route('/reschedule/<int:booking_id>', methods=['POST'])
def reschedule(booking_id):

    if not session.get('user'):
        return jsonify(status="error", message="Login expired")

    new_date = request.form['date']
    new_start = request.form['start_time']
    new_end = request.form['end_time']
    reason = request.form.get('reason')

    conn = get_connection()
    cursor = conn.cursor()

    if new_end <= new_start:
        conn.close()
        return jsonify(status="error", message="End time must be after start time")

    if new_start < "09:00" or new_end > "20:00":
        conn.close()
        return jsonify(status="error",
        message="Booking allowed only between 9 AM and 8 PM")

    cursor.execute("""
        UPDATE booking_transactions
        SET
        rescheduled_date=?,
        re_start_time=?,
        re_end_time=?,
        resch_reason=?,
        rescheduled=1
        WHERE booking_id=?
    """,(new_date,new_start,new_end,reason,booking_id))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Booking rescheduled successfully")


@booking.route("/my_bookings")
def my_bookings():

    if not session.get("user"):
        return jsonify([])

    selected_date = request.args.get("date")

    conn = get_connection()

    if selected_date:
        rows = conn.execute("""
        SELECT 
            booking_id,
            conference_id,

            CASE 
                WHEN ISNULL(rescheduled,0)=1 THEN rescheduled_date
                ELSE trn_date
            END AS trn_date,

            CASE 
                WHEN ISNULL(rescheduled,0)=1 THEN re_start_time
                ELSE start_time
            END AS start_time,

            CASE 
                WHEN ISNULL(rescheduled,0)=1 THEN re_end_time
                ELSE end_time
            END AS end_time,

            status,

            CASE
                WHEN ISNULL(rescheduled,0)=1 THEN resch_reason
                ELSE purpose
            END AS purpose,

            admin_remarks,
            ISNULL(rescheduled,0)

        FROM booking_transactions
        WHERE (empno=? OR empname=?)
        AND CAST(
            CASE 
                WHEN ISNULL(rescheduled,0)=1 THEN rescheduled_date
                ELSE trn_date
            END AS DATE
        ) = ?

        ORDER BY start_time
    """,(session["empno"], session["user"], selected_date)).fetchall()

    else:
        rows = conn.execute("""
            SELECT 
                booking_id,
                conference_id,

                CASE 
                    WHEN ISNULL(rescheduled,0)=1 THEN rescheduled_date
                    ELSE trn_date
                END AS trn_date,

                CASE 
                    WHEN ISNULL(rescheduled,0)=1 THEN re_start_time
                    ELSE start_time
                END AS start_time,

                CASE 
                    WHEN ISNULL(rescheduled,0)=1 THEN re_end_time
                    ELSE end_time
                END AS end_time,

                status,

                CASE
                    WHEN ISNULL(rescheduled,0)=1 THEN resch_reason
                    ELSE purpose
                END AS purpose,
                admin_remarks,
                ISNULL(rescheduled,0)

            FROM booking_transactions
            WHERE (empno=? OR empname=?)
            ORDER BY trn_date, start_time
        """,(session["empno"],session["user"])).fetchall()

    

    conn.close()
    
    bookings = []

    for r in rows:
        bookings.append({
            "id": r[0],
            "hall": r[1],
            "date": str(r[2]),
            "start": str(r[3])[:5],
            "end": str(r[4])[:5],
            "status": r[5],
            "purpose": r[6],
            "cancel_reason": r[7],
            "rescheduled": r[8]
        })

    return jsonify(bookings)


@booking.route('/monthly_bookings')
def monthly_bookings():

    if not session.get('user'):
        return jsonify([])

    month = request.args.get("month")   # example: 2026-03

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        bt.TRN_DATE,
        cm.conference_name,
        bt.start_time,
        bt.end_time,
        bt.purpose,
        bt.status
    FROM booking_transactions bt
    JOIN conference_master cm 
        ON bt.conference_id = cm.conference_id
    WHERE bt.empno = ?
        AND bt.TRN_DATE LIKE ?
    ORDER BY 
        bt.TRN_DATE ASC,
        bt.conference_id ASC,
        bt.start_time ASC
    """, (session['empno'], month + "%"))

    rows = cur.fetchall()

    conn.close()

    data = []

    for r in rows:
        data.append({
            "trn_date": str(r[0]),
            "hall": r[1],
            "start_time": str(r[2]),
            "end_time": str(r[3]),
            "purpose": r[4],
            "status": r[5]
        })

    return jsonify(data)
