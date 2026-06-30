from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

DB = "foodsaver.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= SAFE EMAIL (NEVER CRASHES APP) =================
def send_email(name, email):
    try:
        sender_email = "famibanu321@gmail.com"
        sender_password = "yfaj dhgk mxlk lpqx"

        msg = MIMEText(f"""
Hello {name}, 👋

Welcome to FOOD SAVER 🌱

Your account is successfully created.

Thank you for joining us!

- Food Saver Team
""")

        msg["Subject"] = "Welcome to Food Saver"
        msg["From"] = sender_email
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()

        print("EMAIL SENT")

    except Exception as e:
        print("EMAIL FAILED (ignored):", e)

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home.html")

# ================= REGISTER =================
@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(name,email,password) VALUES (?,?,?)",
                (name, email, password)
            )
            conn.commit()

            send_email(name, email)

            flash("Registration Successful!")
            return redirect(url_for("user_login"))

        except sqlite3.IntegrityError:
            flash("Email already exists")

        finally:
            conn.close()

    return render_template("user_register.html")

# ================= LOGIN =================
@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect(url_for("donate_food"))
        else:
            flash("Invalid login")

    return render_template("user_login.html")

# ================= DONATE FOOD =================
@app.route("/donate_food", methods=["GET", "POST"])
def donate_food():
    if "user" not in session:
        return redirect(url_for("user_login"))

    if request.method == "POST":
        return redirect(url_for("success"))

    return render_template("donate_food.html")

# ================= SUCCESS =================
@app.route("/success")
def success():
    return render_template("success.html")

# ================= TRACK =================
@app.route("/track_donation")
def track_donation():
    if "user" not in session:
        return redirect(url_for("user_login"))

    return render_template("track_donation.html")

# ================= ADMIN LOGIN =================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials")

    return render_template("admin_login.html")

# ================= ADMIN DASHBOARD =================
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    return render_template("admin_dashboard.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
