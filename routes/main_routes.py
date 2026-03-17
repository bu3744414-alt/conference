from flask import Blueprint, render_template, redirect, session
from datetime import date
from database.db import get_connection
from services.master_service import get_halls, get_departments

main = Blueprint("main", __name__)


@main.route('/')
def home():

    if not session.get('user'):
        return redirect('/login')

    conn = get_connection()

    bookings = conn.execute("""
        SELECT empname, conference_id, department, trn_date,
               start_time, end_time, status, purpose
        FROM booking_transactions
        ORDER BY trn_date, start_time
    """).fetchall()

    conn.close()

    halls = get_halls()
    departments=get_departments()
    

    return render_template(
        "index.html",
        bookings=bookings,
        total_halls=len(halls),
        booked_count=len(bookings),
        halls=halls,
        departments=departments,
        user=session['user'],
        role=session['role'],
        dept=session['dept'],
        today=str(date.today())
    )


