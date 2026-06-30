from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import sqlite3

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

DB = "foodsaver.db"

# ==========================================
# EMAIL CONFIGURATION
# ==========================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'famibanu786@gmail.com'
app.config['MAIL_PASSWORD'] = 'fewkzkdmrgsxasgt'
app.config['MAIL_DEFAULT_SENDER'] = 'famibanu786@gmail.com'

mail = Mail(app)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # DONATIONS TABLE
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

# ================= USER REGISTER =================
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

            try:
                msg = Message(
                    subject="✨ Welcome to Food Saver! Let's Make a Difference! 🌱",
                    recipients=[email]
                )
                msg.body = (
                    f"Hello {name}, 👋\n\n"
                    f"🌟 Welcome to FOOD SAVER! 🌟\n\n"
                    f"Thank you for joining Food Saver.\n\n"
                    f"Your registration was successful.\n\n"
                    f"Best regards,\n"
                    f"Food Saver Team"
                )
                mail.send(msg)
            except Exception as e:
                print(f"Registration Email failed: {e}")

            flash("Registration Successful!")
            return redirect(url_for("user_login"))

        except sqlite3.IntegrityError:
            flash("Email already exists")

        finally:
            conn.close()

    return render_template("user_register.html")

# ================= USER LOGIN =================
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
            flash("Login Successful!")
            return redirect(url_for("donate_food"))
        else:
            flash("Invalid Email or Password")

    return render_template("user_login.html")


# ================= USER DASHBOARD ===============
@app.route("/user_dashboard")
def user_dashboard():
    if "user" not in session:
        return redirect(url_for("user_login"))

    user_email = session["user"]

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT food_name, quantity, location, status, delivery_boy
        FROM donations
        WHERE user_email=?
        ORDER BY id DESC
    """, (user_email,))

    donations = cur.fetchall()
    conn.close()

    return render_template(
        "user_dashboard.html",
        donations=donations,
        user_email=user_email
    )
@app.route("/donate_food", methods=["GET", "POST"])
def donate_food():
    if "user" not in session:
        return redirect(url_for("user_login"))

    if request.method == "POST":
        food_name = request.form.get("food_name")
        quantity = request.form.get("quantity")
        location = request.form.get("location")
        user_email = session["user"]

        # ================= SAVE TO DATABASE =================
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO donations (
                user_email,
                food_name,
                quantity,
                location
            )
            VALUES (?,?,?,?)
        """, (user_email, food_name, quantity, location))

        conn.commit()
        conn.close()

        # ================= EMAIL (NON-BLOCKING STYLE) =================
        try:
            msg = Message(
                subject="❤️ Food Donation Confirmation | FoodSaver",
                recipients=[user_email]
            )

            msg.body = f"""
Hello Companion 👋

❤️ Thank you for your food donation!

🍲 Food Name : {food_name}
📊 Quantity  : {quantity}
📍 Location  : {location}

🙏 Your contribution helps someone in need.
With gratitude,
FoodSaver Team
"""

            mail.send(msg)

        except Exception as e:
            print("Email failed:", e)

        # ================= INSTANT REDIRECT =================
        return redirect(url_for("success"))

    return render_template("donate_food.html")
    
    # ================= SUCCESS =================
@app.route("/success")
def success():
    return render_template("success.html")


# ================= TRACK DONATION =================
@app.route("/track_donation")
def track_donation():
    if "user" not in session:
        return redirect(url_for("user_login"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM donations WHERE user_email=?",
        (session["user"],)
    )

    donations = cur.fetchall()

    conn.close()

    return render_template(
        "track_donation.html",
        donations=donations
    )


# ================= ADMIN LOGIN =================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin123":
         session["admin"] = True 
         return redirect(url_for("admin_dashboard"))

        flash("Invalid Admin Credentials")

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations ORDER BY id DESC")
    donations = cur.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        donations=donations
    )


# ================= UPDATE DONATION STATUS =================
@app.route("/update_status/<int:donation_id>", methods=["POST"])
def update_status(donation_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    status = request.form.get("status")
    delivery_boy = request.form.get("delivery_boy")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        UPDATE donations
        SET status = ?, delivery_boy = ?
        WHERE id = ?
    """, (status, delivery_boy, donation_id))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ================= USER LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


# ================= ADMIN LOGOUT =================
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


# ================= RUN APPLICATION =================
import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )