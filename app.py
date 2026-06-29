from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import sqlite3

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

DB = "foodsaver.db"

# ==========================================
# LIVE EMAIL SETTING CONFIGURATION
# ==========================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'famibanu786@gmail.com'
app.config['MAIL_PASSWORD'] = 'lguxywmaptfnxkxq'
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
            
            # Registration Email
            try:
                msg = Message(
                    subject="✨ Welcome to Food Saver! Let's Make a Difference! 🌱",
                    recipients=[email]
                )
                msg.body = (
                    f"Hello {name}, 👋\n\n"
                    f"🌟 Welcome to FOOD SAVER! 🌟\n\n"
                    f"Thank you so much for joining our mission! 🥰 Your registration was successful. "
                    f"By joining our community, you are helping us fight food waste and bring "
                    f"smiles to countless faces. 📦✨\n\n"
                    f"Let's save extra food and support communities together! 🌱🤝\n\n"
                    f"Best regards,\n"
                    f"🚀 The Food Saver Team"
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
            session["user"] = user[2]
            return redirect(url_for("donate_food"))

        flash("Invalid email or password")

    return render_template("user_login.html")


# ================= USER DASHBOARD =================
@app.route("/user_dashboard")
def user_dashboard():
    if "user" not in session:
        return redirect(url_for("user_login"))

    return render_template("user_dashboard.html")


# ================= DONATE FOOD =================
@app.route("/donate_food", methods=["GET", "POST"])
def donate_food():
    if "user" not in session:
        return redirect(url_for("user_login"))

    if request.method == "POST":
        food_name = request.form.get("food_name")
        quantity = request.form.get("quantity")
        location = request.form.get("location")
        user_email = session["user"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO donations(
            user_email,
            food_name,
            quantity,
            location
        )
        VALUES (?,?,?,?)
        """, (user_email, food_name, quantity, location))

        conn.commit()
        conn.close()

        # --- UPDATED: DONATION RECEIPT EMAIL WITH TRACKING BUTTON ---
        try:
            track_url = url_for('track_donation', _external=True)
            msg = Message(
                subject="🍛 Your Food Donation Details Confirmation - Food Saver! 🎁",
                recipients=[user_email]
            )
            msg.html = f"""
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 15px;">
                <h2 style="color: #059669;">Thank you for your generous donation!</h2>
                <p>Hello Companion, 👋</p>
                <p>Your support is immensely valuable in feeding those in need. 🙏✨</p>
                
                <div style="background: #f8fafc; padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <p><strong>Donation Details:</strong><br>
                    🍲 Food Name : {food_name}<br>
                    📊 Quantity  : {quantity}<br>
                    📍 Location  : {location}</p>
                </div>
                
                <p>You can track the live status of your food donation by clicking the button below:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{track_url}" 
                       style="background-color: #39e75f; color: #030704; padding: 14px 28px; 
                              text-decoration: none; border-radius: 30px; font-weight: 700; 
                              font-size: 16px; display: inline-block; box-shadow: 0 4px 10px rgba(57, 231, 95, 0.3);">
                       Track Your Food
                    </a>
                </div>
                
                <p>Our team will handle the rest. Thank you for making a real difference today! 🌟🌎</p>
            </div>
            """
            mail.send(msg)
        except Exception as e:
            print(f"Donation Summary Email failed: {e}")

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

    data = cur.fetchall()
    conn.close()

    return render_template(
        "track_donation.html",
        donations=data
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

        flash("Invalid admin credentials")

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations")

    data = cur.fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        donations=data
    )


# ================= UPDATE STATUS =================
@app.route("/update_status/<int:id>/<status>")
def update_status(id, status):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    valid_status = ["Pending", "Picked", "On the Way", "Delivered"]

    if status not in valid_status:
        flash("Invalid Status")
        return redirect(url_for("admin_dashboard"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE donations SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ================= ASSIGN DELIVERY =================
@app.route("/assign_delivery/<int:id>", methods=["POST"])
def assign_delivery(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    delivery_boy = request.form.get("delivery_boy", "").strip()
    if delivery_boy == "":
        flash("Please enter delivery person name")
        return redirect(url_for("admin_dashboard"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE donations SET delivery_boy=? WHERE id=?", (delivery_boy, id))
    conn.commit()
    conn.close()

    flash("Delivery person assigned")
    return redirect(url_for("admin_dashboard"))


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)