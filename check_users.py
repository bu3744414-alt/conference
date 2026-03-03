import sqlite3

conn = sqlite3.connect("booking.db")
rows = conn.execute("SELECT * FROM users").fetchall()
print(rows)
