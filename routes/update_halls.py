from flask import Blueprint, request, jsonify, session
from database.db import get_connection

update_halls_bp = Blueprint("update_halls_bp", __name__)

@update_halls_bp.route('/update_halls', methods=['POST'])
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