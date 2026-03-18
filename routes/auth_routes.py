from flask import Blueprint, render_template, request, redirect, session
from database.db import get_connection

auth = Blueprint("auth", __name__)

# ---------------- LOGIN code ----------------

@auth.route('/login', methods=['GET','POST'])
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
@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- CHANGE PASSWORD ----------------

@auth.route('/change_password', methods=['POST'])
def change_password():

    empno = request.form.get("empno")

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        return render_template("change_password.html",
                               message="Passwords do not match")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT password
        FROM login_mas
        WHERE employee_id = %s
        AND status_flg = 'A'
    """,(empno,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return render_template("change_password.html",
                               message="Employee not found or inactive")

    db_password = row[0]

    if db_password != old_password:
        conn.close()
        return render_template("change_password.html",
                               message="Old password incorrect")

    cur.execute("""
        UPDATE login_mas
        SET password = %s
        WHERE employee_id = %s
    """,(new_password,empno))

    conn.commit()
    conn.close()

    return render_template("change_password.html",
                           message="Password updated successfully")


@auth.route('/change_password_page')
def change_password_page():
    return render_template("change_password.html")