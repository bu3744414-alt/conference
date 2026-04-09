import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint
email = Blueprint("email", __name__)

#COMMON_EMAIL = "conference.room@vslp.in"

EMAIL = "bu3744414@gmail.com"
PASSWORD = "ufjp buck hipu kpwy"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to_email, subject, body):

    try:
        print("Sending to:", to_email)
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print("Email error:", e)


def build_email_template(action, user, hall, date, start, end, reason=""):

    return f"""
    <h2>Conference Hall Notification</h2>

    <p><b>Action:</b> {action}</p>
    <p><b>User:</b> {user}</p>
    <p><b>Hall:</b> {hall}</p>
    <p><b>Date:</b> {date}</p>
    <p><b>Time:</b> {start} - {end}</p>
    <p><b>Reason:</b> {reason if reason else "N/A"}</p>

    <br>
    <p>This is an automated message from Conference Booking System.</p>
    """