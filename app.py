from flask import Flask, render_template, request, redirect, session, jsonify, send_file

from datetime import datetime, date
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(admin)
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)