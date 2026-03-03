from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import sqlite3
from datetime import datetime, date
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

DB = "booking.db"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hall TEXT,
    department TEXT,
    date TEXT,
    start_time TEXT,
    end_time TEXT,
    booked_by TEXT,
    booked_on TEXT,
    remarks TEXT,
    status TEXT DEFAULT 'Pending',
    active INTEGER DEFAULT 1,
    cancel_reason TEXT,
    rescheduled INTEGER DEFAULT 0
)
""")

    # ⭐ USERS TABLE (for employee login)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE,
        username TEXT,
        department TEXT,
        password TEXT,
        role TEXT
    )
    """)

    # ⭐ halls table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS halls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    # insert default halls
    if conn.execute("SELECT COUNT(*) FROM halls").fetchone()[0] == 0:
        default = [
            "Big_conference-hall-1",
            "Small_conference-hall-1",
            "conference-hall-2nd",
            "conference-hall-3rd",
            "conference-hall-4th"
        ]
        for h in default:
            conn.execute("INSERT INTO halls(name) VALUES(?)",(h,))

    conn.commit()
    conn.close()


# ---------------- GET HALLS ----------------
def get_halls():
    conn = sqlite3.connect(DB)
    halls = [row[0] for row in conn.execute("SELECT name FROM halls")]
    conn.close()
    return halls


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('employee_id','').strip().lower()
        password = request.form.get('password','')

        conn = sqlite3.connect(DB)

        user = conn.execute("""
            SELECT username, department, role
            FROM users
            WHERE (LOWER(employee_id)=? OR LOWER(username)=?)
            AND password=?
        """, (login_id, login_id, password)).fetchone()

        conn.close()

        if user:
            session['user'] = user[0]
            session['dept'] = user[1]
            session['role'] = user[2]
            return redirect('/')
        else:
            return render_template("login.html", error="Invalid credentials")
            print(login_id)
            print(user)
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- HOME ----------------
@app.route('/')
def home():
    if not session.get('user'):
        return redirect('/login')

    conn = sqlite3.connect(DB)

    bookings = conn.execute("""
        SELECT id, hall, department, date, start_time, end_time,
               booked_by, status, remarks
        FROM bookings
        WHERE active=1
        ORDER BY date, start_time
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        bookings=bookings,
        total_halls=len(get_halls()),
        booked_count=len(bookings),
        halls=get_halls(),
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

    conn = sqlite3.connect(DB)
    bookings = conn.execute("""
        SELECT start_time, end_time, department, booked_by
        FROM bookings
        WHERE hall=? AND date=? AND active=1
    """,(hall,date_val)).fetchall()
    conn.close()

    return jsonify(bookings)


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
    remarks = request.form.get('remarks') or ""

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT start_time,end_time,department,booked_by
        FROM bookings
        WHERE hall=? AND date=? AND active=1
        AND (? < end_time AND ? > start_time)
    """,(hall,meeting_date,start,end))

    conflict = cur.fetchone()
    if conflict:
        s,e,d,u = conflict
        conn.close()
        return jsonify(status="error",
                       message=f"Hall booked by {d} ({u}) {s}-{e}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute("""
        INSERT INTO bookings
        (hall, department, date, start_time, end_time,
         booked_by, booked_on, remarks,status)
        VALUES (?,?,?,?,?,?,?,?)
    """,(hall,session['dept'],meeting_date,start,end,
         session['user'],now,remarks,"Booked"))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Booking successful")

@app.route("/hall_stats")
def hall_stats():
    conn = sqlite3.connect(DB)

    # get all halls
    halls = [row[0] for row in conn.execute("SELECT name FROM halls")]

    # get booking counts
    counts = dict(conn.execute("""
        SELECT hall, COUNT(*)
        FROM bookings
        WHERE active=1
        GROUP BY hall
    """).fetchall())

    conn.close()

    # include halls with zero bookings
    data = {hall: counts.get(hall, 0) for hall in halls}

    return jsonify(data)

# ---------------- ADMIN CANCEL ----------------
@app.route('/cancel/<int:id>', methods=['POST'])
def cancel(id):
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    reason = request.form.get('reason')
    if not reason:
        return jsonify(status="error", message="Reason required")

    conn = sqlite3.connect(DB)
    conn.execute("""
        UPDATE bookings
        SET active=0, cancel_reason=?
        WHERE id=?
    """,(reason,id))
    conn.commit()
    conn.close()

    return jsonify(status="success", message="Booking cancelled")


# ---------------- RESCHEDULE ----------------
@app.route('/reschedule/<int:id>', methods=['POST'])
def reschedule(id):
    if not session.get('user'):
        return jsonify(status="error", message="Login expired")

    conn = sqlite3.connect(DB)

    booking = conn.execute("""
        SELECT hall, booked_by, date
        FROM bookings
        WHERE id=? AND active=1
    """,(id,)).fetchone()

    if not booking:
        conn.close()
        return jsonify(status="error", message="Booking not found")

    if booking[2] < str(date.today()):
        conn.close()
        return jsonify(status="error", message="Past booking")

    if booking[1] != session['user']:
        conn.close()
        return jsonify(status="error", message="Unauthorized")

    new_date=request.form['date']
    new_start=request.form['start_time']
    new_end=request.form['end_time']

    conflict = conn.execute("""
        SELECT start_time,end_time,department,booked_by
        FROM bookings
        WHERE hall=? AND date=? AND active=1
        AND (? < end_time AND ? > start_time)
    """,(booking[0],new_date,new_start,new_end)).fetchone()

    if conflict:
        s,e,d,u=conflict
        conn.close()
        return jsonify(status="error",
                       message=f"Slot taken by {d} ({u}) {s}-{e}")

    conn.execute("""
        UPDATE bookings
        SET date=?, start_time=?, end_time=?, status='Booked', rescheduled=1
        WHERE id=?
    """,(new_date,new_start,new_end,id))

    conn.commit()
    conn.close()

    return jsonify(status="success", message="Rescheduled successfully")


# ---------------- ADMIN SETTINGS ----------------
@app.route('/update_halls', methods=['POST'])
def update_halls():
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM halls")

    for name in request.form.values():
        conn.execute("INSERT INTO halls(name) VALUES(?)",(name,))

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

    conn = sqlite3.connect(DB)

    query = """
    SELECT
        id,
        hall,
        department,
        date,
        start_time,
        end_time,
        booked_by,
        booked_on,
        remarks,
        status,
        rescheduled,
        cancel_reason
    FROM bookings
    WHERE date BETWEEN ? AND ?
    ORDER BY date, start_time
    """

    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()

    file = "bookings_export.xlsx"
    df.to_excel(file, index=False, engine="openpyxl")

    return send_file(file,
                     as_attachment=True,
                     download_name="bookings.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ---------------- MY BOOKINGS ----------------
@app.route("/my_bookings")
def my_bookings():

    if not session.get("user"):
        return jsonify([])

    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT id, hall, date, start_time, end_time, status, rescheduled
        FROM bookings
        WHERE booked_by=? AND active=1
        ORDER BY date, start_time
    """, (session["user"],)).fetchall()

    conn.close()

    bookings = []
    for r in rows:
        bookings.append({
            "id": r[0],
            "hall": r[1],
            "date": r[2],
            "start": r[3],
            "end": r[4],
            "status": r[5],
            "rescheduled": r[6],
            "is_admin": session.get("role") == "admin"
        })

    return jsonify(bookings)


#------Add new hall--------
@app.route("/add_hall", methods=["POST"])
def add_hall():
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO halls(name) VALUES(?)",(name,))
    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall added")
#-----delete hall--------
@app.route("/delete_hall", methods=["POST"])
def delete_hall():
    if session.get('role') != 'admin':
        return jsonify(status="error", message="Unauthorized")

    name = request.form.get("name")

    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM halls WHERE name=?",(name,))
    conn.commit()
    conn.close()

    return jsonify(status="success", message="Hall deleted")
#---hall floor grouping 
def group_halls():
    halls = get_halls()
    grouped = {}

    for h in halls:
        parts = h.split("-")

        if len(parts) >= 4:
            floor = parts[2]   # 1st, 2nd, 3rd etc
        else:
            floor = "Other"

        grouped.setdefault(floor, []).append(h)

    return grouped
#---usage analytics per hall---


if __name__ == "__main__":
    init_db()
    app.run(debug=True)