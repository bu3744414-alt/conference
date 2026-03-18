import sqlite3

conn = sqlite3.connect("booking.db")
cursor = conn.cursor()
rows = cursor.execute("SELECT * FROM users").fetchall()
print(rows)
