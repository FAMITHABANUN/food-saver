from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from email_utils import send_registration_email, send_donation_email

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

# ================= SAFE DB PATH (RENDER FIX) =================
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

# ================= REGISTER (NO EMAIL) =================
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

            # Send welcome email (errors are handled internally and never
            # block registration - see email_utils.py)
            send_registration_email(email, name)

            flash("Registration successful!")
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
            flash("Invalid login credentials")

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

        # Send donation confirmation email (errors are handled internally
        # and never block the donation flow - see email_utils.py)
        try:
            user_email = session["user"]
            lookup_conn = sqlite3.connect(DB)
            lookup_cur = lookup_conn.cursor()
            lookup_cur.execute("SELECT name FROM users WHERE email=?", (user_email,))
            row = lookup_cur.fetchone()
            lookup_conn.close()
            user_name = row[0] if row else user_email
            send_donation_email(user_email, user_name)
        except Exception:
            pass

        return redirect(url_for("success"))

    return render_template("donate_food.html")

# ================= TEMP: ONE-TIME RESET (REMOVE AFTER USE) =================
# Visit /reset_users_TEMP?key=foodsaver_reset_2026 once in your browser to
# clear all registered users. DELETE THIS ROUTE after use for security.
@app.route("/reset_users_TEMP")
def reset_users_temp():
    if request.args.get("key") != "foodsaver_reset_2026":
        return "Unauthorized", 403

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()

    return "All users deleted successfully. Remember to remove this route now."

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
        flash("Invalid admin credentials")

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

# ================= UPDATE STATUS =================
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
    app.run(host="0.0.0.0", port=10000, debug=False)

