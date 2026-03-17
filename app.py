from flask import Flask, render_template, request, redirect, session, jsonify, send_file


import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

# import all blueprints
from routes.auth_routes import auth
from routes.booking_routes import booking
from routes.admin_routes import admin
from routes.main_routes import main
from routes.update_halls import update_halls_bp

app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(admin)
app.register_blueprint(main)
app.register_blueprint(update_halls_bp)

if __name__ == "__main__":
    app.run(debug=True)

import os

print("CURRENT DIR:", os.getcwd())
print("STATIC EXISTS:", os.path.exists("static"))
print("ROOM EXISTS:", os.path.exists("static/room"))

if os.path.exists("static"):
    print("STATIC CONTENT:", os.listdir("static"))
# Application is created by AADI SAI NEEKSHAY(IT Intern)