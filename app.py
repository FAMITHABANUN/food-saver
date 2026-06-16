from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "foodsaver_final_secure_key"

DB = "foodsaver.db"


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
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(name,email,password) VALUES (?,?,?)",
                (
                    request.form["name"],
                    request.form["email"],
                    request.form["password"]
                )
            )

            conn.commit()
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
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (
                request.form["email"],
                request.form["password"]
            )
        )

        user = cur.fetchone()

        conn.close()

        if user:
            session["user"] = user[2]

            # Direct to donate page
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
        """, (
            session["user"],
            request.form["food_name"],
            request.form["quantity"],
            request.form["location"]
        ))

        conn.commit()
        conn.close()

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

    valid_status = [
        "Pending",
        "Picked",
        "On the Way",
        "Delivered"
    ]

    if status not in valid_status:
        flash("Invalid Status")
        return redirect(url_for("admin_dashboard"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "UPDATE donations SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ================= ASSIGN DELIVERY =================
@app.route("/assign_delivery/<int:id>", methods=["POST"])
def assign_delivery(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    delivery_boy = request.form.get(
        "delivery_boy",
        ""
    ).strip()

    if delivery_boy == "":
        flash("Please enter delivery person name")
        return redirect(url_for("admin_dashboard"))

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "UPDATE donations SET delivery_boy=? WHERE id=?",
        (delivery_boy, id)
    )

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