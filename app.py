from flask import Flask, render_template, request, redirect, session, jsonify, send_file

from datetime import datetime, date
import pandas as pd
import psycopg2
import os
app = Flask(__name__)
app.secret_key = "secret123"




# ---------------- DATABASE INIT ----------------
# ---------------- SQL CONNECTIONS ----------------
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn



# ---------------- GET HALLS ----------------


# ---------------- LOGIN code ----------------

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        login_input = request.form.get('employee_id','').strip()
        password = request.form.get('password','')

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT employee_id, username, department, role, status_flg, password
            FROM Login_mas
            WHERE CAST(employee_id AS VARCHAR(20))=%s OR LOWER(username)=LOWER(%s)
        """,(login_input, login_input))

        user = new_func(cursor)

        cursor.close()
        conn.close()

        if not user:
            return render_template("login.html", error="Invalid Employee ID")

        if user[5] != password:
            return render_template("login.html", error="Invalid Password")

        if user[4] != 'A':
            return render_template("login.html",error="User account inactive")

                                  

        session['empno'] = user[0]
        session['user'] = user[1]
        session['dept'] = user[2]
        session['role'] = user[3]

        return redirect('/')

    return render_template("login.html")

def new_func(cursor):
    user = cursor.fetchone()
    return user



# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- LOGIN ----------------
@app.route('/')
def home():

    if not session.get('user'):
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT empname, conference_id, department, trn_date,
        start_time, end_time, status, purpose
    FROM booking_transactions
    ORDER BY trn_date, start_time
    """)

    bookings = cursor.fetchall()

    conn.close()

    halls = get_halls()

    return render_template(
        "index.html",
        bookings=bookings,
        total_halls=len(halls),
        booked_count=len(bookings),
        halls=halls,
        user=session['user'],
        role=session['role'],
        dept=session['dept'],
        today=str(date.today())
    )


# ---------------- AVAILABILITY ----------------
@app.route('/availability')
def availability():
    hall = request.args.get('hall')
    date_val = request.args.get('date')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT start_time, end_time, department, empname
        FROM booking_transactions
        WHERE conference_id=%s AND trn_date=%s
    """,(hall,date_val))
    rows = cursor.fetchall()
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
@app.route('/book', methods=['POST'])
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
        WHERE conference_id=%s AND trn_date=%s
        AND (%s < end_time AND %s > start_time)
    """, (hall, meeting_date, start, end))

    # office hours validation
    if end <= start:
        conn.close()
        return jsonify(status="error",
                       message="End time must be after start time")

    if start < "09:00" or end > "18:00":
        conn.close()
        return jsonify(status="error",
                       message="Booking allowed only between 9 AM and 6 PM")

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
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
@app.route("/hall_stats")
def hall_stats():

    conn = get_connection()
    cursor = conn.cursor()
    halls = [row[0] for row in cursor.execute("""
        SELECT conference_id
        FROM conference_master
        WHERE status='A'
    """)]
    halls = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("""
    SELECT conference_id, COUNT(*)
    FROM booking_transactions
    GROUP BY conference_id
    """)

    counts = dict(cursor.fetchall())

    conn.close()

    data = {hall: counts.get(hall, 0) for hall in halls}
    return jsonify(data)
    

# ---------------- ADMIN CANCEL ----------------
@app.route('/cancel/<int:booking_id>', methods=['POST'])
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
#---------AdminBookings--------
@app.route("/admin_bookings")
def admin_bookings():
    if session.get("role") != "admin":
        return jsonify([])

    today = date.today().isoformat()   # ✅ ensures YYYY-MM-DD

    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT booking_id, conference_id, department, trn_date,
            start_time, end_time, empname, status
        FROM booking_transactions
        WHERE trn_date=%s
    """, (today,))
    rows = cursor.fetchall()

    conn.close()

    return jsonify([
        {
            "id": r[0],
            "hall": r[1],
            "department": r[2],
            "date": r[3],
            "start": r[4],
            "end": r[5],
            "user": r[6],
            "status": r[7]
        } for r in rows
    ])


# ---------------- RESCHEDULE ----------------
@app.route('/reschedule/<int:booking_id>', methods=['POST'])
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

    if new_start < "09:00" or new_end > "18:00":
        conn.close()
        return jsonify(status="error",
        message="Booking allowed only between 9 AM and 6 PM")

    cursor.execute("""
        UPDATE booking_transactions
        SET
        rescheduled_date=%s,
        re_start_time=%s,
        re_end_time=%s,
        resch_reason=%s,
        rescheduled=1
        WHERE booking_id=%s
    """,(new_date,new_start,new_end,reason,booking_id))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Booking rescheduled successfully")
# ---------------- ADMIN SETTINGS ----------------
@app.route('/update_halls', methods=['POST'])
def update_halls():

    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    conn = get_connection()
    cursor = conn.cursor()

    # clear existing halls
    cursor.execute("UPDATE conference_master SET status='I'")

    # insert new halls
    for name in request.form.values():
        cursor.execute("""
            INSERT INTO conference_master (conference_id, conference_name, status)
            VALUES (%s, %s, 'A')
        """, (name, name))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall names updated")


# ---------------- EXPORT BOOKINGS ----------------
@app.route("/export_excel", methods=["POST"])
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
    )


# ---------------- MY BOOKINGS ----------------
@app.route("/my_bookings")
def my_bookings():

    if not session.get("user"):
        return jsonify([])

    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT booking_id,
               conference_id,
               trn_date,
               start_time,
               end_time,
               status,
               COALESCE(rescheduled,0)
        FROM booking_transactions
        WHERE empno=%s
        ORDER BY trn_date, start_time
    """,(session["empno"],))
    rows = cursor.fetchall()

    conn.close()

    bookings = []

    for r in rows:
        bookings.append({
            "id" : r[0],
            "hall": r[1],
            "date": str(r[2]),
            "start": str(r[3])[:5],
            "end": str(r[4])[:5],
            "status": r[5],
            "rescheduled": r[6]
        })

    return jsonify(bookings)


#------Add new hall--------
@app.route("/add_hall", methods=["POST"])
def add_hall():
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO conference_master (conference_id, conference_name, status)
        VALUES (%s, %s, 'A')
    """,(name, name))
    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall added")
#-----delete hall--------
@app.route("/delete_hall", methods=["POST"])
def delete_hall():

    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE conference_master
        SET status='I'
        WHERE conference_id=%s
    """,(name,))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall deleted")
#---hall floor grouping 
def get_halls():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT conference_id, conference_name
        FROM conference_master
        WHERE status='A'
    """)
    halls = [row[0] for row in cursor.fetchall()]

    conn.close()
    return halls
#---usage analytics per hall---


if __name__ == "__main__":
    app.run()