from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
app.secret_key = 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


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

            # ================= SENDGRID EMAIL =================
            try:
                message = Mail(
                    from_email="YOUR_VERIFIED_EMAIL",
                    to_emails=email,
                    subject="🌟 Welcome to Food Saver!",
                    html_content=f"""
                    <h2>Hello {name}, 👋</h2>
                    <p>Welcome to <b>Food Saver</b>!</p>
                    <p>Your account has been created successfully.</p>
                    <p>Thank you for joining our mission 🌱</p>
                    <br>
                    <p>Food Saver Team 🚀</p>
                    """
                )

                sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
                response = sg.send(message)

                print("Email sent:", response.status_code)

            except Exception as e:
                print("Email failed:", e)

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

# ================= DONATE =================
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
