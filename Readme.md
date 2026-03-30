# 🏢 Conference Hall Booking System

A web-based application that allows users to **book, reschedule, cancel, and reassign conference halls** efficiently. The system ensures **real-time availability, conflict management, and admin control**.

---

# 🚀 Features

## 👤 User Features

* Book conference halls
* View personal bookings (My Bookings)
* Check real-time availability
* Reschedule bookings
* Cancel bookings with reason
* Monthly booking history

## 🛠️ Admin Features

* View all department bookings
* Reassign halls
* Cancel bookings
* Book on behalf of departments
* Export booking reports
* Manage halls

---

# 🧱 Tech Stack

| Layer         | Technology            |
| ------------- | --------------------- |
| Frontend      | HTML, CSS, JavaScript |
| Backend       | Python (Flask)        |
| Database      | SQL Server            |
| Communication | REST APIs (JSON)      |

---

# 📁 Project Structure

```
conference/
│
├── app.py
├── database/
│   └── db.py
├── routes/
│   └── booking_routes.py
├── static/
│   ├── css/
│   ├── js/
│   └── room/
├── templates/
│   └── dashboard.html
└── README.md
```

---

# 🔄 System Workflow

1. User interacts with UI (HTML + JS)
2. JavaScript sends API request to Flask
3. Flask processes logic
4. SQL queries run on database
5. Response returned as JSON
6. UI updates dynamically

---

# ⚙️ Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd conference
```

## 2. Install Dependencies

```bash
pip install flask pyodbc
```

## 3. Configure Database

* Update `database/db.py` with your SQL Server credentials

## 4. Run Application

```bash
python app.py
```

## 5. Open Browser

```
http://127.0.0.1:5000
```

---

# 🗄️ Database Tables

## booking_transactions

* booking_id
* empno
* empname
* conference_id
* re_conference_id
* trn_date
* start_time
* end_time
* purpose
* status
* reassign_flag
* reassign_reason
* rescheduled
* rescheduled_date

## conference_master

* conference_id
* conference_name

## login_mas

* employee_id
* department

---

# ⚠️ Important Logic

## 🔁 Reassignment Logic

* Old hall becomes **available**
* New hall becomes **booked**
* Controlled using:

```sql
reassign_flag
re_conference_id
```

---

## ⛔ Conflict Detection

```sql
(? < end_time AND ? > start_time)
```

Ensures overlapping bookings are prevented.

---

## 📅 Rescheduling

* Uses `rescheduled_date`, `re_start_time`, `re_end_time`
* Overrides original booking values

---

# 🧪 Validations

* Booking time: **9 AM – 8 PM**
* End time must be after start time
* No overlapping bookings allowed
* Only admin can reassign

---

# 🐞 Known Issues (Fixed)

✔ Reassignment not freeing old hall
✔ Availability mismatch
✔ Modal cancel button not working
✔ Time parsing error (`%H:%M:%S`)
✔ Reassign reason not showing

---

# 📌 Future Enhancements

* Email notifications
* Role-based dashboards
* Calendar integration
* Mobile responsive UI
* Authentication improvements

---

# 👨‍💻 Author

**Aadi Sai Neekshay**
Computer Science Student & Developer

---

# 📜 License

This project is for academic and learning purposes.

---

# ⭐ Tip

For best understanding:

* Follow API flow (`booking_routes.py`)
* Check SQL queries carefully
* Observe frontend-backend interaction

---

# 🎯 Final Note

This system demonstrates:

* Full-stack development
* Real-time data handling
* Complex business logic (reassign, reschedule)
* Clean UI interaction

---

# Run in Personal address

* Open the Terminal 
* Navigate to Project Folder
* To Run Type:-> (python app.py)
* Press Ctrl+Click on ("http://127.0.0.1:5000")
* It will open the the Project in Browser.

---

# 👨‍💻 Author

* Aadi Sai Neekshay 
* IT Intern
* Computer Science Student & Developer
