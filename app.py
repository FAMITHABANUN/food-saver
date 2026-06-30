from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

DB = "foodsaver.db"

# ================= EMAIL CONFIG =================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'   # IMPORTANT: use Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        food_name TEXT,
        quantity TEXT,
        location TEXT,
        status TEXT DEFAULT 'Pending',
        delivery_boy TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home.html")

# ===@app.route("/user_register", methods=["GET", "POST"])
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

            # ================= EMAIL (FORCED + SAFE) =================
            try:
                msg = Message(
                    subject="🌟 Welcome to Food Saver!",
                    recipients=[email]
                )

                msg.body = f"""
Hello {name}, 👋

🌟 Welcome to FOOD SAVER! 🌟

Your account has been successfully created.

Thank you for joining our mission to reduce food waste.

Best regards,
Food Saver Team
"""

                mail.send(msg)

            except Exception as e:
                print("EMAIL ERROR:", e)

            flash("Registration Successful!")

            # 🔥 IMPORTANT FIX (force redirect after processing)
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
        food_name = request.form.get("food_name")
        quantity = request.form.get("quantity")
        location = request.form.get("location")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO donations(user_email, food_name, quantity, location)
            VALUES (?,?,?,?)
        """, (session["user"], food_name, quantity, location))

        conn.commit()
        conn.close()

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

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT food_name, quantity, location, status, delivery_boy
        FROM donations
        WHERE user_email=?
    """, (session["user"],))

    data = cur.fetchall()
    conn.close()

    return render_template("track_donation.html", donations=data)

# ================= ADMIN =================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin login")

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", donations=data)

@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    status = request.form.get("status")
    delivery_boy = request.form.get("delivery_boy")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        UPDATE donations
        SET status=?, delivery_boy=?
        WHERE id=?
    """, (status, delivery_boy, id))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)
