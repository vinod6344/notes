from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import pyodbc
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"  # ⚠️ Change in production

# ----------------- Config -----------------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ----------------- SQL Server Connection -----------------
DRIVERS = ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server", "SQL Server"]
for driver in DRIVERS:
    try:
        conn = pyodbc.connect(
            f'DRIVER={{{driver}}};'
            'SERVER=LAPTOP-P69MB6NO\\SQLEXPRESS;'
            'DATABASE=EduNotesDB;'
            'Trusted_Connection=yes;'
            'Encrypt=yes;'
            'TrustServerCertificate=yes;'
        )
        print(f"Connected using {driver}")
        break
    except Exception as e:
        print(f"Failed with {driver}: {e}")
else:
    raise Exception("No working driver found!")

cursor = conn.cursor()
# ----------------- Helpers -----------------
def load_admin():
    if not os.path.exists("config.json"):
        with open("config.json", "w") as f:
            json.dump({"username": "admin", "password": "12345"}, f, indent=4)
    with open("config.json", "r") as f:
        return json.load(f)

def load_settings():
    if not os.path.exists("settings.json"):
        with open("settings.json", "w") as f:
            json.dump({
                "site_name": "EduNotes",
                "contact_email": "info@edunotes.com",
                "contact_phone": "+1 (555) 123-4567",
                "contact_address": "123 Education Street, Academic City",
                "facebook": "",
                "twitter": "",
                "instagram": "",
                "linkedin": ""
            }, f, indent=4)
    with open("settings.json", "r") as f:
        return json.load(f)

def save_settings(data):
    with open("settings.json", "w") as f:
        json.dump(data, f, indent=4)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(func):
    def wrapper(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ----------------- Routes -----------------
@app.route("/")
def home():
    settings = load_settings()
    cursor.execute("SELECT Id, Title, Description, Branch, Year, FileName FROM Notes ORDER BY UploadedAt DESC")
    notes = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "branch": row[3],
            "year": row[4],
            "download": row[5],
            "pages": "-",
            "type": "PDF"
        }
        for row in cursor.fetchall()
    ]
    return render_template("index.html", settings=settings, notes=notes)

@app.route("/api/notes/<branch>/<year>")
def get_notes(branch, year):
    cursor.execute("""
        SELECT Title, Description, FileName 
        FROM Notes 
        WHERE Branch=? AND Year=?
        ORDER BY UploadedAt DESC
    """, branch, year)
    notes = [
        {"title": row[0], "description": row[1], "download": row[2], "pages": "-", "type": "PDF"}
        for row in cursor.fetchall()
    ]
    return jsonify(notes)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# -------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        admin = load_admin()
        if data.get("username") == admin["username"] and data.get("password") == admin["password"]:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# -------- ADMIN DASHBOARD ----------
@app.route("/admin")
@admin_required
def admin_dashboard():
    cursor.execute("SELECT Id, Title, Description, Branch, Year, FileName, UploadedAt FROM Notes ORDER BY UploadedAt DESC")
    notes = [
        {"id": row[0], "title": row[1], "description": row[2],
         "branch": row[3], "year": row[4], "file": row[5], "uploaded_at": row[6]}
        for row in cursor.fetchall()
    ]
    return render_template("admin.html", notes=notes)

# -------- ADD NOTE ----------

@app.route("/admin/add_note", methods=["GET", "POST"])
@admin_required

def add_note():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        branch = request.form.get("branch")
        year_str = request.form.get("year")  # e.g., '2nd Year'
        file = request.files.get("file")

        # Validate file
        if not file or not allowed_file(file.filename):
            return "Invalid file type! Only PDF allowed.", 400

        # Map year string to integer
        year_mapping = {"1st Year": 1, "2nd Year": 2, "3rd Year": 3, "4th Year": 4}
        year = year_mapping.get(year_str)
        if year is None:
            return "Invalid year selection!", 400

        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Insert into DB
        cursor.execute(
            "INSERT INTO Notes (Title, Description, Branch, Year, FileName) VALUES (?, ?, ?, ?, ?)",
            title, description, branch, year, filename
        )
        conn.commit()

        return redirect(url_for("admin_dashboard"))

    # GET request shows the upload form
    return render_template("add_note.html")

        # Validate file
    if not file or not allowed_file(file.filename):
        return "Invalid file type! Only PDF allowed.", 400

        # Convert year string to integer
        year_mapping = {
            "1st Year": 1,
            "2nd Year": 2,
            "3rd Year": 3,
            "4th Year": 4
        }
        year = year_mapping.get(year_str)
        if year is None:
            return "Invalid year selection!", 400

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Insert into SQL Server
        cursor.execute("""
            INSERT INTO Notes (Title, Description, Branch, Year, FileName)
            VALUES (?, ?, ?, ?, ?)
        """, title, description, branch, year, filename)
        conn.commit()

        return redirect(url_for("admin_dashboard"))

    return render_template("add_note.html")

# -------- SETTINGS ----------
@app.route("/settings")
@admin_required
def settings_page():
    settings = load_settings()
    return render_template("settings.html", settings=settings)

@app.route("/settings/update", methods=["POST"])
@admin_required
def update_settings():
    settings = load_settings()
    for key, value in request.form.items():
        settings[key] = value
    save_settings(settings)
    return jsonify({"message": "Settings updated successfully!"})
@app.route("/contact/submit", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not email or not message:
        return "All fields are required", 400

    cursor.execute("""
        INSERT INTO ContactMessages (Name, Email, Message)
        VALUES (?, ?, ?)
    """, name, email, message)
    conn.commit()

    return "Message sent successfully!"

@app.route("/admin/messages")
@admin_required
def view_messages():
    cursor.execute("SELECT Id, Name, Email, Message, SubmittedAt FROM ContactMessages ORDER BY SubmittedAt DESC")
    messages = [
        {"id": row[0], "name": row[1], "email": row[2], "message": row[3], "submitted_at": row[4]}
        for row in cursor.fetchall()
    ]
    return render_template("admin_messages.html", messages=messages)

@app.route("/admin/view_notes")
@admin_required
def view_notes():
    cursor.execute("SELECT Id, Title, Branch, Year, FileName, UploadedAt FROM Notes ORDER BY UploadedAt DESC")
    notes = [
        {"id": row[0], "title": row[1], "branch": row[2], "year": row[3], "file": row[4], "uploaded_at": row[5]}
        for row in cursor.fetchall()
    ]
    return render_template("delete_notes.html", notes=notes)

@app.route("/admin/delete_note/<int:note_id>")
@admin_required
def delete_note(note_id):
    cursor.execute("DELETE FROM Notes WHERE Id = ?", note_id)
    conn.commit()
    return redirect(url_for("view_notes"))  # redirect back to the list




# ----------------- Run App -----------------
if __name__ == "__main__":
    app.run(debug=True)
