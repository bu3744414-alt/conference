from flask import Blueprint, render_template, request, redirect, session
from database.db import get_connection

auth = Blueprint("auth", __name__)

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
            WHERE CAST(employee_id AS VARCHAR(20))=? OR LOWER(username)=LOWER(?)
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
